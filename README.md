

### 1. Template Method (Plantillas Django)
**Ubicación:** `dcrm/website/templates/base.html:18-22`

`base.html` define el esqueleto con `{% block content %}{% endblock %}`, y las plantillas hijas (`home.html`, `publicaciones.html`, `foro.html`, etc.) sobrescriben ese bloque. El patrón Template Method define la estructura fija en el padre y delega la implementación específica a las subclases.

---

### 2. Decorator (Decoradores de Vista)
**Ubicación:** `dcrm/website/views.py:132-142`

Un decorador personalizado `admin_required()` envuelve la función vista añadiendo chequeos de autenticación y rol sin modificar la lógica original de la vista. Se combina con decoradores de Django como `@require_http_methods(["POST"])` (líneas 247-257, 260-270, etc.), permitiendo apilar comportamiento de forma declarativa.

---

### 3. Strategy (Herencia de Formularios)
**Ubicación:** `dcrm/website/forms.py:49-214`

`RegisterForm` (líneas 49-197) define la estrategia base de validación de registro. `AdminRegisterForm` (líneas 199-214) hereda de ella y personaliza el comportamiento (campo `rol` y su widget). Ambas son intercambiables y son usadas por diferentes vistas según el contexto.

---

### 4. Facade (Funciones Context Builders)
**Ubicación:** `dcrm/website/views.py:58-108`

La función `obtener_publicaciones_foro_context()` actúa como fachada: oculta la complejidad de múltiples consultas a `TemaForo`, `ComentarioForo`, `DenunciaForo`, paginación y transformaciones de datos. Las vistas (`publicaciones_usuario` línea 661, `publicaciones_admin` línea 671) solo pasan parámetros y reciben un diccionario listo para usar.
