from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home_company, name='home_company'),
]