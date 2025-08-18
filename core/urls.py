from django.urls import path
from . import views

urlpatterns = [
    path('', views.subir_movimientos, name='subir'),
    path('transacciones/', views.listar_transacciones, name='listar'),
    path('actualizar-categoria/', views.actualizar_categoria, name='actualizar_categoria'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # --- AÑADE ESTAS DOS LÍNEAS ---
    # URL para borrar una sola transacción. Capturamos el ID desde la URL.
    path('transaccion/<int:transaccion_id>/eliminar/', views.eliminar_transaccion, name='eliminar_transaccion'),
    # URL para procesar la eliminación múltiple.
    path('transacciones/eliminar-multiples/', views.eliminar_multiples, name='eliminar_multiples'),
]