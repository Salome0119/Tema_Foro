from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.paginator import Paginator
from .forms import RegisterForm, LoginForm, UserEditForm, PerfilForm
from django import forms
from .models import Perfil

def home(request):
    if request.user.is_authenticated:
        usuarios = User.objects.all()
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
        
        paginator = Paginator(usuarios, 10)
        page_number = request.GET.get('page')
        usuarios_paginados = paginator.get_page(page_number)
        
        context = {
            'usuarios': usuarios_paginados,
            'id_filtro': id_filtro,
            'rol_filtro': rol_filtro,
        }
        return render(request, 'home.html', context)
    else:
        return render(request, 'login.html', {})


def customer_record(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    return render(request, 'customer_record.html', {'usuario': usuario})


def customer_update(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    perfil, created = Perfil.objects.get_or_create(user=usuario)
    
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=usuario, prefix='user')
        perfil_form = PerfilForm(request.POST, instance=perfil, prefix='perfil')
        if user_form.is_valid() and perfil_form.is_valid():
            user_form.save()
            perfil_form.save()
            messages.success(request, "Usuario actualizado correctamente")
            return redirect('home')
        else:
            for form_errors in [user_form.errors, perfil_form.errors]:
                for field, errors in form_errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
    else:
        user_form = UserEditForm(instance=usuario, prefix='user')
        perfil_form = PerfilForm(instance=perfil, prefix='perfil')
    
    return render(request, 'customer_update.html', {
        'form': user_form,
        'perfil_form': perfil_form,
        'usuario': usuario
    })


def login_user(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data.get('user')
            login(request, user)
            return redirect('home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            return redirect('login')
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form})


def logout_user(request):
    logout(request)
    messages.success(request, "Cerraste sesion correctamente")
    return redirect('login')


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            perfil = Perfil.objects.create(user=user)
            perfil.telefono = request.POST.get('telefono', '')
            perfil.direccion = request.POST.get('direccion', '')
            perfil.departamento = request.POST.get('departamento', '')
            perfil.municipio = request.POST.get('municipio', '')
            perfil.codigo_postal = request.POST.get('codigo_postal', '')
            perfil.save()
            
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Cuenta creada exitosamente. Has iniciado sesión automáticamente.")
                return redirect('home')
            else:
                messages.success(request, "Cuenta creada exitosamente. Por favor, inicia sesión.")
                return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            return redirect('register')
    
    form = RegisterForm()
    perfil_form = PerfilForm()
    return render(request, 'register.html', {'form': form, 'perfil_form': perfil_form})


def delete_record(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        confirm_username = request.POST.get('confirm_username', '')
        if confirm_username != usuario.username:
            messages.error(request, "El nombre de usuario no coincide. No se eliminó el usuario.")
            return redirect('customer_record', pk=pk)
        if usuario == request.user:
            messages.error(request, "No puedes eliminar tu propio usuario")
            return redirect('home')
        usuario.delete()
        messages.success(request, "Usuario eliminado correctamente")
        return redirect('home')
    return render(request, 'customer_record.html', {'usuario': usuario})


def foro(request):
    return render(request, 'foro.html', {})


def add_record(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            perfil = Perfil.objects.create(user=user)
            perfil.telefono = request.POST.get('telefono', '')
            perfil.direccion = request.POST.get('direccion', '')
            perfil.departamento = request.POST.get('departamento', '')
            perfil.municipio = request.POST.get('municipio', '')
            perfil.codigo_postal = request.POST.get('codigo_postal', '')
            perfil.save()
            
            messages.success(request, "Usuario creada correctamente")
            return redirect('home')
        else:
            perfil_form = PerfilForm(request.POST)
            return render(request, 'add_record.html', {'form': form, 'perfil_form': perfil_form})
    else:
        form = RegisterForm()
        perfil_form = PerfilForm()
    
    return render(request, 'add_record.html', {'form': form, 'perfil_form': perfil_form})
