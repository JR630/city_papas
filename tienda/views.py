"""
Vistas para la aplicación de tienda.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.db.models import Sum, F, Count, Q
from django.db import IntegrityError
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import json
import logging

from .models import Tienda, Producto, UsuarioTienda, Venta, CierreCaja, StockActual, MovimientoInventario
from .forms import MovimientoInventarioEntradaForm, MovimientoInventarioSalidaForm, AjusteStockForm, StockMinimoForm

logger = logging.getLogger(__name__)


def login_view(request):
    """Vista para el login de usuarios con selección de rol."""
    # Si el usuario ya está autenticado, redirigir al panel correspondiente
    if request.user.is_authenticated:
        try:
            usuario_tienda = request.user.usuario_tienda
            if usuario_tienda.rol == 'administrador':
                return redirect('admin_panel:admin-dashboard')
            else:
                return redirect('tienda:tienda-dashboard')
        except UsuarioTienda.DoesNotExist:
            logout(request)
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        rol_seleccionado = request.POST.get('rol', '').strip()
        
        # Validar que se haya seleccionado un rol
        if not rol_seleccionado:
            return render(request, 'tienda/login.html', {
                'error': 'Debes seleccionar un rol para continuar.'
            })
        
        # Autenticar usuario
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            try:
                usuario_tienda = user.usuario_tienda
                
                # Validar que el rol seleccionado coincida
                if usuario_tienda.rol != rol_seleccionado:
                    rol_correcto = 'Administrador' if usuario_tienda.rol == 'administrador' else 'Tienda'
                    return render(request, 'tienda/login.html', {
                        'error': f'Este usuario tiene rol de {rol_correcto}. Selecciona el rol correcto.'
                    })
                
                # Validar que el usuario esté activo
                if not usuario_tienda.activo:
                    return render(request, 'tienda/login.html', {
                        'error': 'Tu usuario ha sido desactivado. Contacta con el administrador.'
                    })
                
                # Login exitoso
                login(request, user)
                
                if usuario_tienda.rol == 'administrador':
                    return redirect('admin_panel:admin-dashboard')
                else:
                    return redirect('tienda:tienda-dashboard')
                    
            except UsuarioTienda.DoesNotExist:
                return render(request, 'tienda/login.html', {
                    'error': 'Tu usuario no tiene rol asignado. Contacta con el administrador.'
                })
        else:
            return render(request, 'tienda/login.html', {
                'error': 'Usuario o contraseña incorrectos.'
            })
    
    return render(request, 'tienda/login.html')


def logout_view(request):
    """Vista para cerrar sesión."""
    logout(request)
    return redirect('login')


def register_tienda_view(request):
    """Vista para que una tienda se registre en el sistema."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        tienda_nombre = request.POST.get('tienda_nombre')
        tienda_email = request.POST.get('tienda_email')
        tienda_telefono = request.POST.get('tienda_telefono')
        tienda_ciudad = request.POST.get('tienda_ciudad')
        tienda_direccion = request.POST.get('tienda_direccion')
        
        # Validaciones
        errores = []
        
        if User.objects.filter(username=username).exists():
            errores.append('El nombre de usuario ya existe.')
        
        if password != password_confirm:
            errores.append('Las contraseñas no coinciden.')
        
        if len(password) < 6:
            errores.append('La contraseña debe tener al menos 6 caracteres.')
        
        if Tienda.objects.filter(nombre=tienda_nombre).exists():
            errores.append('Una tienda con ese nombre ya existe.')
        
        if errores:
            return render(request, 'tienda/register.html', {
                'errores': errores,
                'username': username,
                'tienda_nombre': tienda_nombre,
            })
        
        # Crear tienda
        tienda = Tienda.objects.create(
            nombre=tienda_nombre,
            email=tienda_email,
            telefono=tienda_telefono,
            ciudad=tienda_ciudad,
            direccion=tienda_direccion,
        )
        
        # Crear usuario
        user = User.objects.create_user(
            username=username,
            email=tienda_email,
            password=password,
            first_name=tienda_nombre,
        )
        
        # Crear relación UsuarioTienda
        UsuarioTienda.objects.create(
            usuario=user,
            tienda=tienda,
            rol='tienda',
        )
        
        # Hacer login automático
        login(request, user)
        return redirect('tienda:tienda-dashboard')
    
    return render(request, 'tienda/register.html')


