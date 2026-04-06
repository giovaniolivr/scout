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
