from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('candidate/', include('candidates.urls')),
    path('company/', include('company.urls')),
]
