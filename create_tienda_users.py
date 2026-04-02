#!/usr/bin/env python
"""
Script para crear usuarios de tienda.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'citypapa.settings')
django.setup()

from django.contrib.auth.models import User
from tienda.models import Tienda, UsuarioTienda

# Datos de usuarios a crear
usuarios_data = [
    {'username': 'tienda1', 'password': 'tienda1123', 'tienda_nombre': 'CityPapa Bogotá'},
    {'username': 'tienda2', 'password': 'tienda2123', 'tienda_nombre': 'CityPapa Medellín'},
    {'username': 'tienda3', 'password': 'tienda3123', 'tienda_nombre': 'CityPapa Cali'},
]

# Crear usuarios
for user_data in usuarios_data:
    username = user_data['username']
    password = user_data['password']
    tienda_nombre = user_data['tienda_nombre']
    
    # Verificar si el usuario ya existe
    try:
        user = User.objects.get(username=username)
        print(f"✓ Usuario {username} ya existe")
    except User.DoesNotExist:
        user = User.objects.create_user(username=username, password=password)
        print(f"✓ Usuario {username} creado")
    
    # Obtener tienda por nombre
    try:
        tienda = Tienda.objects.get(nombre=tienda_nombre)
    except Tienda.DoesNotExist:
        print(f"✗ No se encontró tienda: {tienda_nombre}")
        continue
    
    # Crear relación UsuarioTienda
    try:
        usuario_tienda = UsuarioTienda.objects.get(usuario=user)
        print(f"  - UsuarioTienda para {username} ya existe")
    except UsuarioTienda.DoesNotExist:
        UsuarioTienda.objects.create(
            usuario=user,
            tienda=tienda,
            rol='tienda',
            activo=True
        )
        print(f"  - UsuarioTienda creado para {username} en {tienda.nombre}")

print("\n✓ Usuarios de tienda configurados correctamente")
