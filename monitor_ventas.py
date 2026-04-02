import os
import sys
import django
import time
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'citypapa.settings')
django.setup()

# Ver últimas ventas cada 2 segundos
from tienda.models import Venta

print("🔍 Monitoreando nuevas ventas...")
print("Presiona Ctrl+C para salir\n")

last_count = Venta.objects.count()

try:
    while True:
        current_count = Venta.objects.count()
        
        if current_count > last_count:
            print(f"\n✅ {datetime.now().strftime('%H:%M:%S')} - Nueva venta detectada!")
            
            # Mostrar la última venta
            latest_venta = Venta.objects.order_by('-fecha').first()
            if latest_venta:
                print(f"   Cliente: {latest_venta.cliente_nombre}")
                print(f"   Producto: {latest_venta.producto.nombre}")
                print(f"   Cantidad: {latest_venta.cantidad}")
                print(f"   Total: ${latest_venta.total}")
                print(f"   Método: {latest_venta.metodo_pago}")
                print(f"   Orden: {latest_venta.numero_orden}")
            
            last_count = current_count
        
        time.sleep(2)
        
except KeyboardInterrupt:
    print("\n\n❌ Monitoreo detenido")
    sys.exit(0)
