from django.core.management.base import BaseCommand
from django.utils import timezone
from tienda.models import Producto, Tienda, StockActual, MovimientoInventario

class Command(BaseCommand):
    help = 'Carga los ingredientes de la lista del restaurante con cantidades realistas'

    def handle(self, *args, **options):
        # Obtener las tiendas
        tiendas = Tienda.objects.all()
        if not tiendas.exists():
            self.stdout.write(self.style.ERROR('No hay tiendas creadas'))
            return

        # Datos de ingredientes
        ingredientes_data = [
            # BASES (3)
            ('Papas Rústicas', 'ingrediente_base', 150),
            ('Queso Mozzarella', 'ingrediente_base', 100),
            ('Salsa de la Casa', 'ingrediente_base', 80),
            
            # PROTEÍNAS (19)
            ('Chicharrón', 'proteinas', 35),
            ('Chorizo Cóctel', 'proteinas', 40),
            ('Chorizo', 'proteinas', 45),
            ('Salchicha Salvaje', 'proteinas', 30),
            ('Salchicha Americana', 'proteinas', 30),
            ('Salchicha', 'proteinas', 40),
            ('Salchichón Cervecero', 'proteinas', 25),
            ('Ropa Vieja', 'proteinas', 35),
            ('Pulled Pork', 'proteinas', 40),
            ('Julianas de Lomo', 'proteinas', 25),
            ('Milanesa de Pollo', 'proteinas', 30),
            ('Crispetas de Pollo', 'proteinas', 35),
            ('Alitas de Pollo', 'proteinas', 28),
            ('Costilla Ahumada', 'proteinas', 22),
            ('Camarones Apanados', 'proteinas', 20),
            ('Morcilla', 'proteinas', 20),
            ('Tocineta', 'proteinas', 45),
            ('Huevos de Codorniz', 'proteinas', 60),
            
            # VEGETALES Y FRUTAS (10)
            ('Plátano Maduro', 'vegetales', 100),
            ('Aguacate', 'vegetales', 50),
            ('Tomate', 'vegetales', 75),
            ('Cebollín', 'vegetales', 40),
            ('Cebolla', 'vegetales', 60),
            ('Cilantro', 'vegetales', 35),
            ('Pimentón Escalivado', 'vegetales', 30),
            ('Pico de Gallo', 'vegetales', 45),
            ('Maicitos', 'vegetales', 55),
            ('Jalapeños', 'vegetales', 40),
            
            # SALSAS Y ADEREZOS (16)
            ('Queso Crema', 'aderezos', 25),
            ('Queso Cheddar', 'aderezos', 20),
            ('Mermelada de Tocineta', 'aderezos', 15),
            ('Salsa de Tocino Dulce', 'aderezos', 20),
            ('Salsa de Tocino Picante', 'aderezos', 20),
            ('Salsa de Maíz y Tocino', 'aderezos', 18),
            ('Salsa Ranch', 'aderezos', 22),
            ('Salsa BBQ', 'aderezos', 20),
            ('Salsa Daytona', 'aderezos', 19),
            ('Salsa Sriracha', 'aderezos', 17),
            ('Salsa Chick', 'aderezos', 18),
            ('Salsa Cosmopolita', 'aderezos', 16),
            ('Salsa Rosada', 'aderezos', 19),
            ('Mayonesa Verde', 'aderezos', 21),
            ('Mayonesa Chimichurri', 'aderezos', 19),
            ('Mayonesa Pimientos Asados', 'aderezos', 18),
            
            # COMPLEMENTOS (2)
            ('Tostacos Picantes', 'complemento', 80),
            ('Pimienta Roja en Escamas', 'complemento', 50),
        ]

        productos_creados = 0
        productos_existentes = 0

        for nombre, categoria, cantidad_base in ingredientes_data:
            # Crear o actualizar producto
            producto, created = Producto.objects.get_or_create(
                nombre=nombre,
                defaults={
                    'categoria': categoria,
                    'precio': 0,  # Se actualiza manual según plato
                    'disponible': True,
                }
            )

            if created:
                productos_creados += 1
                self.stdout.write(f'  ✓ Producto creado: {nombre}')
            else:
                productos_existentes += 1

            # Crear/actualizar StockActual para cada tienda
            for tienda in tiendas:
                stock, created = StockActual.objects.get_or_create(
                    tienda=tienda,
                    producto=producto,
                    defaults={
                        'cantidad': cantidad_base,
                        'stock_minimo': max(int(cantidad_base * 0.3), 5),
                    }
                )

                if created:
                    # Crear registro de movimiento inicial
                    MovimientoInventario.objects.create(
                        tipo_movimiento='entrada',
                        tipo_entrada='compra',
                        producto=producto,
                        tienda=tienda,
                        cantidad=cantidad_base,
                        stock_anterior=0,
                        stock_posterior=cantidad_base,
                        referencia='SISTEMA',
                        descripcion='Carga inicial de inventario'
                    )
                    self.stdout.write(f'    → Stock creado en {tienda.nombre}: {cantidad_base} unidades')

        self.stdout.write(self.style.SUCCESS(f'\n✅ Proceso completado'))
        self.stdout.write(f'  • Productos creados: {productos_creados}')
        self.stdout.write(f'  • Productos existentes: {productos_existentes}')
        self.stdout.write(f'  • Total de tiendas: {tiendas.count()}')
        self.stdout.write(f'  • Registros de stock creados: ~{productos_creados * tiendas.count()}')
