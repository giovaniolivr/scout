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

    # Onboarding gate — set to True after the candidate completes the first-time profile setup
    is_onboarded = models.BooleanField(default=False)

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

    # Experience rating — filled by candidate after job closes
    experience_rating = models.IntegerField(null=True, blank=True)  # 1 to 5
    experience_comment = models.TextField(blank=True)

    # Archived applications are hidden from the candidate's views but kept for scoring
    is_archived = models.BooleanField(default=False)

    class Meta:
        unique_together = ('candidate', 'job')

    def __str__(self):
        return f"{self.candidate} → {self.job.title}"
