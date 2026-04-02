"""
Modelos de datos para la aplicación de tiendas.
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from datetime import datetime


class Tienda(models.Model):
    """Modelo para representar una sucursal de CityPapa."""
    
    nombre = models.CharField(max_length=255, unique=True)
    direccion = models.TextField()
    ciudad = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    email = models.EmailField()
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['nombre']
        verbose_name_plural = 'Tiendas'
    
    def __str__(self):
        return f"{self.nombre} - {self.ciudad}"


class Producto(models.Model):
    """Modelo para representar productos disponibles."""
    
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    categoria = models.CharField(
        max_length=50,
        choices=[
            ('papas', 'Papas'),
            ('adiciones', 'Adiciones'),
            ('salsas', 'Salsas'),
            ('bebidas', 'Bebidas'),
            ('hamburguesa', 'Hamburguesa'),
            ('arepa', 'Arepa'),
            ('perro', 'Perro Caliente'),
            ('pizza', 'Pizza'),
            ('bebida', 'Bebida'),
            ('postre', 'Postre'),
            ('ingrediente_base', 'Ingrediente Base'),
            ('proteinas', 'Proteínas'),
            ('vegetales', 'Vegetales'),
            ('aderezos', 'Aderezos'),
            ('complemento', 'Complemento'),
            ('otro', 'Otro'),
        ]
    )
    disponible = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['categoria', 'nombre']
        verbose_name_plural = 'Productos'
    
    def __str__(self):
        return f"{self.nombre} (${self.precio})"


class UsuarioTienda(models.Model):
    """Modelo para extender el usuario de Django y vincularlo con una tienda."""
    
    ROLES = [
        ('administrador', 'Administrador'),
        ('tienda', 'Tienda'),
    ]
    
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='usuario_tienda')
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE, related_name='usuarios', null=True, blank=True)
    rol = models.CharField(max_length=20, choices=ROLES)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = 'Usuarios de Tienda'
    
    def __str__(self):
        if self.tienda:
            return f"{self.usuario.username} - {self.tienda.nombre} ({self.rol})"
        return f"{self.usuario.username} ({self.rol})"


class Venta(models.Model):
    """Modelo para registrar las ventas de cada tienda."""
    
    METODO_PAGO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('tarjeta_credito', 'Tarjeta de Crédito'),
        ('tarjeta_debito', 'Tarjeta de Débito'),
        ('transferencia', 'Transferencia Bancaria'),
        ('nequi', 'Nequi'),
        ('otro', 'Otro'),
    ]
    
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE, related_name='ventas')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='ventas')
    cantidad = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    total = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES, default='efectivo')
    cliente_nombre = models.CharField(max_length=100, default='Cliente', blank=False)
    numero_orden = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    registrado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='ventas_registradas')
    fecha = models.DateTimeField(auto_now_add=True)
    fecha_venta = models.DateField()  # Fecha en que se registró la venta (puede ser hoy o pasada)
    
    class Meta:
        ordering = ['-fecha_venta', '-fecha']
        verbose_name_plural = 'Ventas'
        indexes = [
            models.Index(fields=['tienda', 'fecha_venta']),
            models.Index(fields=['fecha_venta']),
            models.Index(fields=['numero_orden']),
        ]
    
    def __str__(self):
        return f"{self.tienda.nombre} - {self.producto.nombre} (x{self.cantidad})"
    
    def save(self, *args, **kwargs):
        """Calcula automáticamente el total antes de guardar."""
        # Siempre recalcular el total para asegurar consistencia
        self.total = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)


class CierreCaja(models.Model):
    """Modelo para registrar los cierres de caja diarios."""
    
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE, related_name='cierres_caja')
    fecha_cierre = models.DateField()  # Fecha del cierre (generalmente el día cerrado)
    
    # Resumen por método de pago
    total_efectivo_esperado = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    total_efectivo_contado = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    diferencia_efectivo = models.DecimalField(max_digits=10, decimal_places=2)  # Puede ser positivo o negativo
    
    # Totales por método de pago
    total_tarjeta_credito = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    total_tarjeta_debito = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    total_transferencia = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    total_nequi = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    total_otro = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    
    total_general = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    cantidad_transacciones = models.PositiveIntegerField()
    
    # Información adicional
    notas = models.TextField(blank=True, null=True)
    registrado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='cierres_registrados')
    
    # Auditoría
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-fecha_cierre']
        verbose_name_plural = 'Cierres de Caja'
        unique_together = ['tienda', 'fecha_cierre']
        indexes = [
            models.Index(fields=['tienda', 'fecha_cierre']),
            models.Index(fields=['fecha_cierre']),
        ]
    
    def __str__(self):
        return f"{self.tienda.nombre} - Cierre {self.fecha_cierre}"
    
    @property
    def status_efectivo(self):
        """Retorna el estado del cuadre de efectivo."""
        if self.diferencia_efectivo == 0:
            return 'Cuadrado'
        elif self.diferencia_efectivo > 0:
            return 'Sobrante'
        else:
            return 'Faltante'


class StockActual(models.Model):
    """Modelo para mantener el stock actual de cada producto por tienda."""
    
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE, related_name='stocks')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='stocks')
    cantidad = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    stock_minimo = models.PositiveIntegerField(default=10, validators=[MinValueValidator(0)])
    ultima_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Stocks Actuales'
        unique_together = ['tienda', 'producto']
        ordering = ['producto__categoria', 'producto__nombre']
        indexes = [
            models.Index(fields=['tienda', 'producto']),
            models.Index(fields=['cantidad']),
        ]
    
    def __str__(self):
        return f"{self.tienda.nombre} - {self.producto.nombre}: {self.cantidad} unidades"
    
    @property
    def estado_stock(self):
        """Retorna el estado del stock."""
        if self.cantidad == 0:
            return 'agotado'
        elif self.cantidad < self.stock_minimo:
            return 'bajo'
        else:
            return 'normal'
    
    @property
    def estado_texto(self):
        """Retorna el texto del estado."""
        estados = {
            'agotado': 'Agotado',
            'bajo': 'Bajo Stock',
            'normal': 'Normal'
        }
        return estados.get(self.estado_stock, 'Desconocido')


class MovimientoInventario(models.Model):
    """Modelo para registrar todos los movimientos de inventario."""
    
    TIPO_MOVIMIENTO_CHOICES = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
        ('ajuste', 'Ajuste'),
        ('devolucion', 'Devolución'),
    ]
    
    TIPO_ENTRADA_CHOICES = [
        ('compra', 'Compra'),
        ('devolucion', 'Devolución de Cliente'),
        ('transferencia_entrada', 'Transferencia Recibida'),
        ('otro', 'Otro'),
    ]
    
    TIPO_SALIDA_CHOICES = [
        ('venta', 'Venta'),
        ('merma', 'Merma'),
        ('consumo_interno', 'Consumo Interno'),
        ('transferencia_salida', 'Transferencia Enviada'),
        ('otro', 'Otro'),
    ]
    
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE, related_name='movimientos_inventario')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='movimientos')
    tipo_movimiento = models.CharField(max_length=20, choices=TIPO_MOVIMIENTO_CHOICES)
    
    # Campos específicos según el tipo
    tipo_entrada = models.CharField(max_length=50, choices=TIPO_ENTRADA_CHOICES, null=True, blank=True)
    tipo_salida = models.CharField(max_length=50, choices=TIPO_SALIDA_CHOICES, null=True, blank=True)
    
    cantidad = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    stock_anterior = models.PositiveIntegerField(default=0)
    stock_posterior = models.PositiveIntegerField(default=0)
    
    # Información del movimiento
    referencia = models.CharField(max_length=100, blank=True)  # Número de compra, NC, etc.
    descripcion = models.TextField(blank=True)
    registrado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='movimientos_registrados')
    
    # Auditoría
    fecha_movimiento = models.DateTimeField(auto_now_add=True)
    fecha = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-fecha_movimiento']
        verbose_name_plural = 'Movimientos de Inventario'
        indexes = [
            models.Index(fields=['tienda', 'fecha_movimiento']),
            models.Index(fields=['producto', 'fecha_movimiento']),
            models.Index(fields=['tipo_movimiento']),
        ]
    
    def __str__(self):
        return f"{self.tienda.nombre} - {self.tipo_movimiento} - {self.producto.nombre} ({self.cantidad} unidades)"
    
    def save(self, *args, **kwargs):
        """Actualiza el stock actual al guardar el movimiento."""
        stock_obj = StockActual.objects.get_or_create(
            tienda=self.tienda,
            producto=self.producto,
            defaults={'cantidad': 0}
        )[0]
        
        # Registrar stock anterior
        self.stock_anterior = stock_obj.cantidad
        
        # Calcular nuevo stock
        if self.tipo_movimiento == 'entrada':
            stock_obj.cantidad += self.cantidad
        elif self.tipo_movimiento == 'salida':
            stock_obj.cantidad = max(0, stock_obj.cantidad - self.cantidad)
        elif self.tipo_movimiento == 'ajuste':
            # Para ajustes, cantidad es el nuevo total
            stock_obj.cantidad = self.cantidad
        elif self.tipo_movimiento == 'devolucion':
            stock_obj.cantidad += self.cantidad
        
        self.stock_posterior = stock_obj.cantidad
        stock_obj.save()
        
        super().save(*args, **kwargs)
