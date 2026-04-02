#!/usr/bin/env python
"""
Script para limpiar y repoblar la base de datos con el catálogo real de CityPapa.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'citypapa.settings')
django.setup()

from tienda.models import Tienda, Producto, UsuarioTienda, Venta
from django.contrib.auth.models import User
from decimal import Decimal

# Limpiar toda la base de datos (excepto superusuario)
print("Limpiando datos anteriores...")
Venta.objects.all().delete()
print("✓ Ventas eliminadas")

Producto.objects.all().delete()
print("✓ Productos eliminados")

UsuarioTienda.objects.all().delete()
print("✓ Usuarios de tienda eliminados")

Tienda.objects.all().delete()
print("✓ Tiendas eliminadas")

# Recrear tiendas
tiendas = [
    {'nombre': 'CityPapa Bogotá', 'ciudad': 'Bogotá', 'direccion': 'Carrera 7 # 120', 'telefono': '3022746964'},
    {'nombre': 'CityPapa Medellín', 'ciudad': 'Medellín', 'direccion': 'Calle 50 # 45', 'telefono': '3043355147'},
    {'nombre': 'CityPapa Cali', 'ciudad': 'Cali', 'direccion': 'Avenida 6 # 30', 'telefono': '3023456789'},
]

for tienda_data in tiendas:
    Tienda.objects.create(activa=True, **tienda_data)

print("✓ Tiendas creadas")

# Recrear usuarios
admin_user = User.objects.get(username='admin')
UsuarioTienda.objects.create(usuario=admin_user, tienda=None, rol='administrador', activo=True)

for i in range(1, 4):
    try:
        user = User.objects.get(username=f'tienda{i}')
        tienda = Tienda.objects.get(id=i) if i <= 3 else None
        UsuarioTienda.objects.create(usuario=user, tienda=tienda, rol='tienda', activo=True)
    except (User.DoesNotExist, Tienda.DoesNotExist):
        pass

print("✓ Usuarios configurados")

# PRODUCTOS DEL CATÁLOGO REAL CON DESCRIPCIONES
productos = [
    # ========== PAPAS PRINCIPALES ==========
    {'nombre': 'Papas Cosmopolitan', 'precio': Decimal('15000'), 'categoria': 'papas', 'descripcion': 'Papas rústicas 450gr con salsa de la casa y queso mozzarella derretido', 'disponible': True},
    {'nombre': 'Papas Napoles', 'precio': Decimal('16000'), 'categoria': 'papas', 'descripcion': 'Papa rústica 250gr, salsa rosada, salchicha y huevos de codorniz', 'disponible': True},
    {'nombre': 'Papas Tennesse', 'precio': Decimal('27000'), 'categoria': 'papas', 'descripcion': 'Papas 450gr con pulled pork desmechado, queso, salsa BBQ y cebolla verde', 'disponible': True},
    {'nombre': 'Papas Munich', 'precio': Decimal('27000'), 'categoria': 'papas', 'descripcion': 'Papas 450gr con salchicha americana, huevos de codorniz, queso y tocinta', 'disponible': True},
    {'nombre': 'Papas Medellín', 'precio': Decimal('28000'), 'categoria': 'papas', 'descripcion': 'Papas 450gr con plátano maduro, guacamole, chicharrón y huevo de codorniz', 'disponible': True},
    {'nombre': 'Papas La Habana', 'precio': Decimal('28000'), 'categoria': 'papas', 'descripcion': 'Papas 450gr con milanesa verde, queso, chicharrón y chorizo coctel', 'disponible': True},
    {'nombre': 'Papas Barahona', 'precio': Decimal('28000'), 'categoria': 'papas', 'descripcion': 'Papas 450gr con papa vieja (cerdo desmechado), queso crema y salsa dulce', 'disponible': True},
    {'nombre': 'Papas Palermo', 'precio': Decimal('30000'), 'categoria': 'papas', 'descripcion': 'Papas 450gr con lomo de cerdo, pico de gallo, chorizo y mayonesa chimichurri', 'disponible': True},
    {'nombre': 'Papas Milwaukee', 'precio': Decimal('30000'), 'categoria': 'papas', 'descripcion': 'Papas 450gr con salchicha cervecera, tocinta y salsa ranch', 'disponible': True},
    {'nombre': 'Papas New York', 'precio': Decimal('30000'), 'categoria': 'papas', 'descripcion': 'Papas 450gr con milanesa de pollo, mermelada de tocinta y salsa ranch', 'disponible': True},
    {'nombre': 'Papas Tijuana', 'precio': Decimal('31000'), 'categoria': 'papas', 'descripcion': 'Papas 450gr con picante (cerdo), guacamole, queso y mayo de pimientos asados', 'disponible': True},
    {'nombre': 'Papas Jalisco', 'precio': Decimal('29000'), 'categoria': 'papas', 'descripcion': 'Papas 450gr con pulled pork picante, guacamole, salsa sriracha y cebolla verde', 'disponible': True},
    {'nombre': 'Papas Daytona', 'precio': Decimal('29000'), 'categoria': 'papas', 'descripcion': 'Papas 450gr con alitas crocantes en salsa picante Daytona y queso crema', 'disponible': True},
    {'nombre': 'Papas Kentucky', 'precio': Decimal('29000'), 'categoria': 'papas', 'descripcion': 'Papas 450gr con pollo frito, mayo cilantro, arvejas y tomate', 'disponible': True},
    {'nombre': 'Papas Milán', 'precio': Decimal('30000'), 'categoria': 'papas', 'descripcion': 'Papas 450gr con crispetas de pollo, tocinta, maíz dulce y mayo pesto', 'disponible': True},
    {'nombre': 'Papas Barcelona', 'precio': Decimal('30000'), 'categoria': 'papas', 'descripcion': 'Papas 450gr con costilla ahumada, jardín fresco, tocinta crocante y BBQ', 'disponible': True},
    {'nombre': 'Papas Miami', 'precio': Decimal('31000'), 'categoria': 'papas', 'descripcion': 'Papas 450gr con camarones fritos, pico de gallo, guacamole y salsa sriracha', 'disponible': True},

    # ========== ADICIONES ==========
    {'nombre': 'Camarones apanados', 'precio': Decimal('11500'), 'categoria': 'adiciones', 'descripcion': 'Camarones frescos rebozados y fritos hasta estar crujientes', 'disponible': True},
    {'nombre': 'Milanesa de pollo', 'precio': Decimal('11500'), 'categoria': 'adiciones', 'descripcion': 'Filete de pollo empanizado y frito, tierno y jugoso', 'disponible': True},
    {'nombre': 'Alitas x4', 'precio': Decimal('11500'), 'categoria': 'adiciones', 'descripcion': '4 alitas de pollo crocantes y sazonadas', 'disponible': True},
    {'nombre': 'Costillas', 'precio': Decimal('11500'), 'categoria': 'adiciones', 'descripcion': 'Costillas ahumadas lentamente con especias', 'disponible': True},
    {'nombre': 'Pulled Pork', 'precio': Decimal('9500'), 'categoria': 'adiciones', 'descripcion': 'Cerdo desmechado lentamente cocido, suave y sabroso', 'disponible': True},
    {'nombre': 'Crispetas de pollo', 'precio': Decimal('9500'), 'categoria': 'adiciones', 'descripcion': 'Pollo rebozado y frito en pequeños trozos crujientes', 'disponible': True},
    {'nombre': 'Trozos tomo de cerdo', 'precio': Decimal('9500'), 'categoria': 'adiciones', 'descripcion': 'Trozos de carne de cerdo frita sazonada', 'disponible': True},
    {'nombre': 'Chicharrón', 'precio': Decimal('8500'), 'categoria': 'adiciones', 'descripcion': 'Chicharrón crocante y dorado', 'disponible': True},
    {'nombre': 'Chorizos Cóctel', 'precio': Decimal('7500'), 'categoria': 'adiciones', 'descripcion': 'Chorizos pequeños cosidos, perfectos para picar', 'disponible': True},
    {'nombre': 'Salchicha', 'precio': Decimal('7500'), 'categoria': 'adiciones', 'descripcion': 'Salchicha de cerdo frita', 'disponible': True},
    {'nombre': 'Mermelada de tocinta', 'precio': Decimal('6500'), 'categoria': 'adiciones', 'descripcion': 'Tocinta caramelizada y dulce', 'disponible': True},
    {'nombre': 'Queso Mozzarella', 'precio': Decimal('6500'), 'categoria': 'adiciones', 'descripcion': 'Queso mozzarella derretido sobre las papas', 'disponible': True},
    {'nombre': 'Huevos de codorniz', 'precio': Decimal('5500'), 'categoria': 'adiciones', 'descripcion': 'Huevos fritos de codorniz, tiernos y sabrosos', 'disponible': True},
    {'nombre': 'Tocinta', 'precio': Decimal('6500'), 'categoria': 'adiciones', 'descripcion': 'Tocinta frita crujiente y dorada', 'disponible': True},
    {'nombre': 'Morella Cóctel', 'precio': Decimal('6500'), 'categoria': 'adiciones', 'descripcion': 'Morella cocida y frita en trozos pequeños', 'disponible': True},
    {'nombre': 'Jalapeños', 'precio': Decimal('8000'), 'categoria': 'adiciones', 'descripcion': 'Jalapeños encurtidos para darle ese toque picante', 'disponible': True},
    {'nombre': 'Pico de gallo', 'precio': Decimal('3000'), 'categoria': 'adiciones', 'descripcion': 'Tomate, cebolla y cilantro picado fresco', 'disponible': True},
    {'nombre': 'Plátano maduro', 'precio': Decimal('3000'), 'categoria': 'adiciones', 'descripcion': 'Plátano frito dulce y suave', 'disponible': True},
    {'nombre': 'Malcitos', 'precio': Decimal('3500'), 'categoria': 'adiciones', 'descripcion': 'Maíz frito crocante', 'disponible': True},
    {'nombre': 'Salchicha crocante', 'precio': Decimal('7500'), 'categoria': 'adiciones', 'descripcion': 'Salchicha extra crocante y sazonada', 'disponible': True},
    {'nombre': 'Salchicha salvaje', 'precio': Decimal('7500'), 'categoria': 'adiciones', 'descripcion': 'Salchicha ahumada con sabor especial', 'disponible': True},

    # ========== SALSAS ==========
    {'nombre': 'Salsa Daytona', 'precio': Decimal('2500'), 'categoria': 'salsas', 'descripcion': 'Salsa picante con toque ahumado', 'disponible': True},
    {'nombre': 'Salsa de Sriracha Dulce', 'precio': Decimal('2500'), 'categoria': 'salsas', 'descripcion': 'Sriracha con balance perfecto de picante y dulce', 'disponible': True},
    {'nombre': 'Salsa de Tocino Picante', 'precio': Decimal('2500'), 'categoria': 'salsas', 'descripcion': 'Salsa con tocino crujiente y sabor picante', 'disponible': True},
    {'nombre': 'Mayonesa de Cilantro', 'precio': Decimal('2500'), 'categoria': 'salsas', 'descripcion': 'Mayonesa casera con cilantro fresco', 'disponible': True},
    {'nombre': 'Mayonesa Verde', 'precio': Decimal('2500'), 'categoria': 'salsas', 'descripcion': 'Mayonesa con hierbas verdes frescas', 'disponible': True},
    {'nombre': 'BBQ Budweiser', 'precio': Decimal('2500'), 'categoria': 'salsas', 'descripcion': 'Salsa BBQ con cerveza Budweiser', 'disponible': True},
    {'nombre': 'Salsa de la casa', 'precio': Decimal('2500'), 'categoria': 'salsas', 'descripcion': 'Receta secreta con toques especiales CityPapa', 'disponible': True},
    {'nombre': 'Salsa de Aguacate', 'precio': Decimal('2500'), 'categoria': 'salsas', 'descripcion': 'Guacamole fresco preparado diariamente', 'disponible': True},
    {'nombre': 'Salsa Cosmopolita', 'precio': Decimal('2500'), 'categoria': 'salsas', 'descripcion': 'Salsa gourmet con toque sofisticado', 'disponible': True},
    {'nombre': 'Mayonesa de Chimichurri', 'precio': Decimal('2500'), 'categoria': 'salsas', 'descripcion': 'Mayonesa con especias y chimichurri argentino', 'disponible': True},
    {'nombre': 'Mayonesa de Pesto', 'precio': Decimal('2500'), 'categoria': 'salsas', 'descripcion': 'Mayonesa italiana con pesto fresco', 'disponible': True},
    {'nombre': 'Salsa de Maíz y Tocino', 'precio': Decimal('2500'), 'categoria': 'salsas', 'descripcion': 'Salsa dulce con maíz tierno y tocinta caramelizada', 'disponible': True},
    {'nombre': 'Salsa Ranch', 'precio': Decimal('2500'), 'categoria': 'salsas', 'descripcion': 'Salsa ranch americana fresca y deliciosa', 'disponible': True},
    {'nombre': 'Queso Cheddar', 'precio': Decimal('2500'), 'categoria': 'salsas', 'descripcion': 'Salsa de queso cheddar derretido', 'disponible': True},

    # ========== BEBIDAS ==========
    {'nombre': 'Gaseosa Personal', 'precio': Decimal('4000'), 'categoria': 'bebidas', 'descripcion': 'Gaseosa 350ml fría y refrescante', 'disponible': True},
    {'nombre': 'Gaseosa 1.5L', 'precio': Decimal('9000'), 'categoria': 'bebidas', 'descripcion': 'Botella de 1.5 litros para compartir', 'disponible': True},
    {'nombre': 'Agua', 'precio': Decimal('4000'), 'categoria': 'bebidas', 'descripcion': 'Agua embotellada 500ml', 'disponible': True},
    {'nombre': 'Mr. Tea', 'precio': Decimal('5000'), 'categoria': 'bebidas', 'descripcion': 'Té helado refrescante Mr. Tea', 'disponible': True},
    {'nombre': 'Costerita', 'precio': Decimal('5000'), 'categoria': 'bebidas', 'descripcion': 'Cerveza Costerita 350ml', 'disponible': True},
    {'nombre': 'Jugo Hit', 'precio': Decimal('5000'), 'categoria': 'bebidas', 'descripcion': 'Jugo natural Hit 300ml', 'disponible': True},
]

for prod in productos:
    Producto.objects.create(**prod)

print(f"✓ Se crearon {len(productos)} productos")
print(f"\nResumen:")
print(f"  - Papas: {Producto.objects.filter(categoria='papas').count()}")
print(f"  - Adiciones: {Producto.objects.filter(categoria='adiciones').count()}")
print(f"  - Salsas: {Producto.objects.filter(categoria='salsas').count()}")
print(f"  - Bebidas: {Producto.objects.filter(categoria='bebidas').count()}")
print(f"\n✓ Base de datos lista para registrar ventas")
