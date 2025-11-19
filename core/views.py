from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

def register_candidate(request):
    return render(request, 'register_candidate.html', {'hide_nav_links': True})

def verify_email(request):
    email = request.GET.get('email', '')
    return render(request, 'verify_email_candidate.html', {'email': email,'hide_nav_links': True})

def register_details(request):
    return render(request, 'register_details_candidate.html', {'hide_nav_links': True})

def register_company(request):
    return render(request, 'register_company.html', {'hide_nav_links': True})

def register_details_company(request):
    email = request.GET.get('email', '')
    return render(request, 'register_details_company.html', {'email': email, 'hide_nav_links': True})

def verify_email_company(request):
    email = request.GET.get('email', '')
    return render(request, 'verify_email_company.html', {'email': email, 'hide_nav_links': True})