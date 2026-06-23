# Sistema de Gestión de Usuarios y Foro - Django CRM

¡Bienvenido/a! Este proyecto es una aplicación web robusta desarrollada en **Django** orientada a la gestión de usuarios tipo CRM, que integra un foro comunitario, un estricto sistema de roles con flujo de aprobación y controles avanzados de acceso administrativo y seguridad.

---

## 🚀 Características Principales

### 🔐 Gestión de Usuarios
* **Autenticación Completa:** Inicio de sesión, cierre de sesión y recuperación de contraseña vía correo electrónico (SMTP).
* **Registro Validado:** Formulario de registro con validaciones estrictas y verificación de unicidad de email.
* **Gestión de Perfil:** Actualización de datos personales (teléfono, dirección, departamento, municipio, código postal).
* **Filtros Avanzados:** Visualización y búsqueda de usuarios por ID y Rol (Administrador, Staff, Normal).

### 👥 Sistema de Roles y Workflow
* **Usuario Normal:** Acceso básico al foro y gestión de sus propias publicaciones.
* **Administrador:** Gestión total de usuarios, visualización de todas las publicaciones, visualización de denuncias y aprobación/rechazo de solicitudes.
* **Rol Pendiente:** Los usuarios que solicitan el rol de Administrador permanecen inactivos o restringidos hasta que un administrador existente apruebe su solicitud a través de un flujo de trabajo dedicado.

### 💬 Foro Comunitario
* **Publicaciones:** Crear, editar y eliminar temas de discusión.
* **Comentarios:** Sistema de respuestas anidadas para fomentar el debate.
* **Reacciones:** Sistema de "Me gusta" / "No me gusta" con restricción de una sola reacción por usuario.
* **Moderación:** Denuncia de publicaciones inapropiadas (visibles exclusivamente por el equipo administrador).
* **Paginación:** Listados optimizados con paginación de 10 ítems por página.

---

## 📐 Arquitectura del Proyecto

El proyecto mantiene la estructura clásica y limpia de Django:

dcrm/
├── dcrm/                    # Configuración principal del proyecto
│   ├── settings.py          # Configuraciones globales, base de datos y seguridad
│   ├── urls.py              # Enrutamiento raíz
│   ├── wsgi.py
│   └── asgi.py
└── website/                 # Aplicación principal del CRM y Foro
    ├── models.py            # Modelos de datos (Estructura de la BD)
    ├── views.py             # Lógica de negocio y control de flujo
    ├── forms.py             # Formularios con validaciones personalizadas
    ├── urls.py              # Rutas específicas de la aplicación
    ├── admin.py             # Configuración del panel de administración nativo
    ├── migrations/          # Historial de migraciones de la BD
    └── templates/           # Plantillas HTML estructuradas

---

## 🗄️ Modelos de Datos

El sistema se compone de los siguientes modelos principales:

* **Perfil:** Extensión del modelo nativo de Django (User) que añade campos de ubicación, contacto y el sistema de roles (Usuario, Admin, Pendiente).
* **SolicitudAdministrador:** Registro y seguimiento del estado (Pendiente, Aprobada, Rechazada) de los usuarios que aspiran al rol administrativo.
* **TemaForo:** Almacena el título, contenido, autor y marcas de tiempo de los hilos del foro.
* **ComentarioForo:** Estructura de las respuestas asociadas a cada tema.
* **ReaccionForo:** Control de interacciones únicas por usuario (votos positivos/negativos).
* **DenunciaForo:** Reportes de publicaciones con su respectivo motivo de moderación.

---

## 🛣️ Rutas Disponibles (Endpoints)

