"""
URLs para la aplicación tienda.
"""
from django.urls import path
from . import views

app_name = 'tienda'

urlpatterns = [
    path('dashboard/', views.tienda_dashboard_view, name='tienda-dashboard'),
    path('registrar-venta/', views.registrar_venta_view, name='registrar-venta'),
    path('historial-ventas/', views.historial_ventas_view, name='historial-ventas'),
    path('catalogo/', views.catalogo_productos_view, name='catalogo-productos'),
    path('cerrar-caja/', views.cerrar_caja_view, name='cerrar-caja'),
    path('reportes/', views.reportes_view, name='reportes'),
    
    # URLs de inventario
    path('inventario/', views.inventario_view, name='inventario'),
    path('inventario/entrada/', views.entrada_producto_view, name='entrada-producto'),
    path('inventario/salida/', views.salida_producto_view, name='salida-producto'),
    path('inventario/historial/', views.historial_movimientos_view, name='historial-movimientos'),
    path('inventario/ajuste/', views.ajuste_stock_view, name='ajuste-stock'),
]
