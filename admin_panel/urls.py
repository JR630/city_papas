"""
URLs para la aplicación admin_panel.
"""
from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.admin_dashboard_view, name='admin-dashboard'),
    
    # Gestión de tiendas
    path('tiendas/', views.tiendas_list_view, name='tiendas-list'),
    path('tiendas/crear/', views.crear_tienda_view, name='crear-tienda'),
    path('tiendas/<int:tienda_id>/', views.tienda_detail_view, name='tienda-detail'),
    path('tiendas/<int:tienda_id>/editar/', views.editar_tienda_view, name='editar-tienda'),
    
    # Gestión de productos
    path('productos/', views.productos_list_view, name='productos-list'),
    path('productos/crear/', views.crear_producto_view, name='crear-producto'),
    path('productos/<int:producto_id>/editar/', views.editar_producto_view, name='editar-producto'),
    path('productos/<int:producto_id>/eliminar/', views.eliminar_producto_view, name='eliminar-producto'),
    
    # Reportes
    path('reportes/', views.reportes_view, name='reportes'),
    path('reportes/exportar/', views.exportar_reportes_view, name='exportar-reportes'),
    
    # Inventario
    path('inventario/', views.admin_inventario_view, name='admin-inventario'),
    path('inventario/entrada/', views.admin_entrada_producto_view, name='admin-entrada-producto'),
    path('inventario/salida/', views.admin_salida_producto_view, name='admin-salida-producto'),
    path('inventario/ajuste/', views.admin_ajuste_stock_view, name='admin-ajuste-stock'),
    path('inventario/historial/', views.admin_historial_movimientos_view, name='admin-historial-movimientos'),
]
