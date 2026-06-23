Sistema de Gestión de Usuarios y Foro - Django CRM
Aplicación web desarrollada en Django para gestión de usuarios con foro integrado, sistema de roles y control de acceso administrativo.

Características Principales
🔐 Gestión de Usuarios
Autenticación completa: Login, logout y recuperación de contraseña vía email
Registro de usuarios: Formulario con validación de datos y verificación de email único
Gestión de perfil: Actualización de información personal (teléfono, dirección, departamento, municipio, código postal)
Filtros de usuarios: Visualización y búsqueda por ID y rol (administrador, staff, normal)
👥 Sistema de Roles
Usuario normal: Acceso básico al foro y gestión de publicaciones propias
Administrador: Aprobación/rechazo de solicitudes, gestión de usuarios, visualización de todas las publicaciones
Rol pendiente: Usuarios que solicitan ser administradores permanecen inactivos hasta aprobación
Workflow de aprobación: Los usuarios que solicitan rol admin deben ser aprobados por administradores existentes
💬 Foro Comunitario
Publicaciones: Crear, editar y eliminar temas de discusión
Comentarios: Sistema de respuestas anidadas a publicaciones
Reacciones: "Me gusta" / "No me gusta" con restricción de una reacción por usuario
Denuncias: Reportar publicaciones inapropiadas (solo administradores pueden ver denuncias)
Paginación: Listados paginados (10 items por página)
Arquitectura del Proyecto
dcrm/
├── dcrm/                    # Configuración principal
│   ├── settings.py         # Configuraciones y seguridad
│   ├── urls.py             # Rutas principales
│   ├── wsgi.py
│   └── asgi.py
└── website/                 # Aplicación principal
    ├── models.py          # Modelos de datos
    ├── views.py           # Lógica de negocio
    ├── forms.py           # Formularios con validaciones
    ├── urls.py            # Rutas de la aplicación
    ├── admin.py           # Registro en admin
    ├── migrations/        # Migraciones de base de datos
    └── templates/         # Plantillas HTML
Modelos de Datos
Perfil
Extensión del modelo User con información adicional y sistema de roles (usuario, admin, pendiente).

SolicitudAdministrador
Gestión de solicitudes de rol administrador con estados: pendiente, aprobada, rechazada.

TemaForo
Publicaciones del foro con título, contenido, autor y timestamp.

ComentarioForo
Comentarios asociados a temas de foro con autor y fecha.

ReaccionForo
Sistema de reacciones (me gusta/no me gusta) con restricción única por usuario/tema.

DenunciaForo
Denuncias de publicaciones con motivo explicativo.

Rutas Disponibles
Ruta	Vista	Descripción
/	home	Dashboard principal con listado de usuarios
/login/	login_user	Autenticación de usuarios
/logout/	logout_user	Cierre de sesión
/register/	register	Registro de nuevos usuarios
/perfil/actualizar/	profile_update	Actualización de perfil propio
/administrador/solicitudes-admin/	solicitudes_admin	Panel de solicitudes (admin)
/foro/	foro	Foro principal con publicaciones
/publicaciones/	publicaciones_usuario	Publicaciones para usuarios normales
/administrador/publicaciones/	publicaciones_admin	Todas las publicaciones (admin)
/add-record/	add_record	Crear nuevo usuario (admin)
/delete-record/<pk>/	delete_record	Eliminar usuario (admin)
Seguridad Implementada
Middleware
SecurityMiddleware: Encabezados HSTS y redirección SSL
CsrfViewMiddleware: Protección contra ataques CSRF
XFrameOptionsMiddleware: Prevención de clickjacking
Cookies Seguras
SESSION_COOKIE_SECURE: HTTPS only
CSRF_COOKIE_SAMESITE: Lax (previene envío en cross-site)
CSRF_COOKIE_HTTPONLY: Inaccesible vía JavaScript
SESSION_COOKIE_HTTPONLY: Inaccesible vía JavaScript
SECURE_CONTENT_TYPE_NOSNIFF: Previene MIME-sniffing
Validaciones de Formulario
Contraseñas: mínimo 8 caracteres, mayúscula, minúscula, número
Username: mínimo 4 caracteres, solo alfanuméricos y guiones bajos
Email único en sistema
Control de Acceso
Decorador @admin_required: Protege vistas administrativas
Función usuario_es_admin(): Verifica permisos de administrador
Control de propiedad: Solo el autor o admin pueden editar publicaciones
Requisitos
Python 3.x
Django 4.x
MySQL (base de datos configurada en settings.py)
Configuración
# Clonar repositorio
git clone [repo-url]

# Crear entorno virtual
python -m venv env

# Instalar dependencias
pip install django pymysql

# Migrar base de datos
python manage.py migrate

# Ejecutar servidor de desarrollo
python manage.py runserver
Credenciales de Base de Datos (MySQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'cliente',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
Email SMTP (Gmail)
Configurado para envío de correos de recuperación y notificaciones de solicitud de administrador. Se requiere credenciales en settings.py.
