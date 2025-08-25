from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Transaccion, Categoria, Regla
import csv, io
from datetime import datetime
from django.db.models import Sum, Q
from django.utils import timezone
import json
from django.db.models.functions import TruncMonth
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

@login_required
def subir_movimientos(request):
    if request.method == 'POST':
        if 'csv_file' not in request.FILES: messages.error(request, "No se seleccionó ningún archivo."); return redirect('subir')
        csv_file = request.FILES['csv_file']
        if not csv_file.name.endswith('.csv'): messages.error(request, "El archivo debe tener formato .csv"); return redirect('subir')
        try:
            # Transaccion.objects.all().delete() # LÍNEA COMENTADA: Ya no se borran los datos antiguos.
            data_set = csv_file.read().decode('utf-8'); io_string = io.StringIO(data_set)
            for _ in range(5): next(io_string)
            reader = csv.reader(io_string, delimiter=';'); next(reader)
            reglas = Regla.objects.all()
            num_transacciones_creadas = 0
            num_transacciones_ignoradas = 0
            for row in reader:
                if len(row) < 9: continue
                fecha_str, concepto, importe_str = row[2], row[4], row[6]
                if not fecha_str or not concepto or not importe_str: continue
                fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d').date()
                importe_obj = float(str(importe_str).replace('.', '').replace(',', '.'))
                if isinstance(concepto, str) and '\\' in concepto: concepto = concepto.split('\\')[0].strip()
                if Transaccion.objects.filter(fecha_operacion=fecha_obj, concepto_original=str(concepto), importe=importe_obj).exists():
                    num_transacciones_ignoradas += 1
                    continue
                categoria_asignada = None
                for regla in reglas:
                    if regla.palabra_clave.lower() in str(concepto).lower(): categoria_asignada = regla.categoria_destino; break
                Transaccion.objects.create(fecha_operacion=fecha_obj, concepto_original=str(concepto), importe=importe_obj, categoria=categoria_asignada)
                num_transacciones_creadas += 1
            messages.success(request, f"¡Éxito! Se han importado {num_transacciones_creadas} nuevas transacciones. Se ignoraron {num_transacciones_ignoradas} duplicadas.")
        except Exception as e: messages.error(request, f"Ocurrió un error al procesar el archivo: {e}")
        return redirect('subir')
    return render(request, 'core/subir.html')

@login_required
def listar_transacciones(request):
    transacciones = Transaccion.objects.all().order_by('-fecha_operacion', '-id')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    concepto_query = request.GET.get('concepto')
    categoria_id_filtro = request.GET.get('categoria')
    if fecha_inicio:
        transacciones = transacciones.filter(fecha_operacion__gte=fecha_inicio)
    if fecha_fin:
        transacciones = transacciones.filter(fecha_operacion__lte=fecha_fin)
    if concepto_query:
        transacciones = transacciones.filter(concepto_original__icontains=concepto_query)
    if categoria_id_filtro:
        if categoria_id_filtro == '0':
            transacciones = transacciones.filter(categoria__isnull=True)
        else:
            transacciones = transacciones.filter(categoria__id=categoria_id_filtro)
    categorias = Categoria.objects.all()
    contexto = { 
        'transacciones': transacciones, 
        'categorias': categorias,
        'valores_filtro': { 'fecha_inicio': fecha_inicio, 'fecha_fin': fecha_fin, 'concepto': concepto_query, 'categoria': categoria_id_filtro, }
    }
    return render(request, 'core/listar.html', contexto)

@login_required
def actualizar_categoria(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            transaccion_id = data.get('transaccion_id')
            categoria_id = data.get('categoria_id')
            transaccion = Transaccion.objects.get(id=transaccion_id)
            if categoria_id:
                categoria = Categoria.objects.get(id=categoria_id)
                transaccion.categoria = categoria
            else:
                transaccion.categoria = None
            transaccion.save()
            return JsonResponse({'status': 'ok', 'message': 'Categoría actualizada con éxito.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Método no permitido.'}, status=405)

@login_required
def dashboard(request):
    año_seleccionado = request.GET.get('año', timezone.now().year); mes_filtro = request.GET.get('mes')
    año_seleccionado = int(año_seleccionado); mes_seleccionado = int(mes_filtro or timezone.now().month)
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

@login_required
def eliminar_transaccion(request, transaccion_id):
    if request.method == 'POST':
        try: transaccion = Transaccion.objects.get(id=transaccion_id); transaccion.delete(); messages.success(request, f"Transacción '{transaccion.concepto_original}' eliminada con éxito.")
        except Transaccion.DoesNotExist: messages.error(request, "La transacción que intentas eliminar no existe.")
    return redirect('listar')

@login_required
def eliminar_multiples(request):
    if request.method == 'POST':
        ids_a_borrar = request.POST.getlist('transaccion_ids')
        if not ids_a_borrar: messages.warning(request, "No has seleccionado ninguna transacción para eliminar.")
        else: Transaccion.objects.filter(id__in=ids_a_borrar).delete(); messages.success(request, f"Se han eliminado {len(ids_a_borrar)} transacciones con éxito.")
    return redirect('listar')

# ==============================================================================
# VISTA PARA LA NUEVA PÁGINA DE ANÁLISIS AVANZADO
# ==============================================================================
@login_required
def analisis_avanzado(request):
    # Por ahora, solo obtenemos las categorías para el formulario de filtros.
    # Más adelante añadiremos aquí toda la lógica de cálculo.
    categorias = Categoria.objects.all().order_by('nombre')
    
    contexto = {
        'categorias': categorias
    }
    return render(request, 'core/analisis.html', contexto)