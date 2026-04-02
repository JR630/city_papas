"""
URL Configuration para CityPapa project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from tienda import views as tienda_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Autenticación
    path('', tienda_views.login_view, name='login'),
    path('logout/', tienda_views.logout_view, name='logout'),
    path('register/tienda/', tienda_views.register_tienda_view, name='register_tienda'),
    
    # URLs de tienda
    path('tienda/', include('tienda.urls')),
    
    # URLs de admin panel
    path('admin-panel/', include('admin_panel.urls')),
]
