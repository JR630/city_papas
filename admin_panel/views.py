"""
Vistas para la aplicación de panel administrativo.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Count, Q, F, DecimalField
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from decimal import Decimal
import json
import csv

from tienda.models import Tienda, Producto, UsuarioTienda, Venta, StockActual, MovimientoInventario
from tienda.forms import MovimientoInventarioEntradaForm, MovimientoInventarioSalidaForm, AjusteStockForm
import logging

logger = logging.getLogger(__name__)


def verificar_admin(usuario):
    """Verifica si el usuario es administrador."""
    try:
        usuario_tienda = usuario.usuario_tienda
        return usuario_tienda.rol == 'administrador'
    except UsuarioTienda.DoesNotExist:
        return False


@login_required(login_url='login')
def admin_dashboard_view(request):
    """Dashboard principal del administrador con métricas consolidadas."""
    if not verificar_admin(request.user):
        return redirect('tienda:tienda-dashboard')
    
    try:
        usuario_tienda = request.user.usuario_tienda
        rol = usuario_tienda.rol
    except:
        rol = 'administrador'
    
    hoy = timezone.now().date()
    hace_7_dias = hoy - timedelta(days=7)
    
    # Métricas generales
    total_tiendas = Tienda.objects.filter(activa=True).count()
    total_productos = Producto.objects.filter(disponible=True).count()
    
    # Ventas del día
    ventas_hoy = Venta.objects.filter(fecha_venta=hoy)
    total_ventas_hoy = ventas_hoy.aggregate(Sum('total'))['total__sum'] or Decimal('0.00')
    cantidad_ventas_hoy = ventas_hoy.count()
    
    # Ventas de los últimos 7 días
    ventas_7_dias = Venta.objects.filter(
        fecha_venta__gte=hace_7_dias
    ).values('fecha_venta').annotate(
        total=Sum('total'),
        cantidad=Count('id')
    ).order_by('fecha_venta')
    
    # Ingresos por tienda (últimos 30 días)
    hace_30_dias = hoy - timedelta(days=30)
    ingresos_por_tienda = Tienda.objects.filter(activa=True).annotate(
        ingresos=Sum('ventas__total', filter=Q(ventas__fecha_venta__gte=hace_30_dias))
    ).order_by('-ingresos').values('id', 'nombre', 'ingresos')[:10]
    
    # Productos más vendidos
    productos_top = Venta.objects.filter(
        fecha_venta__gte=hace_30_dias
    ).values('producto__nombre').annotate(
        cantidad_total=Sum('cantidad'),
        ingresos=Sum('total')
    ).order_by('-cantidad_total')[:10]
    
    # Preparar datos para gráficos
    datos_7_dias = json.dumps([(str(v['fecha_venta']), float(v['total'])) for v in ventas_7_dias])
    datos_tiendas = json.dumps([(t['nombre'], float(t['ingresos'] or 0)) for t in ingresos_por_tienda])
    datos_productos = json.dumps([(p['producto__nombre'], int(p['cantidad_total'])) for p in productos_top])
    
    context = {
        'total_tiendas': total_tiendas,
        'total_productos': total_productos,
        'total_ventas_hoy': total_ventas_hoy,
        'cantidad_ventas_hoy': cantidad_ventas_hoy,
        'ventas_7_dias': ventas_7_dias,
        'ingresos_por_tienda': ingresos_por_tienda,
        'productos_top': productos_top,
        'datos_7_dias': datos_7_dias,
        'datos_tiendas': datos_tiendas,
        'datos_productos': datos_productos,
        'rol': rol,
    }
    
    return render(request, 'admin_panel/dashboard.html', context)


@login_required(login_url='login')
def tiendas_list_view(request):
    """Lista de todas las tiendas con opciones de gestión."""
    if not verificar_admin(request.user):
        return redirect('tienda:tienda-dashboard')
    
    tiendas = Tienda.objects.all().annotate(
        cantidad_usuarios=Count('usuarios'),
        total_ventas_hoy=Sum('ventas__total', filter=Q(
            ventas__fecha_venta=timezone.now().date()
        ))
    ).order_by('nombre')
    
    try:
        usuario_tienda = request.user.usuario_tienda
        rol_ctx = usuario_tienda.rol
    except:
        rol_ctx = 'administrador'
    
    context = {
        'tiendas': tiendas,
        'rol': rol_ctx,
    }
    
    return render(request, 'admin_panel/tiendas_list.html', context)


@login_required(login_url='login')
def tienda_detail_view(request, tienda_id):
    """Detalle de una tienda específica con historial de ventas."""
    if not verificar_admin(request.user):
        return redirect('tienda:tienda-dashboard')
    
    tienda = get_object_or_404(Tienda, id=tienda_id)
    
    # Filtros
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    
    ventas = tienda.ventas.select_related('producto').order_by('-fecha_venta')
    
    if fecha_desde:
        fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
        ventas = ventas.filter(fecha_venta__gte=fecha_desde_obj)
    
    if fecha_hasta:
        fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
        ventas = ventas.filter(fecha_venta__lte=fecha_hasta_obj)
    
    total = ventas.aggregate(Sum('total'))['total__sum'] or Decimal('0.00')
    
    # Resumen por día
    ventas_por_dia = Venta.objects.filter(tienda=tienda).values('fecha_venta').annotate(
        total=Sum('total'),
        cantidad=Count('id')
    ).order_by('-fecha_venta')[:30]
    
    usuarios = tienda.usuarios.select_related('usuario')
    
    try:
        usuario_tienda = request.user.usuario_tienda
        rol_ctx = usuario_tienda.rol
    except:
        rol_ctx = 'administrador'
    
    context = {
        'tienda': tienda,
        'ventas': ventas,
        'total': total,
        'ventas_por_dia': ventas_por_dia,
        'usuarios': usuarios,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'rol': rol_ctx,
    }
    
    return render(request, 'admin_panel/tienda_detail.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def crear_tienda_view(request):
    """Crear una nueva tienda."""
    if not verificar_admin(request.user):
        return redirect('tienda:tienda-dashboard')
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        ciudad = request.POST.get('ciudad')
        direccion = request.POST.get('direccion')
        telefono = request.POST.get('telefono')
        email = request.POST.get('email')
        
        # Validaciones
        if Tienda.objects.filter(nombre=nombre).exists():
            return render(request, 'admin_panel/crear_editar_tienda.html', {
                'error': 'Una tienda con ese nombre ya existe.',
                'rol': 'administrador',
            })
        
        tienda = Tienda.objects.create(
            nombre=nombre,
            ciudad=ciudad,
            direccion=direccion,
            telefono=telefono,
            email=email,
        )
        
        return redirect('admin_panel:tienda-detail', tienda_id=tienda.id)
    
    return render(request, 'admin_panel/crear_editar_tienda.html')


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def editar_tienda_view(request, tienda_id):
    """Editar una tienda existente."""
    if not verificar_admin(request.user):
        return redirect('tienda:tienda-dashboard')
    
    tienda = get_object_or_404(Tienda, id=tienda_id)
    
    if request.method == 'POST':
        tienda.nombre = request.POST.get('nombre')
        tienda.ciudad = request.POST.get('ciudad')
        tienda.direccion = request.POST.get('direccion')
        tienda.telefono = request.POST.get('telefono')
        tienda.email = request.POST.get('email')
        tienda.activa = request.POST.get('activa') == 'on'
        tienda.save()
        
        return redirect('admin_panel:tienda-detail', tienda_id=tienda.id)
    
    context = {
        'tienda': tienda,
        'editando': True,
        'rol': 'administrador',
    }
    
    return render(request, 'admin_panel/crear_editar_tienda.html', context)


@login_required(login_url='login')
def productos_list_view(request):
    """Lista de productos con CRUD."""
    if not verificar_admin(request.user):
        return redirect('tienda:tienda-dashboard')
    
    categoria = request.GET.get('categoria')
    productos = Producto.objects.all().order_by('categoria', 'nombre')
    
    if categoria:
        productos = productos.filter(categoria=categoria)
    
    categorias = Producto.objects.values_list('categoria', flat=True).distinct()
    
    try:
        usuario_tienda = request.user.usuario_tienda
        rol_ctx = usuario_tienda.rol
    except:
        rol_ctx = 'administrador'
    
    context = {
        'productos': productos,
        'categorias': categorias,
        'categoria_filtro': categoria,
        'rol': rol_ctx,
    }
    
    return render(request, 'admin_panel/productos_list.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def crear_producto_view(request):
    """Crear un nuevo producto."""
    if not verificar_admin(request.user):
        return redirect('tienda:tienda-dashboard')
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        categoria = request.POST.get('categoria')
        precio = request.POST.get('precio')
        
        try:
            precio = Decimal(precio)
            producto = Producto.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                categoria=categoria,
                precio=precio,
            )
            return redirect('admin_panel:productos-list')
        except Exception as e:
            return render(request, 'admin_panel/crear_editar_producto.html', {
                'error': f'Error al crear producto: {str(e)}',
                'rol': 'administrador',
            })
    
    categorias = [c[0] for c in Producto._meta.get_field('categoria').choices]
    context = {
        'categorias': categorias,
        'rol': 'administrador',
    }
    
    return render(request, 'admin_panel/crear_editar_producto.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def editar_producto_view(request, producto_id):
    """Editar un producto existente."""
    if not verificar_admin(request.user):
        return redirect('tienda:tienda-dashboard')
    
    producto = get_object_or_404(Producto, id=producto_id)
    
    if request.method == 'POST':
        producto.nombre = request.POST.get('nombre')
        producto.descripcion = request.POST.get('descripcion')
        producto.categoria = request.POST.get('categoria')
        producto.precio = Decimal(request.POST.get('precio'))
        producto.disponible = request.POST.get('disponible') == 'on'
        producto.save()
        
        return redirect('admin_panel:productos-list')
    
    categorias = [c[0] for c in Producto._meta.get_field('categoria').choices]
    context = {
        'producto': producto,
        'categorias': categorias,
        'editando': True,
        'rol': 'administrador',
    }
    
    return render(request, 'admin_panel/crear_editar_producto.html', context)


@login_required(login_url='login')
@require_http_methods(["POST"])
def eliminar_producto_view(request, producto_id):
    """Eliminar un producto (desactivar)."""
    if not verificar_admin(request.user):
        return redirect('tienda:tienda-dashboard')
    
    producto = get_object_or_404(Producto, id=producto_id)
    producto.disponible = False
    producto.save()
    
    return redirect('admin_panel:productos-list')


@login_required(login_url='login')
def reportes_view(request):
    """Generador de reportes con filtros avanzados."""
    if not verificar_admin(request.user):
        return redirect('tienda:tienda-dashboard')
    
    # Filtros
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    tienda_id = request.GET.get('tienda')
    producto_id = request.GET.get('producto')
    
    ventas = Venta.objects.select_related('tienda', 'producto')
    
    hoy = timezone.now().date()
    if fecha_desde:
        fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
        ventas = ventas.filter(fecha_venta__gte=fecha_desde_obj)
    else:
        fecha_desde = (hoy - timedelta(days=30)).isoformat()
    
    if fecha_hasta:
        fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
        ventas = ventas.filter(fecha_venta__lte=fecha_hasta_obj)
    else:
        fecha_hasta = hoy.isoformat()
    
    if tienda_id:
        ventas = ventas.filter(tienda_id=tienda_id)
    
    if producto_id:
        ventas = ventas.filter(producto_id=producto_id)
    
    # Resumen
    total = ventas.aggregate(Sum('total'))['total__sum'] or Decimal('0.00')
    cantidad = ventas.count()
    
    # Resumen por tienda
    resumen_tienda = ventas.values('tienda__nombre').annotate(
        total=Sum('total'),
        cantidad=Count('id')
    ).order_by('-total')
    
    # Resumen por producto
    resumen_producto = ventas.values('producto__nombre', 'producto__categoria').annotate(
        total=Sum('total'),
        cantidad=Sum('cantidad')
    ).order_by('-total')
    
    # Resumen por día
    resumen_dia = ventas.values('fecha_venta').annotate(
        total=Sum('total'),
        cantidad=Count('id')
    ).order_by('fecha_venta')
    
    tiendas = Tienda.objects.filter(activa=True).order_by('nombre')
    productos = Producto.objects.filter(disponible=True).order_by('nombre')
    
    # Calcular promedio
    promedio = total / cantidad if cantidad > 0 else Decimal('0.00')
    
    try:
        usuario_tienda = request.user.usuario_tienda
        rol_ctx = usuario_tienda.rol
    except:
        rol_ctx = 'administrador'
    
    context = {
        'ventas': ventas,
        'total': total,
        'cantidad': cantidad,
        'promedio': promedio,
        'resumen_tienda': resumen_tienda,
        'resumen_producto': resumen_producto,
        'resumen_dia': resumen_dia,
        'tiendas': tiendas,
        'productos': productos,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'tienda_filtro': tienda_id,
        'producto_filtro': producto_id,
        'rol': rol_ctx,
    }
    
    return render(request, 'admin_panel/reportes.html', context)


@login_required(login_url='login')
def exportar_reportes_view(request):
    """Exportar reportes a CSV."""
    if not verificar_admin(request.user):
        return redirect('tienda:tienda-dashboard')
    
    # Filtros
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    tienda_id = request.GET.get('tienda')
    
    ventas = Venta.objects.select_related('tienda', 'producto')
    
    if fecha_desde:
        fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
        ventas = ventas.filter(fecha_venta__gte=fecha_desde_obj)
    
    if fecha_hasta:
        fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
        ventas = ventas.filter(fecha_venta__lte=fecha_hasta_obj)
    
    if tienda_id:
        ventas = ventas.filter(tienda_id=tienda_id)
    
    # Crear CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reporte_ventas.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Tienda', 'Producto', 'Categoría', 'Cantidad', 'Precio Unitario', 'Total', 'Fecha'])
    
    for venta in ventas:
        writer.writerow([
            venta.tienda.nombre,
            venta.producto.nombre,
            venta.producto.get_categoria_display(),
            venta.cantidad,
            venta.precio_unitario,
            venta.total,
            venta.fecha_venta,
        ])
    
    return response


# ============= VISTAS DE INVENTARIO ADMIN =============

@login_required(login_url='login')
def admin_inventario_view(request):
    """Vista de inventario consolidado para administrador (todas las tiendas)."""
    if not verificar_admin(request.user):
        return redirect('tienda:tienda-dashboard')
    
    try:
        usuario_tienda = request.user.usuario_tienda
    except UsuarioTienda.DoesNotExist:
        return redirect('login')
    
    # Obtener todos los stocks de todas las tiendas
    stocks = StockActual.objects.select_related('tienda', 'producto').order_by('producto__categoria', 'producto__nombre', 'tienda__nombre')
    
    # Filtros
    filtro_estado = request.GET.get('estado', '')
    filtro_tienda = request.GET.get('tienda', '')
    
    if filtro_estado:
        if filtro_estado == 'bajo':
            stocks = stocks.filter(cantidad__gt=0, cantidad__lt=F('stock_minimo'))
        elif filtro_estado == 'agotado':
            stocks = stocks.filter(cantidad=0)
        elif filtro_estado == 'normal':
            stocks = stocks.filter(cantidad__gte=F('stock_minimo'))
    
    if filtro_tienda:
        stocks = stocks.filter(tienda_id=filtro_tienda)
    
    # Agrupar por categoría
    from itertools import groupby
    stocks_list = list(stocks)
    stocks_por_categoria = {}
    for categoria, items in groupby(stocks_list, key=lambda x: x.producto.get_categoria_display()):
        stocks_por_categoria[categoria] = list(items)
    
    # Calcular totales globales
    total_productos = stocks.count()
    productos_bajo_stock = stocks.filter(cantidad__gt=0, cantidad__lt=F('stock_minimo')).count()
    productos_agotados = stocks.filter(cantidad=0).count()
    
    # Stock por tienda
    stock_por_tienda = Tienda.objects.filter(activa=True).annotate(
        total_items=Count('stocks'),
        total_cantidad=Sum('stocks__cantidad'),
        items_bajo_stock=Count('stocks', filter=Q(stocks__cantidad__gt=0, stocks__cantidad__lt=F('stocks__stock_minimo'))),
        items_agotados=Count('stocks', filter=Q(stocks__cantidad=0)),
    )
    
    # Obtener todas las tiendas para el filtro
    tiendas = Tienda.objects.filter(activa=True).order_by('nombre')
    
    context = {
        'stocks': stocks,
        'stocks_por_categoria': stocks_por_categoria,
        'total_productos': total_productos,
        'productos_bajo_stock': productos_bajo_stock,
        'productos_agotados': productos_agotados,
        'filtro_estado': filtro_estado,
        'filtro_tienda': filtro_tienda,
        'tiendas': tiendas,
        'stock_por_tienda': stock_por_tienda,
        'rol': usuario_tienda.rol,
        'es_admin': True,
    }
    
    return render(request, 'admin_panel/inventario.html', context)


# ============= VISTAS DE MOVIMIENTOS ADMIN =============

@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def admin_entrada_producto_view(request):
    """Vista para que admin registre entrada de productos."""
    if not verificar_admin(request.user):
        return redirect('tienda:tienda-dashboard')
    
    tienda_id = request.GET.get('tienda') or request.POST.get('tienda')
    
    if not tienda_id:
        # Mostrar selector de tienda
        tiendas = Tienda.objects.filter(activa=True).order_by('nombre')
        return render(request, 'admin_panel/seleccionar_tienda.html', {
            'tiendas': tiendas,
            'accion': 'entrada',
            'url': 'admin_panel:admin-entrada-producto',
        })
    
    try:
        usuario_tienda = request.user.usuario_tienda
    except UsuarioTienda.DoesNotExist:
        return redirect('login')
    
    tienda = get_object_or_404(Tienda, id=tienda_id)
    
    if request.method == 'POST':
        form = MovimientoInventarioEntradaForm(request.POST)
        if form.is_valid():
            try:
                movimiento = form.save(commit=False)
                movimiento.tienda = tienda
                movimiento.tipo_movimiento = 'entrada'
                movimiento.registrado_por = request.user
                movimiento.save()
                
                logger.info(f"Entrada registrada por admin: {movimiento.id} - {movimiento.producto.nombre} - Cantidad: {movimiento.cantidad}")
                
                return redirect('admin_panel:admin-inventario')
            except Exception as e:
                logger.error(f"Error al registrar entrada: {str(e)}")
                form.add_error(None, f"Error al registrar la entrada: {str(e)}")
    else:
        form = MovimientoInventarioEntradaForm()
    
    context = {
        'form': form,
        'tienda': tienda,
        'titulo': 'Registrar Entrada de Productos',
        'rol': usuario_tienda.rol,
    }
    
    return render(request, 'tienda/entrada_producto.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def admin_salida_producto_view(request):
    """Vista para que admin registre salida de productos."""
    if not verificar_admin(request.user):
        return redirect('tienda:tienda-dashboard')
    
    tienda_id = request.GET.get('tienda') or request.POST.get('tienda')
    
    if not tienda_id:
        # Mostrar selector de tienda
        tiendas = Tienda.objects.filter(activa=True).order_by('nombre')
        return render(request, 'admin_panel/seleccionar_tienda.html', {
            'tiendas': tiendas,
            'accion': 'salida',
            'url': 'admin_panel:admin-salida-producto',
        })
    
    try:
        usuario_tienda = request.user.usuario_tienda
    except UsuarioTienda.DoesNotExist:
        return redirect('login')
    
    tienda = get_object_or_404(Tienda, id=tienda_id)
    
    if request.method == 'POST':
        form = MovimientoInventarioSalidaForm(request.POST)
        if form.is_valid():
            try:
                producto = form.cleaned_data['producto']
                cantidad = form.cleaned_data['cantidad']
                
                # Verificar stock disponible
                stock = StockActual.objects.get_or_create(tienda=tienda, producto=producto)[0]
                if stock.cantidad < cantidad:
                    form.add_error('cantidad', f'Stock insuficiente. Disponible: {stock.cantidad} unidades')
                else:
                    movimiento = form.save(commit=False)
                    movimiento.tienda = tienda
                    movimiento.tipo_movimiento = 'salida'
                    movimiento.registrado_por = request.user
                    movimiento.save()
                    
                    logger.info(f"Salida registrada por admin: {movimiento.id} - {movimiento.producto.nombre} - Cantidad: {movimiento.cantidad}")
                    
                    return redirect('admin_panel:admin-inventario')
            except Exception as e:
                logger.error(f"Error al registrar salida: {str(e)}")
                form.add_error(None, f"Error al registrar la salida: {str(e)}")
    else:
        form = MovimientoInventarioSalidaForm()
    
    context = {
        'form': form,
        'tienda': tienda,
        'titulo': 'Registrar Salida de Productos',
        'rol': usuario_tienda.rol,
    }
    
    return render(request, 'tienda/salida_producto.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def admin_ajuste_stock_view(request):
    """Vista para que admin ajuste stock."""
    if not verificar_admin(request.user):
        return redirect('tienda:tienda-dashboard')
    
    tienda_id = request.GET.get('tienda') or request.POST.get('tienda')
    
    if not tienda_id:
        # Mostrar selector de tienda
        tiendas = Tienda.objects.filter(activa=True).order_by('nombre')
        return render(request, 'admin_panel/seleccionar_tienda.html', {
            'tiendas': tiendas,
            'accion': 'ajuste',
            'url': 'admin_panel:admin-ajuste-stock',
        })
    
    try:
        usuario_tienda = request.user.usuario_tienda
    except UsuarioTienda.DoesNotExist:
        return redirect('login')
    
    tienda = get_object_or_404(Tienda, id=tienda_id)
    
    if request.method == 'POST':
        form = AjusteStockForm(request.POST)
        if form.is_valid():
            try:
                producto = form.cleaned_data['producto']
                nueva_cantidad = form.cleaned_data['cantidad']
                descripcion = form.cleaned_data['descripcion']
                
                # Crear movimiento de ajuste
                movimiento = MovimientoInventario.objects.create(
                    tienda=tienda,
                    producto=producto,
                    tipo_movimiento='ajuste',
                    cantidad=nueva_cantidad,
                    descripcion=descripcion,
                    registrado_por=request.user,
                )
                
                logger.info(f"Ajuste de stock realizado por admin: {movimiento.id} - {producto.nombre} - Nueva cantidad: {nueva_cantidad}")
                
                return redirect('admin_panel:admin-inventario')
            except Exception as e:
                logger.error(f"Error al ajustar stock: {str(e)}")
                form.add_error(None, f"Error al ajustar el stock: {str(e)}")
    else:
        form = AjusteStockForm()
    
    context = {
        'form': form,
        'tienda': tienda,
        'titulo': 'Ajustar Stock',
        'rol': usuario_tienda.rol,
    }
    
    return render(request, 'tienda/ajuste_stock.html', context)


@login_required(login_url='login')
def admin_historial_movimientos_view(request):
    """Vista del historial de movimientos de inventario para admin (todas las tiendas)."""
    if not verificar_admin(request.user):
        return redirect('tienda:tienda-dashboard')
    
    try:
        usuario_tienda = request.user.usuario_tienda
    except UsuarioTienda.DoesNotExist:
        return redirect('login')
    
    # Obtener movimientos de todas las tiendas
    movimientos = MovimientoInventario.objects.select_related('producto', 'registrado_por', 'tienda').order_by('-fecha_movimiento')
    
    # Filtros
    filtro_tipo = request.GET.get('tipo', '')
    filtro_producto = request.GET.get('producto', '')
    filtro_tienda = request.GET.get('tienda', '')
    filtro_fecha_desde = request.GET.get('fecha_desde', '')
    filtro_fecha_hasta = request.GET.get('fecha_hasta', '')
    
    if filtro_tipo:
        movimientos = movimientos.filter(tipo_movimiento=filtro_tipo)
    
    if filtro_producto:
        movimientos = movimientos.filter(producto__id=filtro_producto)
    
    if filtro_tienda:
        movimientos = movimientos.filter(tienda__id=filtro_tienda)
    
    if filtro_fecha_desde:
        try:
            fecha_desde = datetime.strptime(filtro_fecha_desde, '%Y-%m-%d').date()
            movimientos = movimientos.filter(fecha_movimiento__date__gte=fecha_desde)
        except ValueError:
            pass
    
    if filtro_fecha_hasta:
        try:
            fecha_hasta = datetime.strptime(filtro_fecha_hasta, '%Y-%m-%d').date()
            movimientos = movimientos.filter(fecha_movimiento__date__lte=fecha_hasta)
        except ValueError:
            pass
    
    # Paginación
    from django.core.paginator import Paginator
    paginator = Paginator(movimientos, 20)
    page_num = request.GET.get('page', 1)
    page = paginator.get_page(page_num)
    
    # Obtener listas para los filtros
    productos = Producto.objects.filter(disponible=True).order_by('categoria', 'nombre')
    tiendas = Tienda.objects.filter(activa=True).order_by('nombre')
    
    context = {
        'movimientos': page.object_list,
        'page': page,
        'productos': productos,
        'tiendas': tiendas,
        'filtro_tipo': filtro_tipo,
        'filtro_producto': filtro_producto,
        'filtro_tienda': filtro_tienda,
        'filtro_fecha_desde': filtro_fecha_desde,
        'filtro_fecha_hasta': filtro_fecha_hasta,
        'total_movimientos': paginator.count,
        'rol': usuario_tienda.rol,
        'es_admin': True,
    }
    
    return render(request, 'admin_panel/historial_movimientos.html', context)

