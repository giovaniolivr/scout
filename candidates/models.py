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

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.user.email})"
