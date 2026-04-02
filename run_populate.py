#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'citypapa.settings')
django.setup()

from django.contrib.auth.models import User
from tienda.models import Tienda, Producto, UsuarioTienda, Venta
from datetime import datetime, timedelta
from decimal import Decimal
import random

print("=" * 60)
print("CREANDO DATOS DE PRUEBA PARA CITYPAPA")
print("=" * 60)

# Limpiar
print("\n1. Limpiando datos existentes...")
Venta.objects.all().delete()
UsuarioTienda.objects.all().delete()
User.objects.filter(username__startswith='tienda').delete()
Tienda.objects.all().delete()
Producto.objects.all().delete()

# Admin
print("\n2. Creando administrador...")
admin, created = User.objects.get_or_create(username='admin')
if created:
    admin.set_password('admin123')
    admin.email = 'admin@citypapa.com'
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()
    print(f"   ✓ Admin: admin / admin123")
else:
    print(f"   ✓ Admin ya existe: admin / admin123")

# Tiendas
print("\n3. Creando tiendas...")
tiendas = []
ciudades = ['Bogotá', 'Medellín', 'Cali']
for i, ciudad in enumerate(ciudades, 1):
    tienda = Tienda.objects.create(
        nombre=f'CityPapa {ciudad}',
        direccion=f'Calle {i} #{i}-{i}',
        ciudad=ciudad,
        telefono=f'(+57) 1 {i}234{i}678',
        email=f'tienda{i}@citypapa.com',
        activa=True,
    )
    tiendas.append(tienda)
    print(f"   ✓ {tienda.nombre}")

# Categorías de productos
print("\n4. Creando productos...")
categorias_productos = {
    'hamburguesa': [
        ('Hamburguesa Clásica', Decimal('12.99')),
        ('Hamburguesa CityPapa', Decimal('15.99')),
        ('Doble Hamburguesa', Decimal('18.99')),
        ('Hamburguesa BBQ', Decimal('16.99')),
    ],
    'arepa': [
        ('Arepa Reina', Decimal('8.99')),
        ('Arepa de Queso', Decimal('7.99')),
        ('Arepa Mixta', Decimal('10.99')),
    ],
    'perro': [
        ('Perro Caliente', Decimal('6.99')),
        ('Perro Especial', Decimal('9.99')),
    ],
    'pizza': [
        ('Pizza Margarita', Decimal('14.99')),
        ('Pizza Pepperoni', Decimal('15.99')),
        ('Pizza Hawaiana', Decimal('16.99')),
    ],
    'bebida': [
        ('Gaseosa 350ml', Decimal('2.99')),
        ('Jugo Natural', Decimal('3.99')),
        ('Agua Embotellada', Decimal('1.99')),
        ('Cerveza', Decimal('5.99')),
    ],
    'postre': [
        ('Helado', Decimal('4.99')),
        ('Brownie', Decimal('5.99')),
        ('Pastel de Chocolate', Decimal('6.99')),
    ],
}

productos_dict = {}
for categoria, items in categorias_productos.items():
    for nombre, precio in items:
        producto = Producto.objects.create(
            nombre=nombre,
            descripcion=f'{nombre} delicioso de CityPapa',
            precio=precio,
            categoria=categoria,
            disponible=True,
        )
        productos_dict[nombre] = producto
print(f"   ✓ {Producto.objects.count()} productos creados")

# Usuarios Tienda
print("\n5. Creando usuarios de tiendas...")
for i, tienda in enumerate(tiendas, 1):
    usuario = User.objects.create_user(
        username=f'tienda{i}',
        email=f'tienda{i}@citypapa.com',
        password=f'tienda{i}123',
        first_name=f'Tienda {tienda.ciudad}',
    )
    UsuarioTienda.objects.create(
        usuario=usuario,
        tienda=tienda,
        rol='tienda',
        activo=True,
    )
    print(f"   ✓ tienda{i} / tienda{i}123")

# Ventas
print("\n6. Creando ventas (últimos 7 días)...")
hoy = datetime.now().date()
productos_lista = list(productos_dict.values())

for dia_offset in range(7):
    fecha = hoy - timedelta(days=dia_offset)
    
    for tienda in tiendas:
        num_ventas = random.randint(5, 15)
        
        for _ in range(num_ventas):
            producto = random.choice(productos_lista)
            cantidad = random.randint(1, 5)
            precio_unitario = producto.precio
            
            Venta.objects.create(
                tienda=tienda,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=precio_unitario,
                registrado_por=User.objects.get(username=f'tienda{tiendas.index(tienda) + 1}'),
                fecha_venta=fecha,
            )
    
    print(f"   ✓ {fecha.strftime('%d/%m/%Y')}")

print("\n" + "=" * 60)
print("RESUMEN:")
print("=" * 60)
print(f"✓ Tiendas: {Tienda.objects.count()}")
print(f"✓ Productos: {Producto.objects.count()}")
print(f"✓ Usuarios: {User.objects.count()}")
print(f"✓ Ventas: {Venta.objects.count()}")
print("\n✓ ¡Datos de prueba creados correctamente!")
print("=" * 60)
