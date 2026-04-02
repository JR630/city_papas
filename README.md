# CityPapa - Sistema de Gestión de Ventas

[![Django](https://img.shields.io/badge/Django-4.2-green)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](https://opensource.org/licenses/MIT)

**CityPapa** es una aplicación web completa desarrollada con Django para la gestión de ventas de una cadena de comidas rápidas. Incluye panel administrativo consolidado y portales individuales para cada sucursal.

## 🎨 Identidad Visual

La aplicación implementa una identidad visual urbana y vibrante basada en:

- **Paleta de Colores:**
  - 🟠 Naranja primario: `#FF6B00`
  - 🟡 Amarillo de acento: `#FFD600`
  - ⬛ Fondos muy oscuros: `#0D0D0D`, `#1A1A1A`
  - ⚪ Texto claro: `#FFFFFF`

- **Tipografía:**
  - Títulos: Bebas Neue (sans-serif, bloque, gruesa)
  - Cuerpo: Inter / Poppins (sans-serif)

- **Estilo:** Alto contraste, urbano, moderno, sin elementos corporativos genéricos.

## 📋 Requisitos

- Python 3.8+
- Django 4.2+
- SQLite3 (incluido con Python)
- pip (gestor de paquetes de Python)

## 🚀 Instalación y Configuración

### 1. Clonar o descargar el repositorio

```bash
cd city_papas
```

### 2. Crear un entorno virtual

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Aplicar migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Crear datos de prueba

Se puede usar el script `populate_db.py` para crear datos de prueba iniciales:

**Opción A: Vía shell de Django**
```bash
python manage.py shell < populate_db.py
```

**Opción B: Dentro del shell interactivo**
```bash
python manage.py shell
>>> exec(open('populate_db.py').read())
```

### 6. Iniciar el servidor

```bash
python manage.py runserver
```

La aplicación estará disponible en: `http://localhost:8000`

---

## 👤 Cuentas de Prueba

Después de ejecutar `populate_db.py`, tendrás las siguientes cuentas:

### 👨‍💼 Administrador
- **Usuario:** `admin`
- **Contraseña:** `admin123`
- **Acceso:** http://localhost:8000/admin-panel/dashboard/
- **Funcionalidades:** Dashboard consolidado, gestión de tiendas, productos, usuarios y reportes

### 🏪 Tiendas
- **Usuario:** `tienda1`, `tienda2`, `tienda3`
- **Contraseña:** `tienda1123`, `tienda2123`, `tienda3123`
- **Acceso:** http://localhost:8000/tienda/dashboard/
- **Funcionalidades:** Registro de ventas, resumen diario, historial, catálogo de productos

---

## 📁 Estructura del Proyecto

```
city_papas/
├── citypapa/                 # Configuración principal del proyecto
│   ├── __init__.py
│   ├── settings.py          # Configuración de Django
│   ├── urls.py              # URLs principales
│   ├── asgi.py
│   └── wsgi.py
│
├── tienda/                   # Aplicación de tienda/sucursal
│   ├── migrations/
│   ├── templates/tienda/    # Templates de tienda
│   │   ├── dashboard.html
│   │   ├── registrar_venta.html
│   │   ├── historial_ventas.html
│   │   ├── catalogo_productos.html
│   │   ├── login.html
│   │   └── register.html
│   ├── static/css/          # Estilos CSS
│   │   └── style.css
│   ├── admin.py             # Configuración admin
│   ├── apps.py
│   ├── models.py            # Modelos de datos
│   ├── views.py             # Vistas
│   ├── urls.py
│   └── tests.py
│
├── admin_panel/             # Aplicación de panel administrativo
│   ├── migrations/
│   ├── templates/admin_panel/  # Templates de admin
│   │   ├── dashboard.html
│   │   ├── tiendas_list.html
│   │   ├── tienda_detail.html
│   │   ├── crear_editar_tienda.html
│   │   ├── productos_list.html
│   │   ├── crear_editar_producto.html
│   │   ├── usuarios_list.html
│   │   ├── crear_editar_usuario.html
│   │   └── reportes.html
│   ├── static/css/
│   ├── static/js/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py            # Sin modelos propios
│   ├── views.py             # Vistas del admin
│   ├── urls.py
│   └── tests.py
│
├── manage.py                # Script de gestión de Django
├── populate_db.py           # Script para crear datos de prueba
├── requirements.txt         # Dependencias del proyecto
├── db.sqlite3              # Base de datos (se crea al migrar)
└── README.md               # Este archivo
```

---

## 🔧 Modelos de Datos

### Tienda
Representa una sucursal de CityPapa
- `nombre` - Nombre único de la tienda
- `ciudad` - Ubicación
- `direccion` - Dirección completa
- `telefono` - Teléfono de contacto
- `email` - Email
- `activa` - Estado activo/inactivo
- `fecha_creacion` - Fecha de registro

### Producto
Catálogo de productos disponibles
- `nombre` - Nombre del producto
- `descripcion` - Descripción
- `precio` - Precio unitario
- `categoria` - Categoría (hamburguesa, arepa, perro, pizza, bebida, postre, otro)
- `disponible` - Disponible para vender
- `fecha_creacion` - Fecha de registro

### Venta
Registro de cada transacción
- `tienda` - FK a Tienda
- `producto` - FK a Producto
- `cantidad` - Cantidad vendida
- `precio_unitario` - Precio en el momento de venta
- `total` - Total de la venta (cantidad × precio)
- `registrado_por` - FK a User que registró la venta
- `fecha_venta` - Fecha en que ocurrió la venta
- `fecha` - Fecha de creación del registro

### UsuarioTienda
Extensión del usuario de Django con rol y tienda
- `usuario` - OneToOne a User
- `tienda` - FK a Tienda (puede ser null para administradores)
- `rol` - Rol del usuario (administrador, tienda)
- `activo` - Usuario activo/inactivo

---

## 🎯 Funcionalidades URL

### URLs de Autenticación
| URL | Método | Descripción |
|-----|--------|-------------|
| `/` | GET, POST | Login de usuarios |
| `/logout/` | GET | Cerrar sesión |
| `/register/tienda/` | GET, POST | Registro de nueva tienda |

### URLs de Tienda
| URL | Método | Descripción |
|-----|--------|-------------|
| `/tienda/dashboard/` | GET | Dashboard de ventas del día |
| `/tienda/registrar-venta/` | GET, POST | Registrar nueva venta |
| `/tienda/historial-ventas/` | GET | Historial de ventas con filtros |
| `/tienda/catalogo/` | GET | Ver catálogo de productos |

### URLs de Admin Panel
| URL | Método | Descripción |
|-----|--------|-------------|
| `/admin-panel/dashboard/` | GET | Dashboard consolidado |
| `/admin-panel/tiendas/` | GET | Lista de tiendas |
| `/admin-panel/tiendas/crear/` | GET, POST | Crear tienda |
| `/admin-panel/tiendas/<id>/` | GET | Detalle de tienda |
| `/admin-panel/tiendas/<id>/editar/` | GET, POST | Editar tienda |
| `/admin-panel/productos/` | GET | Lista de productos |
| `/admin-panel/productos/crear/` | GET, POST | Crear producto |
| `/admin-panel/productos/<id>/editar/` | GET, POST | Editar producto |
| `/admin-panel/productos/<id>/eliminar/` | POST | Desactivar producto |
| `/admin-panel/usuarios/` | GET | Lista de usuarios |
| `/admin-panel/usuarios/crear/` | GET, POST | Crear usuario |
| `/admin-panel/usuarios/<id>/editar/` | GET, POST | Editar usuario |
| `/admin-panel/reportes/` | GET | Reportes consolidados |
| `/admin-panel/reportes/exportar/` | GET | Exportar a CSV |

---

## 📊 Características Principales

### Para Tiendas 🏪
- ✅ Registro de ventas del día
- ✅ Resumen diario con totales
- ✅ Historial de ventas filtrable por fecha y categoría
- ✅ Visualización de catálogo de productos
- ✅ Gráfico de ventas de últimos 7 días

### Para Administrador 👨‍💼
- ✅ Dashboard consolidado de todas las tiendas
- ✅ Métricas de desempeño por sucursal
- ✅ Gráficos de ventas (línea, barras, doughnut)
- ✅ Top 10 productos más vendidos
- ✅ Gestión completa de tiendas (CRUD)
- ✅ Gestión de catálogo de productos (CRUD)
- ✅ Gestión de usuarios por rol
- ✅ Generador de reportes con filtros avanzados
- ✅ Exportación de datos a CSV

---

## 🔐 Seguridad y Autenticación

- ✅ Autenticación nativa de Django
- ✅ Protección de vistas por rol
- ✅ Las tiendas solo ven sus propios datos
- ✅ Los administradores ven datos consolidados de todas las tiendas
- ✅ Contraseñas hasheadas
- ✅ Protección CSRF en formularios
- ✅ Sesiones seguras

---

## 🛠️ Comandos Útiles

### Crear migraciones
```bash
python manage.py makemigrations
```

### Aplicar migraciones
```bash
python manage.py migrate
```

### Crear superusuario
```bash
python manage.py createsuperuser
```

### Acceder a Django admin
```
http://localhost:8000/admin/
```

### Limpiar base de datos (cuidado)
```bash
python manage.py flush
```

### Recolectar archivos estáticos
```bash
python manage.py collectstatic
```

---

## 📱 Responsive Design

La aplicación es **100% responsive** y funciona correctamente en:
- 📱 Dispositivos móviles (320px+)
- 📲 Tablets (768px+)
- 💻 Escritorios (1024px+)

---

## 🎨 Personalización

### Cambiar colores
Edita las variables CSS en `tienda/static/css/style.css`:
```css
:root {
    --primary: #FF6B00;      /* Cambiar aquí */
    --accent: #FFD600;       /* Cambiar aquí */
    --bg-dark: #0D0D0D;      /* Cambiar aquí */
    /* ... más variables ... */
}
```

### Cambiar zona horaria
En `citypapa/settings.py`:
```python
TIME_ZONE = 'America/Bogota'  # Cambia a tu zona horaria
```

### Cambiar idioma
En `citypapa/settings.py`:
```python
LANGUAGE_CODE = 'es-es'  # Ya está en español
```

---

## 📝 Notas de Desarrollo

- El proyecto usa **SQLite** por defecto para facilitar desarrollo local
- Para producción, se recomienda usar **PostgreSQL**
- Todos los comentarios del código están en **español**
- La separación de archivos sigue las mejores prácticas de Django

---

## 🐛 Solución de Problemas

### Error: "No module named 'django'"
```bash
pip install -r requirements.txt
```

### Error: "ModuleNotFoundError" al migrar
Asegúrate de estar en el directorio correcto y el venv activado.

### Error: Puerto 8000 en uso
```bash
python manage.py runserver 8001
```

### Base de datos corrupta
```bash
python manage.py flush
python manage.py migrate
python manage.py shell < populate_db.py
```

---

## 📄 Licencia

Este proyecto se distribuye bajo licencia MIT.

---

## 👨‍💻 Autor

Desarrollado como sistema completo de gestión para **CityPapa**.

---

## 📞 Soporte

Para reportar problemas o sugerencias, contacta con el equipo de desarrollo.

---

**¡Gracias por usar CityPapa!** 🍔🟠🟡

Versión: **1.0**  
Última actualización: Diciembre 2024
