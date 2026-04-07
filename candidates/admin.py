from django.contrib import admin
from .models import CandidateProfile, JobApplication


@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'cpf', 'city', 'phone')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'cpf')


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'job', 'status', 'applied_at', 'experience_rating')
    list_filter = ('status',)
    search_fields = ('candidate__user__email', 'job__title')
