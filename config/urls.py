from django.contrib import admin
from django.urls import path, include  # <-- AÑADE 'include' AQUÍ

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),  # <-- AÑADE ESTA LÍNEA ENTERA
]