| Ruta | Vista | Descripción | Restricción |
| :--- | :--- | :--- | :--- |
| / | home | Dashboard principal con listado de usuarios | Autenticado |
| /login/ | login_user | Autenticación de usuarios | Público |
| /logout/ | logout_user | Cierre de sesión de usuario | Autenticado |
| /register/ | register | Registro de nuevos usuarios al sistema | Público |
| /perfil/actualizar/ | profile_update | Actualización de información del perfil propio | Autenticado |
| /administrador/solicitudes-admin/ | solicitudes_admin | Panel de aprobación de solicitudes de rol | Solo Admin |
| /foro/ | foro | Foro principal con publicaciones y respuestas | Autenticado |
| /publicaciones/ | publicaciones_usuario | Listado de publicaciones para usuarios comunes | Autenticado |
| /administrador/publicaciones/ | publicaciones_admin | Panel de control de todas las publicaciones | Solo Admin |
| /add-record/ | add_record | Crear un nuevo usuario manualmente | Solo Admin |
| /delete-record/<pk>/ | delete_record | Eliminar un usuario del sistema | Solo Admin |

---

## 🔒 Seguridad Implementada

### Middleware y Cabeceras
* **SecurityMiddleware:** Configuración de encabezados HSTS y redirección forzada a HTTPS.
* **CsrfViewMiddleware:** Protección integrada contra ataques de Falsificación de Petición en Sitios Cruzados (CSRF).
* **XFrameOptionsMiddleware:** Mitigación de ataques de Clickjacking.
* **SECURE_CONTENT_TYPE_NOSNIFF:** Previene el sniffing de tipo MIME.

### Cookies Seguras (Configuradas en settings.py)
* SESSION_COOKIE_SECURE = True (Transmisión solo vía HTTPS)
* CSRF_COOKIE_SAMESITE = 'Lax' (Restringe el envío en peticiones cross-site)
* CSRF_COOKIE_HTTPONLY = True (Inaccesible desde scripts de JavaScript)
* SESSION_COOKIE_HTTPONLY = True (Protege la sesión contra ataques XSS)

### Validaciones y Control de Acceso
* **Políticas de Contraseñas:** Validaciones personalizadas en formularios (mínimo 8 caracteres, combinación de mayúsculas, minúsculas y números).
* **Restricción de Identidad:** Nombre de usuario único (mínimo 4 caracteres, alfanumérico y guiones bajos) y verificación estricta de correo electrónico único.
* **Decoradores Personalizados:** Uso de @admin_required y la función auxiliar usuario_es_admin() para blindar las vistas críticas del backend.
* **Control de Propiedad:** El sistema valida rigurosamente que solo el autor original de una publicación (o un administrador) tenga permisos de modificación o eliminación.

---

## 🛠️ Requisitos e Instalación

### Requisitos Previos
* Python 3.x
* Django 4.x
* Servidor MySQL

### Pasos para la Configuración Local

1. Clonar el repositorio:
   git clone [repo-url]
   cd dcrm

2. Crear y activar el entorno virtual:
   # En Windows:
   python -m venv env
   .\env\Scripts\activate

   # En Linux/macOS:
   python3 -m venv env
   source env/bin/activate

3. Instalar las dependencias:
   pip install django pymysql

4. Configurar la Base de Datos:
   Asegúrate de tener un servidor MySQL corriendo y crea una base de datos llamada 'cliente'. La configuración por defecto en settings.py es:

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

5. Ejecutar migraciones:
   python manage.py migrate

6. Iniciar el servidor de desarrollo:
   python manage.py runserver

   Visita [http://127.0.0.1:8000/](http://127.0.0.1:8000/) en tu navegador.

---

## 📧 Configuración de Email (Notificaciones)

El sistema utiliza el protocolo SMTP de Gmail para gestionar el flujo de recuperación de contraseñas y alertas del workflow de administración.

> NOTA: No olvides configurar tus credenciales de entorno en el archivo settings.py utilizando variables de entorno seguras o agregando tus parámetros correspondientes (EMAIL_HOST_USER y EMAIL_HOST_PASSWORD mediante contraseñas de aplicación de Google).
