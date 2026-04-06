from django.contrib import admin
from .models import CandidateProfile


@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'cpf', 'city', 'phone')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'cpf')
