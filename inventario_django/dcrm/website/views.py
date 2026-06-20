from collections import defaultdict
from functools import wraps

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.decorators.http import require_http_methods

from .forms import AdminRegisterForm, ComentarioForoForm, DenunciaForoForm, LoginForm, PasswordResetConfirmForm, PasswordResetRequestForm, PerfilForm, RegisterForm, TemaForoForm, UserEditForm
from .models import ComentarioForo, DenunciaForo, Perfil, ReaccionForo, SolicitudAdministrador, TemaForo


REACCION_PUBLICACION_CHOICES = {
    'me-gusta': ReaccionForo.ME_GUSTA,
    'no-me-gusta': ReaccionForo.NO_ME_GUSTA,
}


def obtener_perfil(usuario):
    try:
        return usuario.perfil
    except (AttributeError, Perfil.DoesNotExist):
        return None


def usuario_es_admin(usuario):
    if not usuario.is_authenticated:
        return False
    perfil = obtener_perfil(usuario)
    return usuario.is_staff or usuario.is_superuser or bool(perfil and perfil.es_admin())


def etiqueta_rol(usuario):
    perfil = obtener_perfil(usuario)
    if perfil:
        return perfil.etiqueta_rol()
    if usuario.is_superuser:
        return 'Superusuario'
    if usuario.is_staff:
        return 'Administrador'
    return 'Usuario normal'


def puede_editar_tema_foro(tema, usuario):
    return usuario_es_admin(usuario) or tema.id_usuario_id == usuario.pk


def obtener_publicaciones_foro_context(request, es_admin, titulo_pagina, descripcion):
    publicaciones = TemaForo.objects.select_related('id_usuario').annotate(
        me_gusta=Count('reacciones', filter=Q(reacciones__tipo=ReaccionForo.ME_GUSTA), distinct=True),
        no_me_gusta=Count('reacciones', filter=Q(reacciones__tipo=ReaccionForo.NO_ME_GUSTA), distinct=True),
        comentarios_count=Count('comentarios', distinct=True)
    )

    paginator = Paginator(publicaciones, 10)
    publicaciones_paginadas = paginator.get_page(request.GET.get('page'))
    publicaciones_lista = list(publicaciones_paginadas.object_list)
    ids_publicaciones = [publicacion.pk for publicacion in publicaciones_lista]

    comentarios_por_publicacion = defaultdict(list)
    reacciones_por_publicacion = {}
    denuncias_por_publicacion = defaultdict(list)

    if ids_publicaciones:
        comentarios = ComentarioForo.objects.select_related('id_usuario').filter(
            id_tema_id__in=ids_publicaciones
        ).order_by('fecha_comentario')
        for comentario in comentarios:
            comentarios_por_publicacion[comentario.id_tema_id].append(comentario)

        denuncias = DenunciaForo.objects.select_related('id_usuario').filter(
            id_tema_id__in=ids_publicaciones
        ).order_by('-fecha_denuncia')
        for denuncia in denuncias:
            denuncias_por_publicacion[denuncia.id_tema_id].append(denuncia)

        reacciones_usuario = ReaccionForo.objects.filter(
            id_tema_id__in=ids_publicaciones,
            id_usuario=request.user
        ).values('id_tema_id', 'tipo')
        reacciones_por_publicacion = {
            reaccion['id_tema_id']: reaccion['tipo']
            for reaccion in reacciones_usuario
        }

    for publicacion in publicaciones_lista:
        publicacion.comentarios_lista = comentarios_por_publicacion.get(publicacion.pk, [])
        publicacion.denuncias_lista = denuncias_por_publicacion.get(publicacion.pk, [])
        publicacion.usuario_reaccion = reacciones_por_publicacion.get(publicacion.pk)

    return {
        'publicaciones': publicaciones_lista,
        'publicaciones_paginadas': publicaciones_paginadas,
        'titulo_pagina': titulo_pagina,
        'descripcion': descripcion,
        'es_admin': es_admin,
        'rol_usuario': etiqueta_rol(request.user),
    }


def aplicar_rol(usuario, rol):
    es_admin = rol == Perfil.ROL_ADMIN
    usuario.is_staff = es_admin
    usuario.is_superuser = False
    usuario.save()
    perfil = obtener_perfil(usuario)
    if perfil:
        perfil.rol = rol
        perfil.save()


