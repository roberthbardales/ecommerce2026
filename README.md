# 🛒 E-Commerce 2026

Plataforma de comercio electrónico completa desarrollada con Django, orientada a la venta de productos con pasarela de pagos integrada mediante **Mercado Pago**.

---

## 📋 Descripción

**E-Commerce 2026** es una aplicación web fullstack que permite a los usuarios navegar un catálogo de productos, agregar artículos a un carrito de compras, gestionar pedidos y realizar pagos de forma segura a través de la API de Mercado Pago. El proyecto sigue una arquitectura modular basada en apps de Django con una capa de servicios desacoplada de las vistas (patrón CBV + Services).

---

## 🛠️ Tecnologías utilizadas

| Capa | Tecnología |
|------|-----------|
| **Backend** | Django 3.2 |
| **Base de datos** | PostgreSQL (psycopg2) |
| **Frontend** | Bootstrap 5, jQuery, Font Awesome |
| **Pagos** | Mercado Pago Checkout API |
| **Imágenes** | Pillow, django-admin-thumbnails |
| **Despliegue** | Gunicorn + Nginx |
| **Idioma** | Español (Perú) |

---

## ✨ Principales funcionalidades

- **🔐 Autenticación de usuarios** — Registro, inicio de sesión, cierre de sesión, activación de cuenta por email, recuperación de contraseña y cambio de contraseña.
- **👤 Gestión de perfil** — Edición de datos personales, dirección, foto de perfil y visualización del dashboard.
- **🏪 Catálogo de productos** — Listado paginado con filtros por categoría y rango de precio, detalle de producto con galería de imágenes.
- **🔍 Búsqueda** — Búsqueda de productos por nombre o descripción.
- **⭐ Reseñas y calificaciones** — Los usuarios autenticados pueden dejar reseñas y calificar productos.
- **🛒 Carrito de compras** — Funcional para usuarios autenticados y anónimos (sesión), con soporte para variaciones (color, talla), agregar, eliminar y modificar cantidades.
- **💳 Pasarela de pagos** — Integración con Mercado Pago Checkout API (modo real y modo simulado para desarrollo).
- **📦 Gestión de pedidos** — Creación de órdenes, generación de números de orden, confirmación por email y seguimiento de estados.
- **🖥️ Panel de administración** — Django Admin con gestión de usuarios, categorías, productos, pedidos y pagos.
- **📦 Carga de datos de prueba** — Fixtures JSON para poblar categorías, productos y usuarios de ejemplo.

---

## 📁 Estructura del proyecto

```
ecommerce2026/
├── applications/               # Apps modulares de Django
│   ├── carts/                  # Carrito de compras
│   │   ├── models.py           #   Modelos: Cart, CartItem
│   │   ├── services.py         #   Lógica de negocio del carrito
│   │   ├── views.py            #   Vistas: agregar, eliminar, checkout
│   │   ├── urls.py             #   Rutas del carrito
│   │   └── context_processors.py
│   ├── category/               # Categorías de productos
│   │   ├── models.py           #   Modelo: Category
│   │   └── context_processors.py
│   ├── home/                   # Página de inicio
│   │   └── views.py            #   Vista: productos destacados
│   ├── orders/                 # Pedidos y pagos
│   │   ├── models.py           #   Modelos: Payment, Order, OrderProduct
│   │   ├── services.py         #   Lógica de Mercado Pago y órdenes
│   │   ├── views.py            #   Vistas: place order, payments, order complete
│   │   └── forms.py            #   Formulario de orden
│   ├── store/                  # Tienda / catálogo
│   │   ├── models.py           #   Modelos: Product, Variation, ReviewRating, ProductGallery
│   │   ├── services.py         #   Lógica de productos, búsqueda, reseñas
│   │   ├── views.py            #   Vistas: listado, detalle, búsqueda, reviews
│   │   └── forms.py            #   Formulario de reseñas
│   └── users/                  # Usuarios y autenticación
│       ├── models.py           #   Modelos: Account (custom user), UserProfile
│       ├── services.py         #   Lógica de registro, activación, cambio de contraseña
│       ├── views.py            #   Vistas: registro, login, dashboard, perfil
│       ├── forms.py            #   Formularios de registro y perfil
│       └── mixins.py           #   Mixins: ActiveAccountMixin, StaffRequiredMixin
├── ecommerce/                  # Configuración del proyecto Django
│   ├── settings.py             #   Configuración principal
│   ├── urls.py                 #   URLs raíz
│   ├── wsgi.py
│   └── asgi.py
├── templates/                  # Plantillas HTML
│   ├── base.html               #   Plantilla base (Bootstrap 5)
│   ├── includes/               #   Navbar, footer
│   ├── home.html
│   ├── carts/                  #   Carrito, checkout
│   ├── orders/                 #   Pagos, confirmación
│   ├── store/                  #   Tienda, detalle de producto
│   └── users/                  #   Login, registro, dashboard, perfil
├── static/                     # Archivos estáticos
│   ├── css/                    #   Estilos custom + Bootstrap
│   ├── js/                     #   Scripts (jQuery)
│   ├── images/                 #   Imágenes estáticas
│   └── fonts/                  #   Fuentes (Font Awesome)
├── media/                      # Archivos subidos por usuarios
├── fixture_safe.json           # Datos de prueba (categorías, productos, usuarios)
├── manage.py                   # Script de gestión de Django
├── requeriments.txt            # Dependencias de Python
├── .env.example                # Plantilla de variables de entorno
└── .gitignore
```

