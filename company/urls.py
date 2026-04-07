from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home_company, name='home_company'),
    path('jobs/', views.job_list, name='job_list_company'),
    path('jobs/new/', views.job_create, name='job_create'),
    path('jobs/<int:job_id>/', views.job_detail_company, name='job_detail_company'),
    path('jobs/<int:job_id>/status/', views.job_update_status, name='job_update_status'),
    path('jobs/<int:job_id>/delete/', views.job_delete, name='job_delete'),
    path('jobs/<int:job_id>/applicants/<int:application_id>/', views.applicant_detail, name='applicant_detail'),
    path('candidates/', views.candidate_list, name='candidate_list'),
    path('recommendations/', views.recommendations, name='recommendations'),
]
