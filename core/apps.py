from django.apps import AppConfig
import os

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        # Esta función se ejecuta cada vez que la aplicación arranca.
        # Solo intentará crear el superusuario si las variables de entorno existen.
        from django.contrib.auth.models import User
        
        username = os.environ.get('ADMIN_USER')
        password = os.environ.get('ADMIN_PASSWORD')
        email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')

        if username and password and not User.objects.filter(username=username).exists():
            print(f"Creando superusuario: {username}")
            User.objects.create_superuser(username=username, email=email, password=password)
            print("Superusuario creado con éxito.")