---

## 📦 Requisitos

- **Python** 3.10 o superior
- **PostgreSQL** 12 o superior
- **pip** (gestor de paquetes de Python)
- Cuenta en [Mercado Pago](https://www.mercadopago.com/) (para pagos en producción)

---

## 🚀 Instrucciones de instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/ecommerce2026.git
cd ecommerce2026
```

### 2. Crear entorno virtual

```bash
python -m venv venv
# Linux/macOS
source venv/bin/activate
# Windows
venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requeriments.txt
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
```

Edita el archivo `.env` con tus credenciales reales (ver [Variables de entorno](#-variables-de-entorno)).

### 5. Crear la base de datos

```sql
CREATE DATABASE db_ecommerce2026;
CREATE USER tu_usuario WITH PASSWORD 'tu_contraseña';
ALTER ROLE tu_usuario SET client_encoding TO 'utf8';
ALTER ROLE tu_usuario SET default_transaction_isolation TO 'read committed';
ALTER ROLE tu_usuario SET timezone TO 'America/Lima';
GRANT ALL PRIVILEGES ON DATABASE db_ecommerce2026 TO tu_usuario;
```

### 6. Ejecutar migraciones

```bash
python manage.py migrate
```

### 7. Crear superusuario

```bash
python manage.py createsuperuser
```

### 8. (Opcional) Cargar datos de prueba

```bash
python manage.py loaddata fixture_safe.json
```

---

## 🔑 Variables de entorno

Copia `.env.example` a `.env` y completa los valores:

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `SECRET_KEY` | Clave secreta de Django (genera una nueva) | `django-insecure-xxxxx` |
| `DEBUG` | Modo depuración (`True` en desarrollo) | `True` |
| `ALLOWED_HOSTS` | Hosts permitidos (separados por coma) | `localhost,127.0.0.1` |
| `DB_NAME` | Nombre de la base de datos PostgreSQL | `db_ecommerce2026` |
| `DB_USER` | Usuario de PostgreSQL | `tu_usuario` |
| `DB_PASSWORD` | Contraseña de PostgreSQL | `tu_contraseña` |
| `DB_HOST` | Host de PostgreSQL | `localhost` |
| `DB_PORT` | Puerto de PostgreSQL | `5432` |
| `MP_DEV_MODE` | Modo simulado de Mercado Pago (`True`/`False`) | `True` |
| `MP_PUBLIC_KEY` | Llave pública de Mercado Pago | `APP_USR-xxxxx` |
| `MP_ACCESS_TOKEN` | Token de acceso de Mercado Pago | `APP_USR-xxxxx` |
| `EMAIL_BACKEND` | Backend de correo Django | `django.core.mail.backends.console.EmailBackend` |

---

## ▶️ Ejecutar en modo desarrollo

```bash
python manage.py runserver
```

La aplicación estará disponible en: **http://localhost:8000**

Panel de administración: **http://localhost:8000/admin/**

### Datos de prueba (fixture_safe.json)

| Tipo | Datos |
|------|-------|
| Categorías | Computadoras, Ropa de Verano, Música y Media, Muebles de Oficina, Accesorios Tech |
| Usuarios | Juan Perez, Maria Garcia, Carlos Lopez |
| Productos | 15 productos de ejemplo con imágenes y variaciones |

---

## 🚢 Despliegue en producción

### Preparar el entorno

```bash
# En el servidor
sudo apt update && sudo apt install python3-pip python3-venv postgresql nginx
python3 -m venv venv
source venv/bin/activate
pip install -r requeriments.txt
pip install gunicorn
```

### Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con valores de producción:
# DEBUG=False
# ALLOWED_HOSTS=tu-dominio.com
# MP_DEV_MODE=False
```

### Recopilar archivos estáticos

```bash
python manage.py collectstatic --noinput
```

### Configurar Gunicorn

Crear archivo `gunicorn_config.py`:

```python
bind = "127.0.0.1:8000"
workers = 3
accesslog = "access.log"
errorlog = "error.log"
```

Ejecutar:

```bash
gunicorn -c gunicorn_config.py ecommerce.wsgi:application
```

### Configurar Nginx

```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    location /static/ {
        alias /ruta/al/proyecto/staticfiles/;
    }

    location /media/ {
        alias /ruta/al/proyecto/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://127.0.0.1:8000;
    }
}
```

### Configurar SSL (recomendado)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d tu-dominio.com
```

---

## 📄 Licencia

Este proyecto está bajo la licencia **MIT**. Consulta el archivo [LICENSE](LICENSE) para más detalles.

---

> **Nota de seguridad:** Este proyecto utiliza variables de entorno para almacenar credenciales sensibles. Nunca commitees archivos `.env` al repositorio. El archivo `.env.example` contiene la estructura necesaria sin valores reales.
