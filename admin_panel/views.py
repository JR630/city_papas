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

from tienda.models import Tienda, Producto, UsuarioTienda, Venta


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
        'rol': 'administrador',
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
    
    context = {
        'tiendas': tiendas,
        'rol': 'administrador',
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
    
    context = {
        'tienda': tienda,
        'ventas': ventas,
        'total': total,
        'ventas_por_dia': ventas_por_dia,
        'usuarios': usuarios,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'rol': 'administrador',
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
                'error': 'Una tienda con ese nombre ya existe.'
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
    
    context = {
        'productos': productos,
        'categorias': categorias,
        'categoria_filtro': categoria,
        'rol': 'administrador',
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
                'error': f'Error al crear producto: {str(e)}'
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
def usuarios_list_view(request):
    """Lista de usuarios con gestión."""
    if not verificar_admin(request.user):
        return redirect('tienda:tienda-dashboard')
    
    tienda_id = request.GET.get('tienda')
    usuarios = UsuarioTienda.objects.select_related('usuario', 'tienda')
    
    if tienda_id:
        usuarios = usuarios.filter(tienda_id=tienda_id)
    
    tiendas = Tienda.objects.filter(activa=True).order_by('nombre')
    
    context = {
        'usuarios': usuarios,
        'tiendas': tiendas,
        'tienda_filtro': tienda_id,
        'rol': 'administrador',
    }
    
    return render(request, 'admin_panel/usuarios_list.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def crear_usuario_view(request):
    """Crear un nuevo usuario."""
    if not verificar_admin(request.user):
        return redirect('tienda:tienda-dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        rol = request.POST.get('rol')
        tienda_id = request.POST.get('tienda')
        
        # Validaciones
        if User.objects.filter(username=username).exists():
            return render(request, 'admin_panel/crear_editar_usuario.html', {
                'error': 'El nombre de usuario ya existe.',
                'tiendas': Tienda.objects.filter(activa=True),
            })
        
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
            )
            
            tienda = None
            if tienda_id and rol == 'tienda':
                tienda = get_object_or_404(Tienda, id=tienda_id)
            
            UsuarioTienda.objects.create(
                usuario=user,
                tienda=tienda,
                rol=rol,
            )
            
            return redirect('admin_panel:usuarios-list')
        except Exception as e:
            return render(request, 'admin_panel/crear_editar_usuario.html', {
                'error': f'Error: {str(e)}',
                'tiendas': Tienda.objects.filter(activa=True),
            })
    
    tiendas = Tienda.objects.filter(activa=True).order_by('nombre')
    context = {
        'tiendas': tiendas,
        'roles': [('tienda', 'Tienda'), ('administrador', 'Administrador')],
        'rol': 'administrador',
    }
    
    return render(request, 'admin_panel/crear_editar_usuario.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def editar_usuario_view(request, usuario_id):
    """Editar un usuario existente."""
    if not verificar_admin(request.user):
        return redirect('tienda:tienda-dashboard')
    
    usuario_tienda = get_object_or_404(UsuarioTienda, id=usuario_id)
    
    if request.method == 'POST':
        usuario_tienda.rol = request.POST.get('rol')
        
        if usuario_tienda.rol == 'tienda':
            tienda_id = request.POST.get('tienda')
            usuario_tienda.tienda = get_object_or_404(Tienda, id=tienda_id) if tienda_id else None
        else:
            usuario_tienda.tienda = None
        
        usuario_tienda.activo = request.POST.get('activo') == 'on'
        usuario_tienda.save()
        
        return redirect('admin_panel:usuarios-list')
    
    tiendas = Tienda.objects.filter(activa=True).order_by('nombre')
    context = {
        'usuario_tienda': usuario_tienda,
        'tiendas': tiendas,
        'roles': [('tienda', 'Tienda'), ('administrador', 'Administrador')],
        'editando': True,
        'rol': 'administrador',
    }
    
    return render(request, 'admin_panel/crear_editar_usuario.html', context)


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
        'rol': 'administrador',
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
