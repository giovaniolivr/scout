from django.urls import path
from . import views

urlpatterns = [
    path('onboarding/', views.onboarding_candidate, name='onboarding_candidate'),
    path('home/', views.home_candidate, name='home_candidate'),
    path('profile/', views.profile_candidate, name='profile_candidate'),
    path('profile/edit/', views.edit_profile_candidate, name='edit_profile_candidate'),
    path('jobs/', views.search_jobs, name='search_jobs'),
    path('jobs/<int:job_id>/', views.job_detail, name='job_detail'),
    path('jobs/<int:job_id>/apply/', views.apply_job, name='apply_job'),
    path('jobs/<int:job_id>/apply-external/', views.apply_external, name='apply_external'),
    path('applications/', views.all_applications, name='all_applications'),
    path('applications/<int:application_id>/', views.application_detail, name='application_detail'),
]
