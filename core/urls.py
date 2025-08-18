from django.urls import path
from . import views

urlpatterns = [
    # La página raíz ahora apunta al dashboard, que actuará como página de inicio
    path('', views.dashboard, name='dashboard'),
    
    # Las otras páginas tienen sus propias URLs
    path('subir/', views.subir_movimientos, name='subir'),
    path('transacciones/', views.listar_transacciones, name='listar'),
    path('actualizar-categoria/', views.actualizar_categoria, name='actualizar_categoria'),
    path('transaccion/<int:transaccion_id>/eliminar/', views.eliminar_transaccion, name='eliminar_transaccion'),
    path('transacciones/eliminar-multiples/', views.eliminar_multiples, name='eliminar_multiples'),
]