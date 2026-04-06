from django.contrib import admin
from .models import EmailVerificationToken


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ('email', 'user_type', 'is_used', 'created_at')
    list_filter = ('user_type', 'is_used')
    search_fields = ('email',)
    readonly_fields = ('created_at',)
