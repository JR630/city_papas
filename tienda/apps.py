"""
Configuración de la aplicación 'tienda'.
"""
from django.apps import AppConfig


class TiendaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tienda'
    verbose_name = 'Gestión de Tiendas'
