#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'citypapa.settings')
django.setup()

from django.contrib.auth.models import User
from tienda.models import UsuarioTienda

print("=" * 60)
print("VERIFICANDO USUARIO ADMIN")
print("=" * 60)

try:
    admin = User.objects.get(username='admin')
    print(f"\n✓ Usuario Admin existe: {admin.username}")
    print(f"  Email: {admin.email}")
    print(f"  Is Staff: {admin.is_staff}")
    print(f"  Is Superuser: {admin.is_superuser}")
    
    try:
        ut = admin.usuario_tienda
        print(f"\n✓ UsuarioTienda asignado:")
        print(f"  Rol: {ut.rol}")
        print(f"  Tienda: {ut.tienda}")
        print(f"  Activo: {ut.activo}")
    except UsuarioTienda.DoesNotExist:
        print(f"\n✗ Sin UsuarioTienda asignado - CREANDO...")
        ut = UsuarioTienda.objects.create(
            usuario=admin,
            rol='administrador',
            tienda=None,
            activo=True
        )
        print(f"✓ UsuarioTienda creado:")
        print(f"  Rol: {ut.rol}")
        print(f"  Tienda: {ut.tienda}")
        print(f"  Activo: {ut.activo}")

except User.DoesNotExist:
    print("✗ Usuario admin no encontrado")

print("\n" + "=" * 60)
