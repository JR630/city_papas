"""
Script para poblar la base de datos con datos de prueba.

Ejecución:
    python manage.py shell < populate_db.py

O interactivamente en el shell de Django:
    python manage.py shell
    >>> exec(open('populate_db.py').read())
"""

from django.contrib.auth.models import User
from tienda.models import Tienda, Producto, UsuarioTienda, Venta
from datetime import datetime, timedelta
from decimal import Decimal
import random


def crear_datos_prueba():
    print("=" * 60)
    print("CREANDO DATOS DE PRUEBA PARA CITYPAPA")
    print("=" * 60)
    
    # Limpiar datos existentes
    print("\n1. Limpiando datos existentes...")
    Venta.objects.all().delete()
    UsuarioTienda.objects.all().delete()
    User.objects.filter(username__startswith='admin_', username__endswith='_test').delete()
    User.objects.filter(username__startswith='tienda_').delete()
    Tienda.objects.all().delete()
    Producto.objects.all().delete()
    
    # Crear productos
    print("\n2. Creando catálogo de productos...")
    categorias_productos = {
        'hamburguesa': [
            {'nombre': 'Hamburguesa Clásica', 'precio': Decimal('12.99')},
            {'nombre': 'Hamburguesa CityPapa', 'precio': Decimal('15.99')},
            {'nombre': 'Doble Hamburguesa', 'precio': Decimal('18.99')},
            {'nombre': 'Hamburguesa BBQ', 'precio': Decimal('16.99')},
        ],
        'arepa': [
            {'nombre': 'Arepa Reina', 'precio': Decimal('8.99')},
            {'nombre': 'Arepa de Queso', 'precio': Decimal('7.99')},
            {'nombre': 'Arepa Mixta', 'precio': Decimal('10.99')},
        ],
        'perro': [
            {'nombre': 'Perro Caliente', 'precio': Decimal('6.99')},
            {'nombre': 'Perro Especial', 'precio': Decimal('9.99')},
        ],
        'pizza': [
            {'nombre': 'Pizza Personal', 'precio': Decimal('13.99')},
            {'nombre': 'Pizza Mediana', 'precio': Decimal('19.99')},
            {'nombre': 'Pizza Grande', 'precio': Decimal('24.99')},
        ],
        'bebida': [
            {'nombre': 'Gaseosa Pequeña', 'precio': Decimal('2.99')},
            {'nombre': 'Gaseosa Grande', 'precio': Decimal('3.99')},
            {'nombre': 'Jugo Natural', 'precio': Decimal('4.99')},
            {'nombre': 'Cerveza', 'precio': Decimal('5.99')},
        ],
        'postre': [
            {'nombre': 'Postre del Día', 'precio': Decimal('5.99')},
            {'nombre': 'Helado', 'precio': Decimal('3.99')},
        ],
    }
    
    productos_dict = {}
    for categoria, items in categorias_productos.items():
        for item in items:
            producto = Producto.objects.create(
                nombre=item['nombre'],
                descripcion=f"Delicioso {item['nombre'].lower()} de CityPapa",
                precio=item['precio'],
                categoria=categoria,
                disponible=True,
            )
            productos_dict[item['nombre']] = producto
            print(f"   ✓ {producto.nombre} - ${producto.precio}")
    
    # Crear administrador
    print("\n3. Creando usuario administrador...")
    admin_user = User.objects.create_superuser(
        username='admin',
        email='admin@citypapa.com',
        password='admin123'
    )
    UsuarioTienda.objects.create(
        usuario=admin_user,
        tienda=None,
        rol='administrador',
        activo=True,
    )
    print(f"   ✓ Usuario: admin | Contraseña: admin123")
    
    # Crear tiendas
    print("\n4. Creando sucursales...")
    ciudades = ['Bogotá', 'Medellín', 'Cali']
    direcciones = {
        'Bogotá': 'Carrera 7 #123, Centro',
        'Medellín': 'Avenida La Playa #456',
        'Cali': 'Avenida Chile #789',
    }
    
    tiendas = []
    for i, ciudad in enumerate(ciudades, 1):
        tienda = Tienda.objects.create(
            nombre=f'CityPapa {ciudad}',
            ciudad=ciudad,
            direccion=direcciones[ciudad],
            telefono=f'+57 {310 + i}000{1000 + i}',
            email=f'tienda{i}@citypapa.com',
            activa=True,
        )
        tiendas.append(tienda)
        print(f"   ✓ {tienda.nombre} - {tienda.ciudad}")
        
        # Crear usuarios para cada tienda
        usuario = User.objects.create_user(
            username=f'tienda{i}',
            email=f'tienda{i}@citypapa.com',
            password=f'tienda{i}123',
            first_name=f'Tienda {ciudad}',
        )
        UsuarioTienda.objects.create(
            usuario=usuario,
            tienda=tienda,
            rol='tienda',
            activo=True,
        )
        print(f"      Usuario: tienda{i} | Contraseña: tienda{i}123")
    
    # Crear ventas de prueba (últimos 7 días)
    print("\n5. Creando datos de ventas (últimos 7 días)...")
    hoy = datetime.now().date()
    productos_lista = list(productos_dict.values())
    
    for dia_offset in range(7):
        fecha = hoy - timedelta(days=dia_offset)
        
        # Crear 5-15 ventas por tienda por día
        for tienda in tiendas:
            num_ventas = random.randint(5, 15)
            
            for _ in range(num_ventas):
                producto = random.choice(productos_lista)
                cantidad = random.randint(1, 5)
                precio_unitario = producto.precio
                
                venta = Venta.objects.create(
                    tienda=tienda,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=precio_unitario,
                    registrado_por=User.objects.get(username=f'tienda{tiendas.index(tienda) + 1}'),
                    fecha_venta=fecha,
                )
        
        print(f"   ✓ {fecha.strftime('%d/%m/%Y')} - Ventas registradas")
    
    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE DATOS CREADOS")
    print("=" * 60)
    print(f"✓ Tiendas: {Tienda.objects.count()}")
    print(f"✓ Productos: {Producto.objects.count()}")
    print(f"✓ Usuarios: {User.objects.count()}")
    print(f"✓ Ventas: {Venta.objects.count()}")
    print("\nCUENTAS DE PRUEBA:")
    print("─" * 60)
    print("ADMINISTRADOR:")
    print("  Usuario: admin")
    print("  Contraseña: admin123")
    print("  URL: http://localhost:8000/admin-panel/dashboard/")
    print("\nTIENDAS:")
    for i in range(1, 4):
        print(f"  Usuario: tienda{i}")
        print(f"  Contraseña: tienda{i}123")
        print(f"  URL: http://localhost:8000/tienda/dashboard/")
    print("─" * 60)
    print("\n✓ ¡Datos de prueba creados correctamente!")
    print("=" * 60)


if __name__ == '__main__':
    crear_datos_prueba()
