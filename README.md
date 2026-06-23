# Tema_Foro — Inventario Django (dcrm)

Descripción
-----------
Tema_Foro es un proyecto Django que incluye una aplicación llamada `website` para gestionar un inventario (dcrm). El repositorio contiene la configuración del proyecto Django, modelos, vistas, formularios y plantillas HTML para la interfaz. Está pensado como un proyecto educativo/funcional que puede usarse como base para un sistema de inventario pequeño.

Estado del repositorio
----------------------
- Lenguajes principales: HTML (63.2%), Python (36.8%).
- Ubicación del proyecto Django: `inventario_django/dcrm/`
- App principal: `inventario_django/dcrm/website/`
- Base de datos por defecto: `inventario_django/dcrm/db.sqlite3` (SQLite incluido en el repositorio)
- Archivo de dependencias: `inventario_django/requirements.txt`

Contenido y estructura principal
-------------------------------
- inventario_django/
  - requirements.txt
  - dcrm/
    - manage.py
    - db.sqlite3
    - mysql.py
    - dcrm/
      - __init__.py
      - asgi.py
      - settings.py
      - urls.py
      - wsgi.py
    - website/
      - __init__.py
      - admin.py
      - apps.py
      - forms.py
      - models.py
      - views.py
      - urls.py
      - tests.py
      - templates/         (plantillas HTML)
      - migrations/

Características principales
--------------------------
- CRUD de entidades de inventario (definidas en `website/models.py`).
- Formularios y validaciones centralizadas en `website/forms.py`.
- Vistas (posiblemente basadas en funciones o clases) en `website/views.py`.
- Registro en admin de Django para gestionar modelos (`website/admin.py`).
- Plantillas HTML para interfaz de usuario dentro de `website/templates/`.

Requisitos
----------
- Python 3.8+ (recomendado)
- Virtualenv o entorno virtual similar
- Paquetes listados en `inventario_django/requirements.txt`

Instalación (local)
-------------------
1. Clona el repositorio:
   ```bash
   git clone https://github.com/Salome0119/Tema_Foro.git
   cd Tema_Foro
   ```

2. Entra en el directorio del proyecto Django:
   ```bash
   cd inventario_django/dcrm
   ```

3. Crea y activa un entorno virtual:
   - Linux / macOS:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```
   - Windows (PowerShell):
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```

4. Instala dependencias:
   ```bash
   pip install -r ../requirements.txt
   ```
   Nota: `requirements.txt` está en `inventario_django/requirements.txt`; la ruta en el comando es relativa.

Configuración
-------------
1. Variables de entorno recomendadas (usar un archivo `.env` o exportarlas en el entorno):
   - SECRET_KEY (no dejar la clave real en el repositorio)
   - DEBUG (True/False)
   - ALLOWED_HOSTS (ej.: "localhost,127.0.0.1")
   - DATABASE_URL (si migras a Postgres u otra DB)
   - EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD (si usas correo)

2. Si usas SQLite (por defecto), no necesitas cambiar nada: el archivo `db.sqlite3` ya está en `inventario_django/dcrm/`. Para limpieza de desarrollo, puedes eliminarlo y aplicar migraciones nuevas.

Migraciones y base de datos
--------------------------
1. Genera/Aplica migraciones:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

2. (Opcional) Crea un superusuario para acceder al admin:
   ```bash
   python manage.py createsuperuser
   ```

Ejecución (desarrollo)
----------------------
```bash
python manage.py runserver
```
Luego abre en el navegador: http://127.0.0.1:8000/  
Para acceder al admin: http://127.0.0.1:8000/admin/

Recopilar archivos estáticos (si está configurado)
--------------------------------------------------
Antes de desplegar en producción:
```bash
python manage.py collectstatic
```
Asegúrate de configurar `STATIC_ROOT` en `settings.py` y los ajustes relacionados.

Pruebas
-------
Ejecuta las pruebas definidas en el proyecto:
```bash
python manage.py test
```
(Actualmente hay un archivo `website/tests.py` con pruebas básicas — revisa su contenido y amplíalas según sea necesario).

Despliegue (resumen)
--------------------
- Producción: se recomienda usar Gunicorn + Nginx o un servicio PaaS (Heroku, Render, etc.).
- Configura variables de entorno para `SECRET_KEY`, `DEBUG=False` y `ALLOWED_HOSTS`.
- Usa una base de datos robusta (PostgreSQL) en producción; configura `DATABASES` en `settings.py` o usa `dj-database-url`.
- Considera configurar HTTPS y políticas de seguridad (SECURE_SSL_REDIRECT, SESSION_COOKIE_SECURE, CSRF_COOKIE_SECURE).

Buenas prácticas y seguridad
----------------------------
- Nunca subir `SECRET_KEY` ni credenciales al repositorio. Usa `.env` o variables de entorno.
- No subas la base de datos con datos sensibles. Si `db.sqlite3` contiene datos reales, elimínala antes de publicar.
- Revisa `settings.py` para ver si hay valores por defecto que convengan ser movidos a variables de entorno.
- Añade `python-decouple` o `django-environ` si prefieres manejar variables vía `.env`.


Estructura detallada de la app `website`
----------------------------------------
- `models.py` — definición de modelos (entidades del inventario).
- `forms.py` — formularios y validaciones.
- `views.py` — lógica de las vistas (funciones o clases).
- `urls.py` — rutas específicas de la app.
- `admin.py` — registro y personalización del admin.
- `templates/` — plantillas HTML para páginas públicas e internas.



