from django.contrib import admin
from .models import CompanyProfile


@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'cnpj', 'user', 'city', 'phone')
    search_fields = ('company_name', 'cnpj', 'user__email')