@login_required(login_url='login')
def tienda_dashboard_view(request):
    """Dashboard de la tienda con resumen de ventas del día."""
    try:
        usuario_tienda = request.user.usuario_tienda
        if usuario_tienda.rol != 'tienda':
            return redirect('admin-dashboard')
    except UsuarioTienda.DoesNotExist:
        return redirect('login')
    
    tienda = usuario_tienda.tienda
    hoy = timezone.now().date()
    
    # Ventas del día actual
    ventas_hoy = Venta.objects.filter(
        tienda=tienda,
        fecha_venta=hoy
    ).select_related('producto').order_by('-fecha')
    
    # Si no hay ventas hoy, mostrar todas las ventas recientes (últimos 7 días)
    if not ventas_hoy.exists():
        hace_7_dias = hoy - timedelta(days=6)
        ventas_hoy = Venta.objects.filter(
            tienda=tienda,
            fecha_venta__gte=hace_7_dias,
            fecha_venta__lte=hoy
        ).select_related('producto').order_by('-fecha_venta', '-fecha')
    
    total_hoy = ventas_hoy.aggregate(
        total=Sum('total')
    )['total'] or Decimal('0.00')
    
    cantidad_ventas_hoy = ventas_hoy.count()
    total_productos_vendidos = ventas_hoy.aggregate(
        total=Sum('cantidad')
    )['total'] or 0
    
    # Agrupar ventas por numero_orden para mostrar como órdenes
    ordenes_dict = {}
    for venta in ventas_hoy:
        numero_orden = venta.numero_orden or f"Manual-{venta.id}"
        
        if numero_orden not in ordenes_dict:
            ordenes_dict[numero_orden] = {
                'numero_orden': numero_orden,
                'cliente_nombre': venta.cliente_nombre,
                'metodo_pago': venta.metodo_pago,
                'fecha': venta.fecha,
                'total': Decimal('0.00'),
                'cantidad_items': 0,
            }
        
        ordenes_dict[numero_orden]['total'] += venta.total
        ordenes_dict[numero_orden]['cantidad_items'] += venta.cantidad
    
    # Convertir a lista y ordenar por fecha descendente (más recientes primero)
    ordenes_list = list(ordenes_dict.values())
    ordenes_list.sort(key=lambda x: x['fecha'], reverse=True)
    
    # Ventas por producto
    ventas_por_producto = ventas_hoy.values(
        'producto__nombre',
        'producto__categoria'
    ).annotate(
        cantidad_total=Sum('cantidad'),
        total_producto=Sum('total')
    ).order_by('-total_producto')
    
    # Últimas 7 días para gráfico (incluyendo hoy)
    hace_7_dias = hoy - timedelta(days=6)  # 6 días atrás = últimos 7 días incluyendo hoy
    ventas_7_dias = Venta.objects.filter(
        tienda=tienda,
        fecha_venta__gte=hace_7_dias,
        fecha_venta__lte=hoy
    ).values('fecha_venta').annotate(
        total=Sum('total'),
        cantidad=Count('id')
    ).order_by('fecha_venta')
    
    context = {
        'tienda': tienda,
        'total_hoy': total_hoy,
        'cantidad_ventas_hoy': len(ordenes_list),  # Número de órdenes, no de items
        'total_productos_vendidos': total_productos_vendidos,  # Total de items/productos
        'ordenes': ordenes_list[:5],  # Últimas 5 órdenes para mostrar
        'ventas_hoy': ventas_hoy,
        'ventas_por_producto': ventas_por_producto,
        'ventas_7_dias': json.dumps([(str(v['fecha_venta']), float(v['total'])) for v in ventas_7_dias]),
        'rol': usuario_tienda.rol,
    }
    
    return render(request, 'tienda/dashboard.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def registrar_venta_view(request):
    """Vista para registrar una nueva venta."""
    try:
        usuario_tienda = request.user.usuario_tienda
        if usuario_tienda.rol != 'tienda':
            return redirect('admin-dashboard')
    except UsuarioTienda.DoesNotExist:
        return redirect('login')
    
    tienda = usuario_tienda.tienda
    
    # Ordenar productos por categoría personalizada: Papas, Salsas, Adiciones, Bebidas
    from django.db.models import Case, When, Value, IntegerField
    
    categoria_order = Case(
        When(categoria='papas', then=Value(0)),
        When(categoria='salsas', then=Value(1)),
        When(categoria='adiciones', then=Value(2)),
        When(categoria='bebidas', then=Value(3)),
        default=Value(4),
        output_field=IntegerField(),
    )
    
    productos = Producto.objects.filter(disponible=True).annotate(
        categoria_orden=categoria_order
    ).order_by('categoria_orden', 'nombre')
    
    # Agrupar productos por categoría en el orden correcto
    categorias_orden = ['Papas', 'Salsas', 'Adiciones', 'Bebidas']
    productos_agrupados = {}
    
    for categoria in categorias_orden:
        categoria_lower = categoria.lower()
        productos_agrupados[categoria] = [
            p for p in productos if p.get_categoria_display().lower() == categoria_lower
        ]
    
    if request.method == 'POST':
        try:
            # Obtener los datos del formulario
            productos_data = request.POST.get('productosData', '{}')
            metodo_pago = request.POST.get('metodo_pago', 'efectivo')
            fecha_venta_str = request.POST.get('fecha_venta')
            cliente_nombre = request.POST.get('cliente_nombre', 'Cliente').strip()
            
            logger.info(f"POST - Cliente: {cliente_nombre}, Método: {metodo_pago}, Fecha: {fecha_venta_str}")
            logger.info(f"POST - ProductosData: {productos_data}")
            
            # Validar método de pago
            if not metodo_pago:
                raise ValueError('Debes seleccionar un método de pago.')
            
            # Validar nombre del cliente
            if not cliente_nombre:
                raise ValueError('Debes ingresar el nombre del cliente.')
            
            # Parsear los productos JSON
            carrito = json.loads(productos_data)
            logger.info(f"Carrito parseado: {carrito}")
            
            if not carrito or len(carrito) == 0:
                raise ValueError('El carrito está vacío.')
            
            # Procesar la fecha
            if fecha_venta_str:
                fecha_venta = datetime.strptime(fecha_venta_str, '%Y-%m-%d').date()
            else:
                fecha_venta = timezone.now().date()
            
            logger.info(f"Fecha de venta: {fecha_venta}")
            
            # Generar número de orden único (timestamp + tienda ID)
            from time import time
            numero_orden = f"{tienda.id}-{int(time() * 1000)}"
            
            logger.info(f"Número de orden: {numero_orden}")
            
            # Crear una venta por cada producto en el carrito
            ventas_creadas = 0
            total_factura = Decimal('0')
            
            for producto_id, item_data in carrito.items():
                producto = get_object_or_404(Producto, id=int(producto_id))
                cantidad = int(item_data.get('cantidad', 1))
                precio_unitario = Decimal(str(item_data.get('precio', 0)))
                
                if cantidad <= 0:
                    raise ValueError(f'La cantidad de {producto.nombre} debe ser mayor a 0.')
                
                if precio_unitario <= 0:
                    raise ValueError(f'El precio de {producto.nombre} debe ser mayor a 0.')
                
                # Crear la venta con cliente_nombre y numero_orden
                venta = Venta.objects.create(
                    tienda=tienda,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=precio_unitario,
                    metodo_pago=metodo_pago,
                    registrado_por=request.user,
                    fecha_venta=fecha_venta,
                    cliente_nombre=cliente_nombre,
                    numero_orden=numero_orden,
                )
                
                logger.info(f"Venta creada: {venta.id} - {producto.nombre}")
                ventas_creadas += 1
                total_factura += (precio_unitario * cantidad)
            
            logger.info(f"Total de ventas creadas: {ventas_creadas}")
            # Redirigir con mensaje de éxito
            return redirect('tienda:tienda-dashboard')
        
        except (ValueError, TypeError, json.JSONDecodeError) as e:
            logger.error(f"Error registrando venta: {str(e)}")
            return render(request, 'tienda/registrar_venta.html', {
                'productos': productos,
                'categorias_orden': categorias_orden,
                'productos_agrupados': productos_agrupados,
                'error': f'Error en los datos: {str(e)}'
            })
    
    context = {
        'productos': productos,
        'categorias_orden': categorias_orden,
        'productos_agrupados': productos_agrupados,
        'hoy': timezone.now().date(),
        'rol': usuario_tienda.rol,
    }
    
    return render(request, 'tienda/registrar_venta.html', context)


@login_required(login_url='login')
def historial_ventas_view(request):
    """Vista para consultar el historial de ventas con filtros."""
    try:
        usuario_tienda = request.user.usuario_tienda
        if usuario_tienda.rol != 'tienda':
            return redirect('admin-dashboard')
    except UsuarioTienda.DoesNotExist:
        return redirect('login')
    
    tienda = usuario_tienda.tienda
    
    # Filtros
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    categoria = request.GET.get('categoria')
    
    ventas = Venta.objects.filter(tienda=tienda).select_related('producto')
    
    if fecha_desde:
        fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
        ventas = ventas.filter(fecha_venta__gte=fecha_desde_obj)
    
    if fecha_hasta:
        fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
        ventas = ventas.filter(fecha_venta__lte=fecha_hasta_obj)
    
    if categoria:
        ventas = ventas.filter(producto__categoria=categoria)
    
    # Agrupar ventas por numero_orden para mostrar órdenes completas
    ordenes_dict = {}
    total_general = Decimal('0.00')
    
    for venta in ventas:
        numero_orden = venta.numero_orden or f"Manual-{venta.id}"
        
        if numero_orden not in ordenes_dict:
            ordenes_dict[numero_orden] = {
                'numero_orden': numero_orden,
                'cliente_nombre': venta.cliente_nombre,
                'metodo_pago': venta.metodo_pago,
                'fecha_venta': venta.fecha_venta,
                'productos': [],
                'total': Decimal('0.00'),
            }
        
        # Agregar productos a la orden
        item_total = venta.precio_unitario * venta.cantidad
        ordenes_dict[numero_orden]['productos'].append({
            'nombre': venta.producto.nombre,
            'cantidad': venta.cantidad,
            'precio_unitario': venta.precio_unitario,
            'total': item_total,
        })
        ordenes_dict[numero_orden]['total'] += item_total
        total_general += item_total
    
    # Convertir a lista y ordenar por fecha
    ordenes_list = list(ordenes_dict.values())
    ordenes_list.sort(key=lambda x: x['fecha_venta'], reverse=True)
    
    categorias = Producto.objects.values_list('categoria', flat=True).distinct()
    
    # Obtener cierres de caja
    cierres_caja = CierreCaja.objects.filter(tienda=tienda).order_by('-fecha_cierre')
    
    if fecha_desde or fecha_hasta:
        if fecha_desde:
            fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
            cierres_caja = cierres_caja.filter(fecha_cierre__gte=fecha_desde_obj)
        
        if fecha_hasta:
            fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
            cierres_caja = cierres_caja.filter(fecha_cierre__lte=fecha_hasta_obj)
    
    context = {
        'ordenes': ordenes_list,
        'total_general': total_general,
        'cantidad_ordenes': len(ordenes_list),
        'cierres_caja': cierres_caja,
        'categorias': categorias,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'categoria_filtro': categoria,
        'tienda': tienda,
        'rol': usuario_tienda.rol,
    }
    
    return render(request, 'tienda/historial_ventas.html', context)


@login_required(login_url='login')
def catalogo_productos_view(request):
    """Vista para consultar el catálogo de productos disponibles."""
    try:
        usuario_tienda = request.user.usuario_tienda
        if usuario_tienda.rol != 'tienda':
            return redirect('admin-dashboard')
    except UsuarioTienda.DoesNotExist:
        return redirect('login')
    
    categoria_filtro = request.GET.get('categoria')
    productos = Producto.objects.filter(disponible=True)
    
    if categoria_filtro:
        productos = productos.filter(categoria=categoria_filtro)
    
    categorias = Producto.objects.values_list('categoria', flat=True).distinct()
    
    context = {
        'productos': productos,
        'categorias': categorias,
        'categoria_filtro': categoria_filtro,
        'rol': usuario_tienda.rol,
    }
    
    return render(request, 'tienda/catalogo_productos.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def cerrar_caja_view(request):
    """Vista para cerrar caja con resumen de pagos por método y validación de efectivo."""
    try:
        usuario_tienda = request.user.usuario_tienda
        if usuario_tienda.rol != 'tienda':
            return redirect('admin-dashboard')
    except UsuarioTienda.DoesNotExist:
        return redirect('login')
    
    tienda = usuario_tienda.tienda
    hoy = timezone.now().date()
    
    # Obtener todas las ventas del día
    ventas_hoy = Venta.objects.filter(
        tienda=tienda,
        fecha_venta=hoy
    ).select_related('producto').order_by('-fecha')
    
    # Agrupar ventas por método de pago
    resumen_pagos = ventas_hoy.values('metodo_pago').annotate(
        total=Sum('total'),
        cantidad=Count('id')
    ).order_by('metodo_pago')
    
    # Convertir a diccionario para fácil acceso
    resumen_dict = {
        'efectivo': {'total': Decimal('0.00'), 'cantidad': 0},
        'tarjeta_credito': {'total': Decimal('0.00'), 'cantidad': 0},
        'tarjeta_debito': {'total': Decimal('0.00'), 'cantidad': 0},
        'transferencia': {'total': Decimal('0.00'), 'cantidad': 0},
        'nequi': {'total': Decimal('0.00'), 'cantidad': 0},
        'otro': {'total': Decimal('0.00'), 'cantidad': 0},
    }
    
    for item in resumen_pagos:
        metodo = item['metodo_pago']
        resumen_dict[metodo] = {
            'total': item['total'],
            'cantidad': item['cantidad']
        }
    
    # Totales generales
    total_general = ventas_hoy.aggregate(total=Sum('total'))['total'] or Decimal('0.00')
    total_efectivo_esperado = resumen_dict['efectivo']['total']
    
    if request.method == 'POST':
        try:
            efectivo_contado = request.POST.get('efectivo_contado', '0')
            notas = request.POST.get('notas', '').strip()
            
            # Convertir a decimal
            efectivo_contado = Decimal(str(efectivo_contado))
            
            # Validar que sea un número positivo
            if efectivo_contado < 0:
                return render(request, 'tienda/cerrar_caja.html', {
                    'resumen_dict': resumen_dict,
                    'total_general': total_general,
                    'total_efectivo_esperado': total_efectivo_esperado,
                    'cantidad_ventas': ventas_hoy.count(),
                    'error': 'El monto contado debe ser un número positivo.'
                })
            
            # Calcular diferencia
            diferencia = efectivo_contado - total_efectivo_esperado
            
            # Intenta crear o actualizar el cierre de caja
            cierre_caja, created = CierreCaja.objects.update_or_create(
                tienda=tienda,
                fecha_cierre=hoy,
                defaults={
                    'total_efectivo_esperado': total_efectivo_esperado,
                    'total_efectivo_contado': efectivo_contado,
                    'diferencia_efectivo': diferencia,
                    'total_tarjeta_credito': resumen_dict['tarjeta_credito']['total'],
                    'total_tarjeta_debito': resumen_dict['tarjeta_debito']['total'],
                    'total_transferencia': resumen_dict['transferencia']['total'],
                    'total_nequi': resumen_dict['nequi']['total'],
                    'total_otro': resumen_dict['otro']['total'],
                    'total_general': total_general,
                    'cantidad_transacciones': ventas_hoy.count(),
                    'notas': notas if notas else None,
                    'registrado_por': request.user,
                }
            )
            
            accion = "registrado" if created else "actualizado"
            logger.info(f"Cierre de caja {accion}: {cierre_caja.id} - Tienda: {tienda.nombre} - Fecha: {hoy}")
            
            context = {
                'resumen_dict': resumen_dict,
                'total_general': total_general,
                'total_efectivo_esperado': total_efectivo_esperado,
                'cantidad_ventas': ventas_hoy.count(),
                'efectivo_contado': efectivo_contado,
                'diferencia': diferencia,
                'notas': notas,
                'cierre_completado': True,
                'hoy': hoy,
                'tienda': tienda,
                'rol': usuario_tienda.rol,
                'mensaje_exito': f'Cierre de caja {accion} correctamente',
            }
            
            return render(request, 'tienda/cerrar_caja.html', context)
        
        except (ValueError, TypeError, Decimal.InvalidOperation) as e:
            logger.error(f"Error al procesar cierre de caja: {str(e)}")
            return render(request, 'tienda/cerrar_caja.html', {
                'resumen_dict': resumen_dict,
                'total_general': total_general,
                'total_efectivo_esperado': total_efectivo_esperado,
                'cantidad_ventas': ventas_hoy.count(),
                'error': 'Error al procesar el monto de efectivo. Verifica que sea un número válido.'
            })
        except Exception as e:
            logger.error(f"Error inesperado al guardar cierre de caja: {str(e)}")
            return render(request, 'tienda/cerrar_caja.html', {
                'resumen_dict': resumen_dict,
                'total_general': total_general,
                'total_efectivo_esperado': total_efectivo_esperado,
                'cantidad_ventas': ventas_hoy.count(),
                'error': f'Error inesperado: {str(e)}'
            })
    
    context = {
        'resumen_dict': resumen_dict,
        'total_general': total_general,
        'total_efectivo_esperado': total_efectivo_esperado,
        'cantidad_ventas': ventas_hoy.count(),
        'tienda': tienda,
        'hoy': hoy,
        'rol': usuario_tienda.rol,
    }
    
    return render(request, 'tienda/cerrar_caja.html', context)


@login_required(login_url='login')
def reportes_view(request):
    """Vista de reportes para el administrador con cierres de caja de todas las sedes."""
    try:
        usuario_tienda = request.user.usuario_tienda
        if usuario_tienda.rol != 'administrador':
            return redirect('tienda:tienda-dashboard')
    except UsuarioTienda.DoesNotExist:
        return redirect('login')
    
    # Filtros
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    tienda_filtro = request.GET.get('tienda')
    
    # Obtener todos los cierres de caja
    cierres = CierreCaja.objects.all().select_related('tienda', 'registrado_por').order_by('-fecha_cierre')
    
    if fecha_desde:
        try:
            fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
            cierres = cierres.filter(fecha_cierre__gte=fecha_desde_obj)
        except ValueError:
            pass
    
    if fecha_hasta:
        try:
            fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
            cierres = cierres.filter(fecha_cierre__lte=fecha_hasta_obj)
        except ValueError:
            pass
    
    if tienda_filtro:
        cierres = cierres.filter(tienda__id=tienda_filtro)
    
    # Calcular totales y resumen
    resumen_general = {
        'total_efectivo_esperado': cierres.aggregate(Sum('total_efectivo_esperado'))['total_efectivo_esperado__sum'] or Decimal('0.00'),
        'total_efectivo_contado': cierres.aggregate(Sum('total_efectivo_contado'))['total_efectivo_contado__sum'] or Decimal('0.00'),
        'total_tarjeta_credito': cierres.aggregate(Sum('total_tarjeta_credito'))['total_tarjeta_credito__sum'] or Decimal('0.00'),
        'total_tarjeta_debito': cierres.aggregate(Sum('total_tarjeta_debito'))['total_tarjeta_debito__sum'] or Decimal('0.00'),
        'total_transferencia': cierres.aggregate(Sum('total_transferencia'))['total_transferencia__sum'] or Decimal('0.00'),
        'total_nequi': cierres.aggregate(Sum('total_nequi'))['total_nequi__sum'] or Decimal('0.00'),
        'total_otro': cierres.aggregate(Sum('total_otro'))['total_otro__sum'] or Decimal('0.00'),
        'total_general': cierres.aggregate(Sum('total_general'))['total_general__sum'] or Decimal('0.00'),
    }
    
    # Calcular diferencia total
    resumen_general['diferencia_total'] = resumen_general['total_efectivo_contado'] - resumen_general['total_efectivo_esperado']
    
    # Obtener todas las tiendas para el filtro
    tiendas = Tienda.objects.all()
    
    context = {
        'cierres': cierres,
        'resumen': resumen_general,
        'tiendas': tiendas,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'tienda_filtro': tienda_filtro,
        'cantidad_cierres': cierres.count(),
        'rol': usuario_tienda.rol,
    }
    
    return render(request, 'tienda/reportes.html', context)


# ============= VISTAS DE INVENTARIO =============

@login_required(login_url='login')
def inventario_view(request):
    """Vista del inventario con stock actual de los productos de la tienda."""
    try:
        usuario_tienda = request.user.usuario_tienda
    except UsuarioTienda.DoesNotExist:
        return redirect('login')
    
    # Si es administrador, redirigir a su vista consolidada
    if usuario_tienda.rol == 'administrador':
        return redirect('admin_panel:admin-inventario')
    
    tienda = usuario_tienda.tienda
    
    # Obtener todos los stocks asociados a esta tienda
    stocks = StockActual.objects.filter(tienda=tienda).select_related('producto').order_by('producto__categoria', 'producto__nombre')
    
    # Filtro por estado de stock
    filtro_estado = request.GET.get('estado', '')
    if filtro_estado:
        if filtro_estado == 'bajo':
            stocks = stocks.filter(cantidad__gt=0, cantidad__lt=F('stock_minimo'))
        elif filtro_estado == 'agotado':
            stocks = stocks.filter(cantidad=0)
        elif filtro_estado == 'normal':
            stocks = stocks.filter(cantidad__gte=F('stock_minimo'))
    
    # Agrupar por categoría
    from itertools import groupby
    stocks_list = list(stocks)
    stocks_por_categoria = {}
    for categoria, items in groupby(stocks_list, key=lambda x: x.producto.get_categoria_display()):
        stocks_por_categoria[categoria] = list(items)
    
    # Calcular totales
    total_productos = stocks.count()
    productos_bajo_stock = stocks.filter(cantidad__lt=F('stock_minimo')).count()
    productos_agotados = stocks.filter(cantidad=0).count()
    
    context = {
        'tienda': tienda,
        'stocks': stocks,
        'stocks_por_categoria': stocks_por_categoria,
        'total_productos': total_productos,
        'productos_bajo_stock': productos_bajo_stock,
        'productos_agotados': productos_agotados,
        'filtro_estado': filtro_estado,
        'rol': usuario_tienda.rol,
    }
    
    return render(request, 'tienda/inventario.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def entrada_producto_view(request):
    """Vista para registrar entrada de productos al inventario."""
    try:
        usuario_tienda = request.user.usuario_tienda
    except UsuarioTienda.DoesNotExist:
        return redirect('login')
    
    # Solo tiendas acceden aquí, admins van a su vista
    if usuario_tienda.rol == 'administrador':
        return redirect('admin_panel:admin-inventario')
    
    tienda = usuario_tienda.tienda
    
    if request.method == 'POST':
        form = MovimientoInventarioEntradaForm(request.POST)
        if form.is_valid():
            try:
                movimiento = form.save(commit=False)
                movimiento.tienda = tienda
                movimiento.tipo_movimiento = 'entrada'
                movimiento.registrado_por = request.user
                movimiento.save()
                
                logger.info(f"Entrada registrada: {movimiento.id} - {movimiento.producto.nombre} - Cantidad: {movimiento.cantidad}")
                
                return redirect('tienda:inventario')
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
def salida_producto_view(request):
    """Vista para registrar salida de productos del inventario."""
    try:
        usuario_tienda = request.user.usuario_tienda
    except UsuarioTienda.DoesNotExist:
        return redirect('login')
    
    # Solo tiendas acceden aquí, admins van a su vista
    if usuario_tienda.rol == 'administrador':
        return redirect('admin_panel:admin-inventario')
    
    tienda = usuario_tienda.tienda
    
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
                    
                    logger.info(f"Salida registrada: {movimiento.id} - {movimiento.producto.nombre} - Cantidad: {movimiento.cantidad}")
                    
                    return redirect('tienda:inventario')
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
def historial_movimientos_view(request):
    """Vista del historial de movimientos de inventario."""
    try:
        usuario_tienda = request.user.usuario_tienda
    except UsuarioTienda.DoesNotExist:
        return redirect('login')
    
    # Solo tiendas ven historial, admins van a su vista
    if usuario_tienda.rol == 'administrador':
        return redirect('admin_panel:admin-inventario')
    
    tienda = usuario_tienda.tienda
    
    # Obtener movimientos
    movimientos = MovimientoInventario.objects.filter(tienda=tienda).select_related('producto', 'registrado_por').order_by('-fecha_movimiento')
    
    # Filtros
    filtro_tipo = request.GET.get('tipo', '')
    filtro_producto = request.GET.get('producto', '')
    filtro_fecha_desde = request.GET.get('fecha_desde', '')
    filtro_fecha_hasta = request.GET.get('fecha_hasta', '')
    
    if filtro_tipo:
        movimientos = movimientos.filter(tipo_movimiento=filtro_tipo)
    
    if filtro_producto:
        movimientos = movimientos.filter(producto__id=filtro_producto)
    
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
    
    # Obtener lista de productos para el filtro
    productos = Producto.objects.filter(disponible=True).order_by('categoria', 'nombre')
    
    context = {
        'tienda': tienda,
        'movimientos': page.object_list,
        'page': page,
        'productos': productos,
        'filtro_tipo': filtro_tipo,
        'filtro_producto': filtro_producto,
        'filtro_fecha_desde': filtro_fecha_desde,
        'filtro_fecha_hasta': filtro_fecha_hasta,
        'total_movimientos': paginator.count,
        'rol': usuario_tienda.rol,
    }
    
    return render(request, 'tienda/historial_movimientos.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def ajuste_stock_view(request):
    """Vista para hacer ajustes manuales al stock."""
    try:
        usuario_tienda = request.user.usuario_tienda
        if usuario_tienda.rol != 'administrador':
            return redirect('tienda:tienda-dashboard')
    except UsuarioTienda.DoesNotExist:
        return redirect('login')
    
    tienda_id = request.GET.get('tienda') or request.POST.get('tienda')
    if not tienda_id:
        # Si no hay tienda especificada, solo admin puede ver todas
        tiendas = Tienda.objects.all()
    else:
        tiendas = Tienda.objects.filter(id=tienda_id)
    
    if request.method == 'POST':
        tienda = get_object_or_404(Tienda, id=request.POST.get('tienda'))
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
                
                logger.info(f"Ajuste de stock realizado: {movimiento.id} - {producto.nombre} - Nueva cantidad: {nueva_cantidad}")
                
                return redirect('admin_panel:admin-inventario')
            except Exception as e:
                logger.error(f"Error al ajustar stock: {str(e)}")
                form.add_error(None, f"Error al ajustar el stock: {str(e)}")
    else:
        form = AjusteStockForm()
    
    context = {
        'form': form,
        'tiendas': tiendas,
        'tienda_id': tienda_id,
        'titulo': 'Ajustar Stock',
        'rol': usuario_tienda.rol,
    }
    
    return render(request, 'tienda/ajuste_stock.html', context)
