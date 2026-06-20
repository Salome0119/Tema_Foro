from functools import wraps

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AdminRegisterForm, LoginForm, PerfilForm, RegisterForm, TemaForoForm, UserEditForm
from .models import Perfil, TemaForo


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


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            rol = form.cleaned_data.get('rol', Perfil.ROL_USUARIO)
            aplicar_rol(user, rol)
            Perfil.objects.create(
                user=user,
                rol=rol,
                **datos_perfil_desde_post(request)
            )
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

    temas = TemaForo.objects.select_related('id_usuario').all()
    if not es_admin or filtro == 'mis':
        temas = temas.filter(id_usuario=request.user)

    paginator = Paginator(temas, 10)
    temas_paginados = paginator.get_page(request.GET.get('page'))
    temas_lista = list(temas_paginados.object_list)
    for tema in temas_lista:
        tema.puede_editar = puede_editar_tema_foro(tema, request.user)

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
