import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'citypapa.settings')
django.setup()
from tienda.models import Venta, UsuarioTienda, Tienda

print('TIENDAS:')
for tienda in Tienda.objects.all():
    count = Venta.objects.filter(tienda=tienda).count()
    print(f'  - {tienda.nombre} (ID: {tienda.id}): {count} ventas')

print('\nUSUARIOSTIENDA:')
for ut in UsuarioTienda.objects.filter(rol='tienda'):
    tienda_name = ut.tienda.nombre if ut.tienda else 'Sin tienda'
    print(f'  - {ut.usuario.username} -> {tienda_name}')

print('\nVENTAS (últimas 10):')
for venta in Venta.objects.select_related('tienda').order_by('-fecha')[:10]:
    print(f'  - {venta.tienda.nombre} | {venta.cliente_nombre} | {venta.producto.nombre} | {venta.fecha_venta}')
