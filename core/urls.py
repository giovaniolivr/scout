from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/candidate/', views.register_candidate, name='register_candidate'),
    path('verify/', views.verify_email, name='verify_email'),
    path('register/details/', views.register_details, name='register_details'),
]