from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/candidate/', views.register_candidate, name='register_candidate'),
    path('verify/candidate/', views.verify_email, name='verify_email_candidate'),
    path('register/candidate/details/', views.register_details, name='register_details_candidate'),
    path('register/company/', views.register_company, name='register_company'),
    path('register/company/details/', views.register_details_company, name='register_details_company'),
    path('verify/company/', views.verify_email_company, name='verify_email_company'),
]