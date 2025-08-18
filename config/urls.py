from django.urls import path, include

urlpatterns = [
    # Apuntamos todas las peticiones a nuestra app 'core'
    path('', include('core.urls')),
]
