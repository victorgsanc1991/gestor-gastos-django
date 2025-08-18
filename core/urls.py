from django.urls import path
from . import views

urlpatterns = [
    # Nuevas URLs para el login
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # La página raíz ahora es el dashboard
    path('', views.dashboard, name='dashboard'),
    
    path('subir/', views.subir_movimientos, name='subir'),
    path('transacciones/', views.listar_transacciones, name='listar'),
    path('actualizar-categoria/', views.actualizar_categoria, name='actualizar_categoria'),
    path('transaccion/<int:transaccion_id>/eliminar/', views.eliminar_transaccion, name='eliminar_transaccion'),
    path('transacciones/eliminar-multiples/', views.eliminar_multiples, name='eliminar_multiples'),
]