def datos_perfil_desde_post(request):
    return {
        'telefono': request.POST.get('telefono', ''),
        'direccion': request.POST.get('direccion', ''),
        'departamento': request.POST.get('departamento', ''),
        'municipio': request.POST.get('municipio', ''),
        'codigo_postal': request.POST.get('codigo_postal', ''),
    }


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Debes iniciar sesión para continuar.')
            return redirect('login')
        if not usuario_es_admin(request.user):
            messages.error(request, 'No tienes permisos de administrador.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


def obtener_correo_administrador():
    correo = settings.ADMIN_AUTH_EMAIL or (settings.ADMINS[0][1] if settings.ADMINS else '')
    if correo:
        return correo
    usuario_admin = User.objects.filter(is_superuser=True).order_by('id').first()
    return usuario_admin.email if usuario_admin and usuario_admin.email else ''


def enviar_correo_solicitud_admin(request, solicitud):
    destinatario = obtener_correo_administrador()
    if not destinatario:
        return False

    aprobar_url = request.build_absolute_uri(reverse('aprobar_admin', args=[solicitud.pk]))
    rechazar_url = request.build_absolute_uri(reverse('rechazar_admin', args=[solicitud.pk]))
    asunto = 'Nueva solicitud de acceso administrador'
    mensaje = (
        f'Se ha solicitado acceso de administrador para el usuario {solicitud.user.username}.\n\n'
        f'Nombre: {solicitud.user.get_full_name() or "-"}\n'
        f'Correo: {solicitud.user.email}\n'
        f'Usuario: {solicitud.user.username}\n\n'
        f'Aprobar: {aprobar_url}\n'
        f'Rechazar: {rechazar_url}'
    )
    try:
        send_mail(asunto, mensaje, settings.DEFAULT_FROM_EMAIL, [destinatario], fail_silently=False)
    except Exception:
        return False
    return True


def enviar_correo_decision_admin(solicitud, aprobada):
    if not solicitud.user.email:
        return False
    asunto = 'Solicitud de administrador aprobada' if aprobada else 'Solicitud de administrador rechazada'
    mensaje = (
        f'Hola {solicitud.user.username},\n\n'
        f'Tu solicitud para acceder como administrador ha sido {"aprobada" if aprobada else "rechazada"}.\n\n'
        f'{"Ahora puedes iniciar sesión con permisos de administrador." if aprobada else "Puedes iniciar sesión con permisos de usuario normal."}'
    )
    try:
        send_mail(asunto, mensaje, settings.DEFAULT_FROM_EMAIL, [solicitud.user.email], fail_silently=False)
    except Exception:
        return False
    return True


def crear_solicitud_admin(request, user):
    perfil = Perfil.objects.get_or_create(user=user)[0]
    perfil.rol = Perfil.ROL_PENDIENTE
    perfil.save()
    user.is_active = False
    user.is_staff = False
    user.is_superuser = False
    user.save()
    solicitud, _ = SolicitudAdministrador.objects.get_or_create(
        user=user,
        defaults={
            'solicitante': user,
            'estado': SolicitudAdministrador.PENDIENTE,
        }
    )
    enviar_correo_solicitud_admin(request, solicitud)


def aprobar_solicitud_admin(request, solicitud):
    solicitud.estado = SolicitudAdministrador.APROBADA
    solicitud.fecha_resolucion = timezone.now()
    solicitud.resuelto_por = request.user
    solicitud.save()
    perfil = Perfil.objects.get_or_create(user=solicitud.user)[0]
    perfil.rol = Perfil.ROL_ADMIN
    perfil.save()
    solicitud.user.is_active = True
    solicitud.user.is_staff = True
    solicitud.user.is_superuser = False
    solicitud.user.save()


def rechazar_solicitud_admin(request, solicitud):
    solicitud.estado = SolicitudAdministrador.RECHAZADA
    solicitud.fecha_resolucion = timezone.now()
    solicitud.resuelto_por = request.user
    solicitud.save()
    perfil = Perfil.objects.get_or_create(user=solicitud.user)[0]
    perfil.rol = Perfil.ROL_USUARIO
    perfil.save()
    solicitud.user.is_active = True
    solicitud.user.is_staff = False
    solicitud.user.is_superuser = False
    solicitud.user.save()


@admin_required
def solicitudes_admin(request):
    solicitudes = SolicitudAdministrador.objects.select_related('user', 'resuelto_por').order_by('-fecha_solicitud')
    return render(request, 'solicitudes_admin.html', {
        'solicitudes': solicitudes,
        'rol_usuario': etiqueta_rol(request.user),
    })


@admin_required
@require_http_methods(["POST"])
def aprobar_admin(request, pk):
    solicitud = get_object_or_404(SolicitudAdministrador, pk=pk)
    if request.method == 'POST':
        aprobar_solicitud_admin(request, solicitud)
        if enviar_correo_decision_admin(solicitud, True):
            messages.success(request, 'Solicitud aprobada correctamente')
        else:
            messages.warning(request, 'Solicitud aprobada, pero no se pudo enviar el correo de notificación.')
    return redirect('solicitudes_admin')


@admin_required
@require_http_methods(["POST"])
def rechazar_admin(request, pk):
    solicitud = get_object_or_404(SolicitudAdministrador, pk=pk)
    if request.method == 'POST':
        rechazar_solicitud_admin(request, solicitud)
        if enviar_correo_decision_admin(solicitud, False):
            messages.success(request, 'Solicitud rechazada correctamente')
        else:
            messages.warning(request, 'Solicitud rechazada, pero no se pudo enviar el correo de notificación.')
    return redirect('solicitudes_admin')


def home(request):
    if not request.user.is_authenticated:
        return render(request, 'login.html', {})

    es_admin = usuario_es_admin(request.user)
    usuarios = User.objects.all().order_by('-date_joined')

    if es_admin:
        id_filtro = request.GET.get('id')
        rol_filtro = request.GET.get('rol')

        if id_filtro:
            usuarios = usuarios.filter(id=id_filtro)

        if rol_filtro == 'staff':
            usuarios = usuarios.filter(is_staff=True)
        elif rol_filtro == 'superuser':
            usuarios = usuarios.filter(is_superuser=True)
        elif rol_filtro == 'normal':
            usuarios = usuarios.filter(is_staff=False, is_superuser=False)
    else:
        usuarios = usuarios.filter(pk=request.user.pk)
        id_filtro = None
        rol_filtro = None

    paginator = Paginator(usuarios, 10)
    page_number = request.GET.get('page')
    usuarios_paginados = paginator.get_page(page_number)
    usuarios_lista = list(usuarios_paginados.object_list)
    perfiles = Perfil.objects.filter(user__in=[usuario.pk for usuario in usuarios_lista])
    perfiles_por_usuario = {perfil.user_id: perfil for perfil in perfiles}
    for usuario in usuarios_lista:
        usuario.perfil_admin = perfiles_por_usuario.get(usuario.pk)

    context = {
        'usuarios': usuarios_paginados,
        'id_filtro': id_filtro,
        'rol_filtro': rol_filtro,
        'es_admin': es_admin,
        'rol_usuario': etiqueta_rol(request.user),
    }
    return render(request, 'home.html', context)


def customer_record(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    if not usuario_es_admin(request.user) and usuario.pk != request.user.pk:
        messages.error(request, 'No tienes permiso para ver este usuario.')
        return redirect('home')
    return render(request, 'customer_record.html', {
        'usuario': usuario,
        'rol_usuario': etiqueta_rol(usuario),
    })


def customer_update(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    if not usuario_es_admin(request.user):
        messages.error(request, 'No tienes permisos de administrador.')
        return redirect('home')

    perfil = Perfil.objects.get_or_create(user=usuario)[0]

    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=usuario, prefix='user')
        perfil_form = PerfilForm(request.POST, instance=perfil, prefix='perfil')
        if user_form.is_valid() and perfil_form.is_valid():
            user_form.save()
            perfil_form.save()
            messages.success(request, 'Usuario actualizado correctamente')
            return redirect('home')
        for form_errors in [user_form.errors, perfil_form.errors]:
            for field, errors in form_errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        user_form = UserEditForm(instance=usuario, prefix='user')
        perfil_form = PerfilForm(instance=perfil, prefix='perfil')

    return render(request, 'customer_update.html', {
        'form': user_form,
        'perfil_form': perfil_form,
        'usuario': usuario,
        'rol_usuario': etiqueta_rol(usuario),
    })


def login_user(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data.get('user')
            login(request, user)
            if usuario_es_admin(user):
                messages.success(request, 'Bienvenido administrador.')
            else:
                messages.success(request, 'Bienvenido usuario normal.')
            return redirect('home')
        return render(request, 'login.html', {'form': form})

    form = LoginForm()
    return render(request, 'login.html', {'form': form})


def logout_user(request):
    logout(request)
    messages.success(request, 'Cerraste sesion correctamente')
    return redirect('login')


def recuperar_contrasena(request):
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            usuarios = User.objects.filter(email__iexact=email, is_active=True)
            correo_enviado = False
            if usuarios.exists():
                for usuario in usuarios:
                    uid = urlsafe_base64_encode(force_bytes(usuario.pk))
                    token = default_token_generator.make_token(usuario)
                    reset_url = request.build_absolute_uri(reverse('password_reset_confirm', args=[uid, token]))
                    asunto = 'Recuperación de contraseña'
                    mensaje = (
                        f'Hola {usuario.username},\n\n'
                        f'Has solicitado recuperar tu contraseña.\n\n'
                        f'Usa este enlace para crear una nueva contraseña:\n{reset_url}\n\n'
                        f'Si no solicitaste este cambio, puedes ignorar este correo.'
                    )
                    try:
                        send_mail(asunto, mensaje, settings.DEFAULT_FROM_EMAIL, [usuario.email], fail_silently=False)
                        correo_enviado = True
                    except Exception:
                        correo_enviado = False
            if correo_enviado:
                messages.success(request, 'Se envió un enlace de recuperación a tu correo.')
            else:
                messages.warning(request, 'No se pudo enviar el correo de recuperación. Verifica la configuración SMTP.')
            return redirect('login')
    else:
        form = PasswordResetRequestForm()
    return render(request, 'password_reset_request.html', {
        'form': form,
        'rol_usuario': etiqueta_rol(request.user) if request.user.is_authenticated else 'Usuario normal',
    })


def recuperar_contrasena_confirmar(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        usuario = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        usuario = None

    if usuario is not None and default_token_generator.check_token(usuario, token):
        if request.method == 'POST':
            form = PasswordResetConfirmForm(request.POST)
            if form.is_valid():
                usuario.set_password(form.cleaned_data.get('new_password1'))
                usuario.save()
                messages.success(request, 'Contraseña actualizada correctamente. Ahora puedes iniciar sesión.')
                return redirect('login')
        else:
            form = PasswordResetConfirmForm()
        return render(request, 'password_reset_confirm.html', {
            'form': form,
            'rol_usuario': etiqueta_rol(request.user) if request.user.is_authenticated else 'Usuario normal',
        })

    messages.error(request, 'El enlace de recuperación no es válido o ha expirado.')
    return redirect('recuperar_contrasena')


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            rol = form.cleaned_data.get('rol', Perfil.ROL_USUARIO)
            Perfil.objects.create(
                user=user,
                rol=rol if rol != Perfil.ROL_ADMIN else Perfil.ROL_PENDIENTE,
                **datos_perfil_desde_post(request)
            )
            if rol == Perfil.ROL_ADMIN:
                user.is_active = False
                user.is_staff = False
                user.is_superuser = False
                user.save()
                solicitud = SolicitudAdministrador.objects.create(user=user, solicitante=user)
                correo_enviado = enviar_correo_solicitud_admin(request, solicitud)
                if correo_enviado:
                    messages.success(request, 'Cuenta creada. Se envió una solicitud de aprobación de administrador.')
                else:
                    messages.warning(request, 'Cuenta creada, pero no se pudo enviar el correo de solicitud de administrador.')
                messages.warning(request, 'No podrás iniciar sesión hasta que la solicitud sea aprobada o rechazada.')
                return redirect('login')

            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Cuenta creada exitosamente. Has iniciado sesión automáticamente.')
                return redirect('home')
            messages.success(request, 'Cuenta creada exitosamente. Por favor, inicia sesión.')
            return redirect('login')

        perfil_form = PerfilForm(request.POST)
        return render(request, 'register.html', {
            'form': form,
            'perfil_form': perfil_form,
            'rol_usuario': etiqueta_rol(request.user) if request.user.is_authenticated else 'Usuario normal',
        })

    form = RegisterForm()
    perfil_form = PerfilForm()
    return render(request, 'register.html', {
        'form': form,
        'perfil_form': perfil_form,
        'rol_usuario': etiqueta_rol(request.user) if request.user.is_authenticated else 'Usuario normal',
    })


@admin_required
@require_http_methods(["POST"])
def delete_record(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        confirm_username = request.POST.get('confirm_username', '')
        if confirm_username != usuario.username:
            messages.error(request, 'El nombre de usuario no coincide. No se eliminó el usuario.')
            return redirect('customer_record', pk=pk)
        if usuario == request.user:
            messages.error(request, 'No puedes eliminar tu propio usuario')
            return redirect('home')
        usuario.delete()
        messages.success(request, 'Usuario eliminado correctamente')
        return redirect('home')
    return render(request, 'customer_record.html', {'usuario': usuario})


def foro(request):
    if not request.user.is_authenticated:
        messages.warning(request, 'Debes iniciar sesión para publicar en el foro.')
        return redirect('login')

    es_admin = usuario_es_admin(request.user)
    filtro = request.GET.get('filtro', 'todos')

    if request.method == 'POST':
        form = TemaForoForm(request.POST)
        if form.is_valid():
            tema = form.save(commit=False)
            tema.id_usuario = request.user
            tema.save()
            messages.success(request, 'Tema publicado correctamente')
            return redirect('foro')
    else:
        form = TemaForoForm()

    if es_admin and filtro == 'denuncias':
        temas = TemaForo.objects.select_related('id_usuario').filter(
            denuncias__isnull=False
        ).distinct().annotate(
            denuncias_count=Count('denuncias', distinct=True)
        )
    else:
        temas = TemaForo.objects.select_related('id_usuario').annotate(
            denuncias_count=Count('denuncias', distinct=True)
        )

    if not es_admin or filtro == 'mis':
        temas = temas.filter(id_usuario=request.user)

    paginator = Paginator(temas, 10)
    temas_paginados = paginator.get_page(request.GET.get('page'))
    temas_lista = list(temas_paginados.object_list)
    ids_temas = [tema.pk for tema in temas_lista]
    denuncias_por_tema = defaultdict(list)

    if ids_temas:
        denuncias = DenunciaForo.objects.select_related('id_usuario').filter(
            id_tema_id__in=ids_temas
        ).order_by('-fecha_denuncia')
        for denuncia in denuncias:
            denuncias_por_tema[denuncia.id_tema_id].append(denuncia)

    for tema in temas_lista:
        tema.puede_editar = puede_editar_tema_foro(tema, request.user)
        tema.denuncias_lista = denuncias_por_tema.get(tema.pk, [])

    filtro_query = f'&filtro={filtro}' if es_admin else ''

    context = {
        'form': form,
        'temas': temas_lista,
        'temas_paginados': temas_paginados,
        'filtro': filtro if es_admin else 'mis',
        'filtro_query': filtro_query,
        'es_admin': es_admin,
        'rol_usuario': etiqueta_rol(request.user),
    }
    return render(request, 'foro.html', context)


def tema_foro_update(request, pk):
    if not request.user.is_authenticated:
        messages.warning(request, 'Debes iniciar sesión para editar temas del foro.')
        return redirect('login')

    tema = get_object_or_404(TemaForo, pk=pk)
    if not puede_editar_tema_foro(tema, request.user):
        messages.error(request, 'No tienes permiso para editar este tema.')
        return redirect('foro')

    if request.method == 'POST':
        form = TemaForoForm(request.POST, instance=tema)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tema actualizado correctamente')
            return redirect('foro')
    else:
        form = TemaForoForm(instance=tema)
    return render(request, 'tema_foro_update.html', {
        'form': form,
        'tema': tema,
        'rol_usuario': etiqueta_rol(request.user),
    })


@require_http_methods(["POST"])
def tema_foro_delete(request, pk):
    if not request.user.is_authenticated:
        messages.warning(request, 'Debes iniciar sesión para eliminar temas del foro.')
        return redirect('login')

    tema = get_object_or_404(TemaForo, pk=pk)
    if not puede_editar_tema_foro(tema, request.user):
        messages.error(request, 'No tienes permiso para eliminar este tema.')
        return redirect('foro')

    if request.method == 'POST':
        tema.delete()
        messages.success(request, 'Tema eliminado correctamente')
        return redirect('foro')

    messages.warning(request, 'La eliminación de temas se confirma desde el listado del foro.')
    return redirect('foro')


def publicaciones_usuario(request):
    if not request.user.is_authenticated:
        messages.warning(request, 'Debes iniciar sesión para ver publicaciones.')
        return redirect('login')

    return render(request, 'publicaciones.html', obtener_publicaciones_foro_context(
        request,
        False,
        'Publicaciones',
        'Comenta y reacciona con las publicaciones del foro.'
    ))


@admin_required
def publicaciones_admin(request):
    return render(request, 'publicaciones.html', obtener_publicaciones_foro_context(
        request,
        True,
        'Publicaciones del Foro',
        'Consulta, comenta y reacciona con todas las publicaciones registradas en el foro.'
    ))


@require_http_methods(["POST"])
def comentar_publicacion_usuario(request, pk):
    if not request.user.is_authenticated:
        messages.warning(request, 'Debes iniciar sesión para comentar.')
        return redirect('login')

    return procesar_comentario_publicacion(request, pk, 'publicaciones_usuario')


@admin_required
@require_http_methods(["POST"])
def comentar_publicacion_admin(request, pk):
    return procesar_comentario_publicacion(request, pk, 'publicaciones_admin')


def procesar_comentario_publicacion(request, pk, redirect_name):
    tema = get_object_or_404(TemaForo, pk=pk)
    if not puede_editar_tema_foro(tema, request.user):
        messages.error(request, 'No tienes permiso para comentar esta publicación.')
        return redirect(redirect_name)

    if request.method == 'POST':
        form = ComentarioForoForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.id_tema = tema
            comentario.id_usuario = request.user
            comentario.save()
            messages.success(request, 'Comentario publicado correctamente')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    return redirect(redirect_name)


@require_http_methods(["POST"])
def reaccion_publicacion_usuario(request, pk, tipo):
    if not request.user.is_authenticated:
        messages.warning(request, 'Debes iniciar sesión para reaccionar.')
        return redirect('login')

    return procesar_reaccion_publicacion(request, pk, tipo, 'publicaciones_usuario')


@admin_required
@require_http_methods(["POST"])
def reaccion_publicacion_admin(request, pk, tipo):
    return procesar_reaccion_publicacion(request, pk, tipo, 'publicaciones_admin')


def procesar_reaccion_publicacion(request, pk, tipo, redirect_name):
    tipo_reaccion = REACCION_PUBLICACION_CHOICES.get(tipo)
    if tipo_reaccion is None:
        messages.error(request, 'Tipo de reacción no válido.')
        return redirect(redirect_name)

    tema = get_object_or_404(TemaForo, pk=pk)
    if not puede_editar_tema_foro(tema, request.user):
        messages.error(request, 'No tienes permiso para reaccionar a esta publicación.')
        return redirect(redirect_name)

    ReaccionForo.objects.update_or_create(
        id_tema=tema,
        id_usuario=request.user,
        defaults={'tipo': tipo_reaccion}
    )
    messages.success(request, 'Reacción registrada correctamente')
    return redirect(redirect_name)


@require_http_methods(["POST"])
def denunciar_publicacion_usuario(request, pk):
    if not request.user.is_authenticated:
        messages.warning(request, 'Debes iniciar sesión para denunciar.')
        return redirect('login')

    return procesar_denuncia_publicacion(request, pk, 'publicaciones_usuario')


@admin_required
@require_http_methods(["POST"])
def denunciar_publicacion_admin(request, pk):
    return procesar_denuncia_publicacion(request, pk, 'publicaciones_admin')


def procesar_denuncia_publicacion(request, pk, redirect_name):
    tema = get_object_or_404(TemaForo, pk=pk)

    if request.method == 'POST':
        form = DenunciaForoForm(request.POST)
        if form.is_valid():
            DenunciaForo.objects.update_or_create(
                id_tema=tema,
                id_usuario=request.user,
                defaults={'motivo': form.cleaned_data['motivo']}
            )
            messages.success(request, 'Publicación denunciada correctamente')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    return redirect(redirect_name)


@admin_required
def add_record(request):
    if request.method == 'POST':
        form = AdminRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            rol = form.cleaned_data.get('rol', Perfil.ROL_USUARIO)
            aplicar_rol(user, rol)
            Perfil.objects.create(
                user=user,
                rol=rol,
                **datos_perfil_desde_post(request)
            )
            messages.success(request, 'Usuario creado correctamente')
            return redirect('home')
        perfil_form = PerfilForm(request.POST)
        return render(request, 'add_record.html', {
            'form': form,
            'perfil_form': perfil_form,
            'rol_usuario': etiqueta_rol(request.user),
        })

    form = AdminRegisterForm()
    perfil_form = PerfilForm()
    return render(request, 'add_record.html', {
        'form': form,
        'perfil_form': perfil_form,
        'rol_usuario': etiqueta_rol(request.user),
    })
