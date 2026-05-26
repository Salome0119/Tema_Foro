from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import RegisterForm, LoginForm
from django import forms

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        labels = {
            'username': 'Usuario',
            'email': 'Correo electrónico',
            'first_name': 'Nombre',
            'last_name': 'Apellido',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usuario'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}),
        }

def home(request):
    if request.user.is_authenticated:
        usuarios = User.objects.all()
        return render(request, 'home.html', {'usuarios': usuarios})
    else:
        return render(request, 'login.html', {})


class DeleteConfirmForm(forms.Form):
    confirm_username = forms.CharField(
        max_length=150,
        label="Escribe el nombre de usuario para confirmar",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Confirmar usuario'})
    )

def customer_record(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = DeleteConfirmForm(request.POST)
        if form.is_valid():
            confirm_username = form.cleaned_data.get('confirm_username')
            if not request.user.is_superuser:
                messages.error(request, "No tienes permiso para eliminar usuarios.")
            elif confirm_username != usuario.username:
                messages.error(request, "El nombre de usuario no coincide. No se eliminó.")
            else:
                usuario.delete()
                messages.success(request, f"Usuario {usuario.username} eliminado exitosamente.")
        else:
            messages.error(request, "Error en la validación.")
        return redirect('home')
    return render(request, 'customer_record.html', {'usuario': usuario})


def customer_update(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, f"Usuario {usuario.username} actualizado exitosamente.")
            return redirect('home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserUpdateForm(instance=usuario)
    
    return render(request, 'customer_update.html', {'form': form, 'usuario': usuario})


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
            # Guardar el usuario usando el formulario (que tiene el hasheo correcto)
            user = form.save()
            
            from website.models import Perfil
            Perfil.objects.create(user=user)
            
            # Autenticar al usuario inmediatamente después del registro
            # Usamos exactamente el mismo proceso que en login_user
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Cuenta creada exitosamente. Has iniciado sesión automáticamente.")
                return redirect('home')
            else:
                # Si por alguna razón la autenticación falla, aún así creamos la cuenta
                messages.success(request, "Cuenta creada exitosamente. Por favor, inicia sesión.")
                return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            return redirect('register')
    
    form = RegisterForm()
    return render(request, 'register.html', {'form': form})