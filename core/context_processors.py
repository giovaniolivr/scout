def user_type(request):
    """Injects user type flags into every template context."""
    user_is_candidate = False
    user_is_company = False

    if request.user.is_authenticated:
        user_is_candidate = hasattr(request.user, 'candidate_profile')
        user_is_company = hasattr(request.user, 'company_profile')

    return {
        'user_is_candidate': user_is_candidate,
        'user_is_company': user_is_company,
    }
