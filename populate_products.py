#!/usr/bin/env python
"""
Script para poblar la base de datos con los productos del catálogo de CityPapa.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'citypapa.settings')
django.setup()

from tienda.models import Producto
from decimal import Decimal

# Limpiar productos existentes
Producto.objects.all().delete()

# PRODUCTOS: Lista de todas las papas, adiciones, salsas y bebidas
productos = [
    # ========== PAPAS PRINCIPALES ==========
    {
        'nombre': 'Papas Cosmopolitan',
        'precio': Decimal('15000'),
        'categoria': 'papas',
        'descripcion': 'Papas rústicas 450 gr, salsa de la casa y queso mozzarella',
        'disponible': True,
    },
    {
        'nombre': 'Papas Napoles',
        'precio': Decimal('16000'),
        'categoria': 'papas',
        'descripcion': 'Papa rústica 250 gr, salsa de la casa, salsa rosada, salchicha, huevos de codorniz',
        'disponible': True,
    },
    {
        'nombre': 'Papas Tennesse',
        'precio': Decimal('27000'),
        'categoria': 'papas',
        'descripcion': 'Papas rústicas 450 gr, pulled pork (cerdo desmechado), salsa de la casa, queso mozzarella, BBQ budweiser, queso crema, tomate verde',
        'disponible': True,
    },
    {
        'nombre': 'Papas Munich',
        'precio': Decimal('27000'),
        'categoria': 'papas',
        'descripcion': 'Papas rústicas 450 gr, queso mozzarella, salchicha americana, salsa cosmopolita, huevos de codorniz, tocinta, cebollín, tomate',
        'disponible': True,
    },
    {
        'nombre': 'Papas Medellín',
        'precio': Decimal('28000'),
        'categoria': 'papas',
        'descripcion': 'Papas Rústicas 450 gr, salsa de la casa queso mozzarella, plátano maduro, guacamole, chicharrón, chorizo coctel, huevo de codorniz, salsa de aguacate, cebollín, tomate',
        'disponible': True,
    },
    {
        'nombre': 'Papas La Habana',
        'precio': Decimal('28000'),
        'categoria': 'papas',
        'descripcion': 'Papas rústicas 450 gr, salsa de la casa, queso mozzarella, milanesas verde, chicharrón, queso crema, tomate verde, chorizo coctel y salchicha salvaje',
        'disponible': True,
    },
    {
        'nombre': 'Papas Barahona',
        'precio': Decimal('28000'),
        'categoria': 'papas',
        'descripcion': 'Papas rústicas 450 gr, papa vieja (carne de cerdo desmechada) salsa de la casa, queso mozzarella, queso crema, huevos de codorniz, salsa de tocino dulce, malcitos, plátano maduro y cebollín',
        'disponible': True,
    },
    {
        'nombre': 'Papas Palermo',
        'precio': Decimal('30000'),
        'categoria': 'papas',
        'descripcion': 'Papas rústicas 450 gr, salsa de la casa, queso mozzarella, pico de gallo, juliana de lomo de cerdo, chorizo, morella, mayonesa de chimichurri y queso crema',
        'disponible': True,
    },
    {
        'nombre': 'Papas Milwaukee',
        'precio': Decimal('30000'),
        'categoria': 'papas',
        'descripcion': 'Papas rústicas 450 gr, queso mozzarella, salsa de la casa, salsa salvaje, salchichón cervecero, huevos de codorniz, tocinta, salsa ranch, BBQ sweet y cebollín',
        'disponible': True,
    },
    {
        'nombre': 'Papas New York',
        'precio': Decimal('30000'),
        'categoria': 'papas',
        'descripcion': 'Papas rústicas 450 gr, salsa de la casa, queso mozzarella, milanesas de pollo, mermelada de tocinta, salsa ranch, queso crema, BBQ sweet y cebollín',
        'disponible': True,
    },
    {
        'nombre': 'Papas Tijuana',
        'precio': Decimal('31000'),
        'categoria': 'papas',
        'descripcion': 'Papas rústicas 450 gr, salsa de la casa, queso mozzarella, picante (cerdo desmechado), mermelada de tocinta, queso crema, guacamole, tocinta (picante), salsa chick y mayonesa de pimientos asados',
        'disponible': True,
    },
    {
        'nombre': 'Papas Jalisco',
        'precio': Decimal('29000'),
        'categoria': 'papas',
        'descripcion': 'Papas rústicas 450 gr, salsa de la casa, queso mozzarella, pico de gallo, guacamole, queso crema, pulled pork (cerdo desmechado), salsa de tocino picante (opcional) - PICANTE',
        'disponible': True,
    },
    {
        'nombre': 'Papas Daytona',
        'precio': Decimal('29000'),
        'categoria': 'papas',
        'descripcion': 'Papas rústicas 450 gr, salsa de la casa, queso mozzarella, alitas crocantes bañadas en salsa daytona o DAYTONA SWEET, queso crema y salsa de sriracha - PICANTE',
        'disponible': True,
    },
    {
        'nombre': 'Papas Kentucky',
        'precio': Decimal('29000'),
        'categoria': 'papas',
        'descripcion': 'Papas rústicas 450 gr, salsa de la casa de pollo, queso mozzarella, mayonesa de cilantro, arrejotes de pollo, guacamole y palta, tomate verde y tocinta',
        'disponible': True,
    },
    {
        'nombre': 'Papas Milán',
        'precio': Decimal('30000'),
        'categoria': 'papas',
        'descripcion': 'Papas rústicas 450 gr, salsa mozzarella, crispetas de pollo, tocinta, salsa de maíz y tocino dulce, mayonesa de pesto, pimienta roja en escabeche, tomate cherry y malcitos',
        'disponible': True,
    },
    {
        'nombre': 'Papas Barcelona',
        'precio': Decimal('30000'),
        'categoria': 'papas',
        'descripcion': 'Papas rústicas 450 gr, costilla ahumada, jardín (cebolla-cilantro-pimentón escaivado), queso crema, queso mozzarella, tocinta crocante, salsa de la casa, salsa de aguacate y BBQ (budweiser o picante)',
        'disponible': True,
    },
    {
        'nombre': 'Papas Miami',
        'precio': Decimal('31000'),
        'categoria': 'papas',
        'descripcion': 'Papas rústicas 450 gr, salsa de la casa, queso mozzarella, camarones apanados, pico de gallo, guacamole, queso crema y salsa de sriracha dulce',
        'disponible': True,
    },

    # ========== ADICIONES ==========
    {
        'nombre': 'Camarones apanados',
        'precio': Decimal('11500'),
        'categoria': 'adiciones',
        'descripcion': 'Adición de camarones crujientes',
        'disponible': True,
    },
    {
        'nombre': 'Milanesa de pollo',
        'precio': Decimal('11500'),
        'categoria': 'adiciones',
        'descripcion': 'Adición de milanesa de pollo frita',
        'disponible': True,
    },
    {
        'nombre': 'Alitas x4',
        'precio': Decimal('11500'),
        'categoria': 'adiciones',
        'descripcion': 'Cuatro alitas de pollo crocantes',
        'disponible': True,
    },
    {
        'nombre': 'Costillas',
        'precio': Decimal('11500'),
        'categoria': 'adiciones',
        'descripcion': 'Adición de costillas ahumadas',
        'disponible': True,
    },
    {
        'nombre': 'Pulled Pork',
        'precio': Decimal('9500'),
        'categoria': 'adiciones',
        'descripcion': 'Cerdo desmechado',
        'disponible': True,
    },
    {
        'nombre': 'Crispetas de pollo',
        'precio': Decimal('9500'),
        'categoria': 'adiciones',
        'descripcion': 'Pollo rebozado y frito',
        'disponible': True,
    },
    {
        'nombre': 'Trozos tomo de cerdo',
        'precio': Decimal('9500'),
        'categoria': 'adiciones',
        'descripcion': 'Trozos de cerdo frito',
        'disponible': True,
    },
    {
        'nombre': 'Chicharrón',
        'precio': Decimal('8500'),
        'categoria': 'adiciones',
        'descripcion': 'Chicharrón crocante',
        'disponible': True,
    },
    {
        'nombre': 'Chorizos Cóctel',
        'precio': Decimal('7500'),
        'categoria': 'adiciones',
        'descripcion': 'Chorizos pequeños cocidos',
        'disponible': True,
    },
    {
        'nombre': 'Salchicha',
        'precio': Decimal('7500'),
        'categoria': 'adiciones',
        'descripcion': 'Salchicha frita',
        'disponible': True,
    },
    {
        'nombre': 'Mermelada de tocinta',
        'precio': Decimal('6500'),
        'categoria': 'adiciones',
        'descripcion': 'Tocinta dulce en mermelada',
        'disponible': True,
    },
    {
        'nombre': 'Queso Mozzarella',
        'precio': Decimal('6500'),
        'categoria': 'adiciones',
        'descripcion': 'Queso mozzarella derretido',
        'disponible': True,
    },
    {
        'nombre': 'Huevos de codorniz',
        'precio': Decimal('5500'),
        'categoria': 'adiciones',
        'descripcion': 'Huevos fritos de codorniz',
        'disponible': True,
    },
    {
        'nombre': 'Tocinta',
        'precio': Decimal('6500'),
        'categoria': 'adiciones',
        'descripcion': 'Tocinta frita crocante',
        'disponible': True,
    },
    {
        'nombre': 'Morella Cóctel',
        'precio': Decimal('6500'),
        'categoria': 'adiciones',
        'descripcion': 'Morella cocida y frita',
        'disponible': True,
    },
    {
        'nombre': 'Jalapeños',
        'precio': Decimal('8000'),
        'categoria': 'adiciones',
        'descripcion': 'Jalapeños encurtidos',
        'disponible': True,
    },
    {
        'nombre': 'Pico de gallo',
        'precio': Decimal('3000'),
        'categoria': 'adiciones',
        'descripcion': 'Tomate, cebolla y cilantro picado',
        'disponible': True,
    },
    {
        'nombre': 'Plátano maduro',
        'precio': Decimal('3000'),
        'categoria': 'adiciones',
        'descripcion': 'Plátano frito',
        'disponible': True,
    },
    {
        'nombre': 'Malcitos',
        'precio': Decimal('3500'),
        'categoria': 'adiciones',
        'descripcion': 'Maíz frito',
        'disponible': True,
    },
    {
        'nombre': 'Salchicha crocante',
        'precio': Decimal('7500'),
        'categoria': 'adiciones',
        'descripcion': 'Salchicha extra crocante',
        'disponible': True,
    },
    {
        'nombre': 'Salchicha salvaje',
        'precio': Decimal('7500'),
        'categoria': 'adiciones',
        'descripcion': 'Salchicha especial',
        'disponible': True,
    },

    # ========== SALSAS ==========
    {
        'nombre': 'Salsa Daytona',
        'precio': Decimal('2500'),
        'categoria': 'salsas',
        'descripcion': 'Salsa picante Daytona',
        'disponible': True,
    },
    {
        'nombre': 'Salsa de Sriracha Dulce',
        'precio': Decimal('2500'),
        'categoria': 'salsas',
        'descripcion': 'Salsa sriracha con toque dulce',
        'disponible': True,
    },
    {
        'nombre': 'Salsa de Tocino Picante',
        'precio': Decimal('2500'),
        'categoria': 'salsas',
        'descripcion': 'Salsa con tocino y picante',
        'disponible': True,
    },
    {
        'nombre': 'Mayonesa de Cilantro',
        'precio': Decimal('2500'),
        'categoria': 'salsas',
        'descripcion': 'Mayonesa casera con cilantro',
        'disponible': True,
    },
    {
        'nombre': 'Mayonesa Verde',
        'precio': Decimal('2500'),
        'categoria': 'salsas',
        'descripcion': 'Mayonesa verde con hierbas',
        'disponible': True,
    },
    {
        'nombre': 'BBQ Budweiser',
        'precio': Decimal('2500'),
        'categoria': 'salsas',
        'descripcion': 'Salsa BBQ con cerveza Budweiser',
        'disponible': True,
    },
    {
        'nombre': 'Salsa de la casa',
        'precio': Decimal('2500'),
        'categoria': 'salsas',
        'descripcion': 'Salsa especial de la casa',
        'disponible': True,
    },
    {
        'nombre': 'Salsa de Aguacate',
        'precio': Decimal('2500'),
        'categoria': 'salsas',
        'descripcion': 'Guacamole fresco',
        'disponible': True,
    },
    {
        'nombre': 'Salsa Cosmopolita',
        'precio': Decimal('2500'),
        'categoria': 'salsas',
        'descripcion': 'Salsa especial Cosmopolita',
        'disponible': True,
    },
    {
        'nombre': 'Mayonesa de Chimichurri',
        'precio': Decimal('2500'),
        'categoria': 'salsas',
        'descripcion': 'Mayonesa con chimichurri argentino',
        'disponible': True,
    },
    {
        'nombre': 'Mayonesa de Pesto',
        'precio': Decimal('2500'),
        'categoria': 'salsas',
        'descripcion': 'Mayonesa con pesto italiano',
        'disponible': True,
    },
    {
        'nombre': 'Salsa de Maíz y Tocino',
        'precio': Decimal('2500'),
        'categoria': 'salsas',
        'descripcion': 'Salsa dulce con maíz y tocino',
        'disponible': True,
    },
    {
        'nombre': 'Salsa Ranch',
        'precio': Decimal('2500'),
        'categoria': 'salsas',
        'descripcion': 'Salsa Ranch americana',
        'disponible': True,
    },
    {
        'nombre': 'Queso Cheddar',
        'precio': Decimal('2500'),
        'categoria': 'salsas',
        'descripcion': 'Salsa de queso cheddar',
        'disponible': True,
    },

    # ========== BEBIDAS ==========
    {
        'nombre': 'Gaseosa Personal',
        'precio': Decimal('4000'),
        'categoria': 'bebidas',
        'descripcion': 'Gaseosa personal (350ml)',
        'disponible': True,
    },
    {
        'nombre': 'Gaseosa 1.5L',
        'precio': Decimal('9000'),
        'categoria': 'bebidas',
        'descripcion': 'Gaseosa botella 1.5 litros',
        'disponible': True,
    },
    {
        'nombre': 'Agua',
        'precio': Decimal('4000'),
        'categoria': 'bebidas',
        'descripcion': 'Agua embotellada',
        'disponible': True,
    },
    {
        'nombre': 'Mr. Tea',
        'precio': Decimal('5000'),
        'categoria': 'bebidas',
        'descripcion': 'Té helado Mr. Tea',
        'disponible': True,
    },
    {
        'nombre': 'Costerita',
        'precio': Decimal('5000'),
        'categoria': 'bebidas',
        'descripcion': 'Cerveza Costerita',
        'disponible': True,
    },
    {
        'nombre': 'Jugo Hit',
        'precio': Decimal('5000'),
        'categoria': 'bebidas',
        'descripcion': 'Jugo Hit natural',
        'disponible': True,
    },
]

# Crear todos los productos
for prod in productos:
    Producto.objects.create(**prod)

print(f"✓ Se crearon {len(productos)} productos del catálogo CityPapa")
print(f"\nProductos por categoría:")
print(f"  - Papas: {Producto.objects.filter(categoria='papas').count()}")
print(f"  - Adiciones: {Producto.objects.filter(categoria='adiciones').count()}")
print(f"  - Salsas: {Producto.objects.filter(categoria='salsas').count()}")
print(f"  - Bebidas: {Producto.objects.filter(categoria='bebidas').count()}")
