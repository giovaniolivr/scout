from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


@login_required
def home_company(request):
    if not hasattr(request.user, 'company_profile'):
        return redirect('home')
    return render(request, 'home_company.html')
