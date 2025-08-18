from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Transaccion, Categoria, Regla
import csv
import io
from datetime import datetime
from django.db.models import Sum, Q
from django.utils import timezone
import json
from django.db.models.functions import TruncMonth
from functools import wraps

# ==============================================================================
# DECORADOR DE LOGIN PERSONALIZADO (NUESTRO "PORTERO")
# ==============================================================================
def login_requerido(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('autenticado'):
            return redirect('login') # Si no hay sesión, redirige a nuestra página de login
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# ==============================================================================
# VISTAS DE LOGIN Y LOGOUT
# ==============================================================================
def login_view(request):
    if request.session.get('autenticado'):
        return redirect('dashboard') # Si ya está logueado, va al dashboard

    if request.method == 'POST':
        password = request.POST.get('password')
        # La contraseña "maestra" la definimos aquí. ¡Cámbiala si quieres!
        if password == 'RoseMcgowan1991':
            request.session['autenticado'] = True
            return redirect('dashboard')
        else:
            messages.error(request, 'Contraseña incorrecta.')
    return render(request, 'core/login.html')

def logout_view(request):
    try:
        del request.session['autenticado']
    except KeyError:
        pass
    return redirect('login')

# ==============================================================================
# VISTAS DE LA APLICACIÓN (AHORA PROTEGIDAS CON NUESTRO DECORADOR)
# ==============================================================================
@login_requerido
def subir_movimientos(request):
    # ... (el contenido de la función es el mismo)
    if request.method == 'POST':
        if 'csv_file' not in request.FILES: messages.error(request, "No se seleccionó ningún archivo."); return redirect('subir')
        csv_file = request.FILES['csv_file']
        if not csv_file.name.endswith('.csv'): messages.error(request, "El archivo debe tener formato .csv"); return redirect('subir')
        try:
            data_set = csv_file.read().decode('utf-8'); io_string = io.StringIO(data_set)
            for _ in range(5): next(io_string)
            reader = csv.reader(io_string, delimiter=';'); next(reader)
            reglas = Regla.objects.all(); num_transacciones_creadas = 0
            for row in reader:
                if len(row) < 9: continue
                fecha_str, concepto, importe_str = row[2], row[4], row[6]
                if not fecha_str or not concepto or not importe_str: continue
                fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d').date()
                importe_obj = float(str(importe_str).replace('.', '').replace(',', '.'))
                if isinstance(concepto, str) and '\\' in concepto: concepto = concepto.split('\\')[0].strip()
                categoria_asignada = None
                for regla in reglas:
                    if regla.palabra_clave.lower() in str(concepto).lower(): categoria_asignada = regla.categoria_destino; break
                Transaccion.objects.create(fecha_operacion=fecha_obj, concepto_original=str(concepto), importe=importe_obj, categoria=categoria_asignada)
                num_transacciones_creadas += 1
            messages.success(request, f"¡Éxito! Se han importado {num_transacciones_creadas} transacciones.")
        except Exception as e: messages.error(request, f"Ocurrió un error al procesar el archivo: {e}")
        return redirect('subir')
    return render(request, 'core/subir.html')

@login_requerido
def listar_transacciones(request):
    # ... (el contenido de la función es el mismo)
    transacciones = Transaccion.objects.all().order_by('-fecha_operacion', '-id')
    categoria_id_filtro = request.GET.get('categoria'); mes_filtro = request.GET.get('mes'); año_filtro = request.GET.get('año'); tipo_filtro = request.GET.get('tipo')
    if categoria_id_filtro:
        if categoria_id_filtro == '0': transacciones = transacciones.filter(categoria__isnull=True)
        else: transacciones = transacciones.filter(categoria__id=categoria_id_filtro)
    if mes_filtro and año_filtro: transacciones = transacciones.filter(fecha_operacion__month=mes_filtro, fecha_operacion__year=año_filtro)
    if tipo_filtro == 'gastos': transacciones = transacciones.filter(importe__lt=0)
    if tipo_filtro == 'ingresos': transacciones = transacciones.filter(importe__gt=0)
    categorias = Categoria.objects.all()
    contexto = { 'transacciones': transacciones, 'categorias': categorias, }
    return render(request, 'core/listar.html', contexto)

@login_requerido
def actualizar_categoria(request):
    # ... (el contenido de la función es el mismo)
    if request.method == 'POST':
        transaccion_id = request.POST.get('transaccion_id'); categoria_id = request.POST.get('categoria_id')
        try:
            transaccion = Transaccion.objects.get(id=transaccion_id)
            if categoria_id: categoria = Categoria.objects.get(id=categoria_id); transaccion.categoria = categoria
            else: transaccion.categoria = None
            transaccion.save()
        except Exception as e: messages.error(request, f'Ocurrió un error: {e}')
    return redirect('listar')

@login_requerido
def dashboard(request):
    # ... (el contenido de la función es el mismo)
    año_seleccionado = request.GET.get('año', timezone.now().year); mes_seleccionado = request.GET.get('mes', timezone.now().month)
    año_seleccionado = int(año_seleccionado); mes_seleccionado = int(mes_seleccionado)
    transacciones_mes = Transaccion.objects.filter(fecha_operacion__year=año_seleccionado, fecha_operacion__month=mes_seleccionado)
    ingresos_totales = transacciones_mes.filter(importe__gt=0).aggregate(Sum('importe'))['importe__sum'] or 0
    gastos_totales = transacciones_mes.filter(importe__lt=0).aggregate(Sum('importe'))['importe__sum'] or 0
    balance = ingresos_totales + gastos_totales
    gastos_por_categoria = transacciones_mes.filter(importe__lt=0).values('categoria__id', 'categoria__nombre').annotate(total=Sum('importe')).order_by('total')
    labels_grafico_gastos_nombres = [item['categoria__nombre'] or 'Sin Categoría' for item in gastos_por_categoria]
    labels_grafico_gastos_ids = [item['categoria__id'] or 0 for item in gastos_por_categoria]
    data_grafico_gastos_valores = [float(abs(item['total'])) for item in gastos_por_categoria]
    data_evolucion = Transaccion.objects.annotate(mes=TruncMonth('fecha_operacion')).values('mes').annotate(total_ingresos=Sum('importe', filter=Q(importe__gt=0)), total_gastos=Sum('importe', filter=Q(importe__lt=0))).order_by('-mes')[:6][::-1]
    labels_evolucion = [item['mes'].strftime('%b %Y') for item in data_evolucion]
    data_ingresos_evolucion = [float(item['total_ingresos'] or 0) for item in data_evolucion]
    data_gastos_evolucion = [float(abs(item['total_gastos'] or 0)) for item in data_evolucion]
    contexto = {
        'ingresos_totales': ingresos_totales, 'gastos_totales': gastos_totales, 'balance': balance,
        'labels_grafico_gastos_nombres': json.dumps(labels_grafico_gastos_nombres), 'labels_grafico_gastos_ids': json.dumps(labels_grafico_gastos_ids), 'data_grafico_gastos_valores': json.dumps(data_grafico_gastos_valores),
        'labels_evolucion': json.dumps(labels_evolucion), 'data_ingresos_evolucion': json.dumps(data_ingresos_evolucion), 'data_gastos_evolucion': json.dumps(data_gastos_evolucion),
        'años_disponibles': range(2020, timezone.now().year + 2), 'meses_disponibles': range(1, 13),
        'año_seleccionado': año_seleccionado, 'mes_seleccionado': mes_seleccionado, 'transacciones_mes': transacciones_mes,
    }
    return render(request, 'core/dashboard.html', contexto)

@login_requerido
def eliminar_transaccion(request, transaccion_id):
    # ... (el contenido de la función es el mismo)
    if request.method == 'POST':
        try: transaccion = Transaccion.objects.get(id=transaccion_id); transaccion.delete(); messages.success(request, f"Transacción '{transaccion.concepto_original}' eliminada con éxito.")
        except Transaccion.DoesNotExist: messages.error(request, "La transacción que intentas eliminar no existe.")
    return redirect('listar')

@login_requerido
def eliminar_multiples(request):
    # ... (el contenido de la función es el mismo)
    if request.method == 'POST':
        ids_a_borrar = request.POST.getlist('transaccion_ids')
        if not ids_a_borrar: messages.warning(request, "No has seleccionado ninguna transacción para eliminar.")
        else: Transaccion.objects.filter(id__in=ids_a_borrar).delete(); messages.success(request, f"Se han eliminado {len(ids_a_borrar)} transacciones con éxito.")
    return redirect('listar')