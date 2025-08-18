"""
Django settings for config project.
"""
from pathlib import Path
import os  # Importamos 'os' para leer variables de entorno
import dj_database_url  # Importamos la librería para la URL de la base de datos

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ==============================================================================
# CONFIGURACIÓN DE SEGURIDAD Y ENTORNO
# ==============================================================================

# La SECRET_KEY no debe estar visible en el código. La leeremos de una variable
# de entorno. Si no la encuentra, usará una clave simple (solo para desarrollo).
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-una-clave-insegura-para-desarrollo')

# El modo DEBUG será 'False' en producción. Render pondrá la variable RENDER
# a 'true', así que lo usamos para detectar si estamos en producción.
# El 'False' como string es importante.
DEBUG = os.environ.get('RENDER', 'False') != 'True'

# En producción, añadiremos la URL de nuestra app en Render.
ALLOWED_HOSTS = []
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Django necesita saber que el origen de las peticiones desde nuestra URL de Render es seguro.
CSRF_TRUSTED_ORIGINS = []
if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(f"https://{RENDER_EXTERNAL_HOSTNAME}")


# ==============================================================================
# APLICACIONES Y MIDDLEWARE
# ==============================================================================

INSTALLED_APPS = [
    'core',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Middleware de WhiteNoise
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# ==============================================================================
# BASE DE DATOS
# ==============================================================================

# En producción, usaremos la base de datos PostgreSQL de Render. En local,
# seguiremos usando SQLite para que sea fácil trabajar.
DATABASES = {
    'default': dj_database_url.config(
        # La URL de la BD la leerá de la variable de entorno DATABASE_URL
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600 # Mantiene las conexiones vivas por más tiempo
    )
}


# ==============================================================================
# VALIDACIÓN DE CONTRASEÑAS
# ==============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ==============================================================================
# INTERNACIONALIZACIÓN
# ==============================================================================

LANGUAGE_CODE = 'es-es' # Cambiado a español
TIME_ZONE = 'Europe/Madrid' # Cambiado a zona horaria de España
USE_I18N = True
USE_TZ = True


# ==============================================================================
# ARCHIVOS ESTÁTICOS (CSS, JAVASCRIPT, IMÁGENES)
# ==============================================================================

STATIC_URL = 'static/'

# Esto solo se usa en desarrollo. En producción, WhiteNoise se encarga de todo.
# STATICFILES_DIRS = [BASE_DIR / "static"]

# El directorio donde `collectstatic` reunirá todos los archivos estáticos.
STATIC_ROOT = BASE_DIR / 'staticfiles'

# El motor de almacenamiento de WhiteNoise.
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}


# ==============================================================================
# OTROS AJUSTES
# ==============================================================================

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'