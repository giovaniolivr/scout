import uuid
from django.db import models
from django.utils import timezone


class EmailVerificationToken(models.Model):
    USER_TYPE_CANDIDATE = 'candidate'
    USER_TYPE_COMPANY = 'company'
    USER_TYPE_CHOICES = [
        (USER_TYPE_CANDIDATE, 'Candidato'),
        (USER_TYPE_COMPANY, 'Empresa'),
    ]

    email = models.EmailField()
    token = models.CharField(max_length=64)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def is_expired(self):
        return (timezone.now() - self.created_at).total_seconds() > 600  # 10 minutes

    def __str__(self):
        return f"{self.user_type} | {self.email} | used={self.is_used}"

    @classmethod
    def generate_candidate_code(cls, email):
        """Creates a 4-digit numeric code for candidate email verification."""
        import random
        cls.objects.filter(email=email, user_type=cls.USER_TYPE_CANDIDATE, is_used=False).delete()
        code = str(random.randint(1000, 9999))
        return cls.objects.create(email=email, token=code, user_type=cls.USER_TYPE_CANDIDATE)

    @classmethod
    def generate_company_token(cls, email):
        """Creates a UUID token for company email verification link."""
        cls.objects.filter(email=email, user_type=cls.USER_TYPE_COMPANY, is_used=False).delete()
        token = uuid.uuid4().hex
        return cls.objects.create(email=email, token=token, user_type=cls.USER_TYPE_COMPANY)
