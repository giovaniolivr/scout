from django.shortcuts import render

def home_company(request):
    return render(request, 'home_company.html', {'user_is_company': True,})
