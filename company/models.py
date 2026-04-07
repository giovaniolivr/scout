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

    def __str__(self):
        return f"{self.title} — {self.company.company_name}"
