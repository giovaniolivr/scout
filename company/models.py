from django.db import models
from django.contrib.auth.models import User


class CompanyProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company_profile')
    company_name = models.CharField(max_length=200)
    cnpj = models.CharField(max_length=14, unique=True)
    responsible_name = models.CharField(max_length=200)
    cpf_responsible = models.CharField(max_length=11)
    phone = models.CharField(max_length=20)
    cep = models.CharField(max_length=8)
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    street = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.company_name} ({self.user.email})"


class Job(models.Model):
    STATUS_OPEN = 'open'
    STATUS_PAUSED = 'paused'
    STATUS_CLOSED = 'closed'
    STATUS_CHOICES = [
        (STATUS_OPEN, 'Aberta'),
        (STATUS_PAUSED, 'Pausada'),
        (STATUS_CLOSED, 'Fechada'),
    ]

    TYPE_FULL_TIME = 'full_time'
    TYPE_PART_TIME = 'part_time'
    TYPE_INTERNSHIP = 'internship'
    TYPE_CHOICES = [
        (TYPE_FULL_TIME, 'Tempo integral'),
        (TYPE_PART_TIME, 'Meio período'),
        (TYPE_INTERNSHIP, 'Estágio'),
    ]

    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=100)
    job_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_FULL_TIME)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_OPEN)
    external_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Skill requirements — comma-separated; matched against CandidateProfile skills.
    required_hard_skills = models.TextField(blank=True, default='')
    required_soft_skills = models.TextField(blank=True, default='')

    def get_required_hard_skills_list(self):
        return [s.strip() for s in self.required_hard_skills.split(',') if s.strip()]

    def get_required_soft_skills_list(self):
        return [s.strip() for s in self.required_soft_skills.split(',') if s.strip()]

    def has_requirements(self):
        return bool(self.required_hard_skills.strip() or self.required_soft_skills.strip())

    def match_score(self, candidate_profile):
        """
        Returns an integer 0–100 representing how well a candidate matches
        this job's skill requirements, or None if no requirements are set.

        MATCHING HOOK — this logic will be refined once the Scout Score
        system and candidate skill profiles are fully populated.
        """
        required = (
            self.get_required_hard_skills_list() +
            self.get_required_soft_skills_list()
        )
        if not required:
            return None  # No requirements = open to all; don't penalise

        candidate_skills = (
            candidate_profile.get_hard_skills_list() +
            candidate_profile.get_soft_skills_list()
        )
        if not candidate_skills:
            return 0

        candidate_lower = {s.lower() for s in candidate_skills}
        matched = sum(1 for s in required if s.lower() in candidate_lower)
        return int((matched / len(required)) * 100)

    def __str__(self):
        return f"{self.title} — {self.company.company_name}"
