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

from .models import Tienda, Producto, UsuarioTienda, Venta, CierreCaja

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
    productos = Producto.objects.filter(disponible=True)
    
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
                'error': f'Error en los datos: {str(e)}'
            })
    
    context = {
        'productos': productos,
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
