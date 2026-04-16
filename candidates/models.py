from django.db import models
from django.contrib.auth.models import User
from core.roles import JOB_AREAS, SENIORITY_LEVELS


class CandidateProfile(models.Model):
    EDUCATION_CHOICES = [
        ('medio', 'Ensino Médio'),
        ('superior_incompleto', 'Superior Incompleto'),
        ('superior_completo', 'Superior Completo'),
        ('pos_graduacao', 'Pós-graduação'),
        ('mestrado', 'Mestrado'),
        ('doutorado', 'Doutorado'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='candidate_profile')
    cpf = models.CharField(max_length=11, unique=True)
    phone = models.CharField(max_length=20)
    cep = models.CharField(max_length=8)
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    street = models.CharField(max_length=200)

    # Profile info — collected during onboarding and editable afterwards
    bio = models.TextField(blank=True, default='', max_length=500)
    desired_role = models.CharField(max_length=100, blank=True, default='')  # free-text display title (legacy)
    desired_area = models.CharField(max_length=20, choices=JOB_AREAS, blank=True, default='')
    desired_seniority = models.CharField(max_length=20, choices=SENIORITY_LEVELS, blank=True, default='')
    education_level = models.CharField(max_length=25, choices=EDUCATION_CHOICES, blank=True, default='')
    profile_cv = models.FileField(upload_to='profile_cvs/', blank=True, null=True)
    linkedin_url = models.URLField(blank=True, default='')
    github_url = models.URLField(blank=True, default='')
    portfolio_url = models.URLField(blank=True, default='')
    languages = models.TextField(blank=True, default='')  # comma-separated, e.g. "Português, Inglês"

    # Onboarding gate — set to True after the candidate completes the first-time profile setup
    is_onboarded = models.BooleanField(default=False)

    # Calculated and stored on every new company rating — see recalculate_scout_score()
    scout_score = models.IntegerField(null=True, blank=True)

    # Internal cumulative score — never shown to users; used for platform ranking
    internal_score = models.IntegerField(default=0)

    # Skills — stored as comma-separated strings; populated via onboarding and profile edit.
    hard_skills = models.TextField(blank=True, default='')
    soft_skills = models.TextField(blank=True, default='')

    # Visibility — skills the candidate chose to hide from their profile display.
    # The data (and any company ratings) persists; only the display is toggled.
    hidden_hard_skills = models.TextField(blank=True, default='')
    hidden_soft_skills = models.TextField(blank=True, default='')

    # -----------------------------------------------------------------------
    # Skill helpers
    # -----------------------------------------------------------------------

    def get_languages_list(self):
        return [l.strip() for l in self.languages.split(',') if l.strip()]

    def recalculate_scout_score(self):
        """
        Scout Score v1 — stored on the profile, recalculated on every new company rating.

        Components:
          - Base (0–80): average of all received company_rating values, scaled from 1–5 → 0–80
          - Completeness bonus (0–20): proportion of optional profile fields filled

        Returns None when no ratings exist yet (score stays hidden until first rating).
        This method saves the result directly and can be replaced with a richer algorithm later.
        """
        from django.db.models import Avg
        rated_qs = self.applications.filter(company_rating__isnull=False)
        if not rated_qs.exists():
            self.scout_score = None
            self.save(update_fields=['scout_score'])
            return

        avg = rated_qs.aggregate(avg=Avg('company_rating'))['avg']
        base = int((avg / 5) * 80)

        filled = sum([
            bool(self.bio),
            bool(self.profile_cv),
            bool(self.linkedin_url),
            bool(self.hard_skills),
            bool(self.soft_skills),
            bool(self.languages),
            bool(self.portfolio_url or self.github_url),
        ])
        bonus = int((filled / 7) * 20)

        self.scout_score = min(100, base + bonus)
        self.save(update_fields=['scout_score'])

    def recalculate_internal_score(self):
        """
        Internal Score — cumulative, never shown to users.
        Grows over time by rewarding sustained engagement and quality signals.

        Components:
          - 10 pts per application submitted
          - 20 pts per completed rating cycle (company submitted a rating)
          -  5 pts per skill endorsement received
          -  3 pts per optional profile field filled (max 7 fields × 3 = 21)
        """
        apps = self.applications.all()
        total_apps = apps.count()
        rated_apps = apps.filter(company_rated_at__isnull=False).count()
        endorsements = self.endorsements.count()

        filled = sum([
            bool(self.bio),
            bool(self.profile_cv),
            bool(self.linkedin_url),
            bool(self.hard_skills),
            bool(self.soft_skills),
            bool(self.languages),
            bool(self.portfolio_url or self.github_url),
        ])

        self.internal_score = (total_apps * 10) + (rated_apps * 20) + (endorsements * 5) + (filled * 3)
        self.save(update_fields=['internal_score'])

    def get_hard_skills_list(self):
        return [s.strip() for s in self.hard_skills.split(',') if s.strip()]

    def get_soft_skills_list(self):
        return [s.strip() for s in self.soft_skills.split(',') if s.strip()]

    def get_hidden_hard_skills_set(self):
        # Canonical casing is guaranteed by filter_hard_skills() at save time,
        # so plain string equality is reliable here.
        return {s.strip() for s in self.hidden_hard_skills.split(',') if s.strip()}

    def get_hidden_soft_skills_set(self):
        return {s.strip() for s in self.hidden_soft_skills.split(',') if s.strip()}

    def get_visible_hard_skills_list(self):
        hidden = self.get_hidden_hard_skills_set()
        return [s for s in self.get_hard_skills_list() if s not in hidden]

    def get_visible_soft_skills_list(self):
        hidden = self.get_hidden_soft_skills_set()
        return [s for s in self.get_soft_skills_list() if s not in hidden]

    def has_skills(self):
        return bool(self.hard_skills.strip() or self.soft_skills.strip())

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.user.email})"


class JobApplication(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_VIEWED = 'viewed'
    STATUS_ACCEPTED = 'accepted'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Aguardando'),
        (STATUS_VIEWED, 'Visualizado'),
        (STATUS_ACCEPTED, 'Aprovado'),
        (STATUS_REJECTED, 'Reprovado'),
    ]

    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='applications')
    job = models.ForeignKey('company.Job', on_delete=models.CASCADE, related_name='applications')
    applied_at = models.DateTimeField(auto_now_add=True)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    cv = models.FileField(upload_to='cvs/', blank=True)

    # Candidate rates the experience — filled after application reaches a final status
    experience_rating = models.IntegerField(null=True, blank=True)  # 1 to 5
    experience_comment = models.TextField(blank=True)

    # Company rates the candidate — filled after accepting/rejecting
    company_rating = models.IntegerField(null=True, blank=True)      # 1 to 5, optional
    company_comment = models.TextField(blank=True, default='')
    company_rated_at = models.DateTimeField(null=True, blank=True)   # set on submit; determines "rated" state

    # Archived applications are hidden from the candidate's views but kept for scoring
    is_archived = models.BooleanField(default=False)

    class Meta:
        unique_together = ('candidate', 'job')

    def __str__(self):
        return f"{self.candidate} → {self.job.title}"
