from django.contrib import admin
from .models import Categoria, Transaccion, Regla

admin.site.register(Categoria)
admin.site.register(Transaccion)
admin.site.register(Regla)