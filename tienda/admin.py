"""
Registro de modelos en el admin de Django para la aplicación tienda.
"""
from django.contrib import admin
from .models import Tienda, Producto, UsuarioTienda, Venta, CierreCaja


@admin.register(Tienda)
class TiendaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'ciudad', 'telefono', 'activa', 'fecha_creacion')
    list_filter = ('activa', 'ciudad', 'fecha_creacion')
    search_fields = ('nombre', 'ciudad')
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'ciudad')
        }),
        ('Contacto', {
            'fields': ('direccion', 'telefono', 'email')
        }),
        ('Estado', {
            'fields': ('activa',)
        }),
    )


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio', 'disponible')
    list_filter = ('categoria', 'disponible')
    search_fields = ('nombre',)
    fieldsets = (
        ('Información del Producto', {
            'fields': ('nombre', 'descripcion', 'categoria')
        }),
        ('Precios', {
            'fields': ('precio',)
        }),
        ('Estado', {
            'fields': ('disponible',)
        }),
    )


@admin.register(UsuarioTienda)
class UsuarioTiendaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'rol', 'tienda', 'activo')
    list_filter = ('rol', 'activo', 'tienda')
    search_fields = ('usuario__username', 'tienda__nombre')
    fieldsets = (
        ('Usuario', {
            'fields': ('usuario',)
        }),
        ('Asignación', {
            'fields': ('tienda', 'rol')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
    )


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('tienda', 'producto', 'cantidad', 'total', 'fecha_venta')
    list_filter = ('tienda', 'fecha_venta', 'producto__categoria')
    search_fields = ('tienda__nombre', 'producto__nombre')
    readonly_fields = ('fecha', 'total')
    date_hierarchy = 'fecha_venta'
    fieldsets = (
        ('Información de Venta', {
            'fields': ('tienda', 'producto')
        }),
        ('Detalles', {
            'fields': ('cantidad', 'precio_unitario', 'total')
        }),
        ('Registro', {
            'fields': ('registrado_por', 'fecha_venta', 'fecha')
        }),
    )


@admin.register(CierreCaja)
class CierreCajaAdmin(admin.ModelAdmin):
    list_display = ('tienda', 'fecha_cierre', 'total_general', 'status_efectivo', 'diferencia_efectivo', 'fecha_registro')
    list_filter = ('tienda', 'fecha_cierre')
    search_fields = ('tienda__nombre',)
    readonly_fields = ('fecha_registro',)
    date_hierarchy = 'fecha_cierre'
    fieldsets = (
        ('Información del Cierre', {
            'fields': ('tienda', 'fecha_cierre')
        }),
        ('Efectivo', {
            'fields': ('total_efectivo_esperado', 'total_efectivo_contado', 'diferencia_efectivo')
        }),
        ('Otros Métodos de Pago', {
            'fields': ('total_tarjeta_credito', 'total_tarjeta_debito', 'total_transferencia', 'total_nequi', 'total_otro')
        }),
        ('Resumen', {
            'fields': ('total_general', 'cantidad_transacciones')
        }),
        ('Notas', {
            'fields': ('notas',)
        }),
        ('Auditoría', {
            'fields': ('registrado_por', 'fecha_registro'),
            'classes': ('collapse',)
        }),
    )
