from django.db import models
from django.contrib.auth.models import User


class CandidateProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='candidate_profile')
    cpf = models.CharField(max_length=11, unique=True)
    phone = models.CharField(max_length=20)
    cep = models.CharField(max_length=8)
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    street = models.CharField(max_length=200)

    # Skills — stored as comma-separated strings; populated via the profile edit page.
    hard_skills = models.TextField(blank=True, default='')
    soft_skills = models.TextField(blank=True, default='')

    def get_hard_skills_list(self):
        return [s.strip() for s in self.hard_skills.split(',') if s.strip()]

    def get_soft_skills_list(self):
        return [s.strip() for s in self.soft_skills.split(',') if s.strip()]

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

    class Meta:
        unique_together = ('candidate', 'job')

    def __str__(self):
        return f"{self.candidate} → {self.job.title}"
