from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Candidate registration
    path('register/candidate/', views.register_candidate, name='register_candidate'),
    path('verify/candidate/', views.verify_email_candidate, name='verify_email_candidate'),
    path('verify/candidate/resend/', views.resend_candidate_code, name='resend_candidate_code'),
    path('register/candidate/details/', views.register_details_candidate, name='register_details_candidate'),

    # Company registration
    path('register/company/', views.register_company, name='register_company'),
    path('register/company/details/', views.register_details_company, name='register_details_company'),
    path('verify/company/', views.verify_email_company, name='verify_email_company'),

    # Auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
