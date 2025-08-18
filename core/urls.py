from django.urls import path
from . import views

urlpatterns = [
    # URLs para el sistema de login simple
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # URLs de la aplicación
    path('', views.dashboard, name='dashboard'),
    path('subir/', views.subir_movimientos, name='subir'),
    path('transacciones/', views.listar_transacciones, name='listar'),
    path('actualizar-categoria/', views.actualizar_categoria, name='actualizar_categoria'),
    path('transaccion/<int:transaccion_id>/eliminar/', views.eliminar_transaccion, name='eliminar_transaccion'),
    path('transacciones/eliminar-multiples/', views.eliminar_multiples, name='eliminar_multiples'),
]