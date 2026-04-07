from django.contrib import admin
from .models import CompanyProfile, Job


@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'cnpj', 'user', 'city', 'phone')
    search_fields = ('company_name', 'cnpj', 'user__email')


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'location', 'job_type', 'status', 'created_at')
    list_filter = ('status', 'job_type')
    search_fields = ('title', 'company__company_name', 'location')
