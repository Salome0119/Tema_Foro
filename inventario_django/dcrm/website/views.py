from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import RegisterForm, LoginForm
from django import forms

class UserEditForm(forms.ModelForm):
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


def customer_record(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    return render(request, 'customer_record.html', {'usuario': usuario})


def customer_update(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario actualizado correctamente")
            return redirect('home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserEditForm(instance=usuario)
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


def foro(request):
    return render(request, 'foro.html', {})

#Agregar usuario
def add_record(request):
    form = RegisterForm(request.POST or None)
    if request.user.is_authenticated:
        if request.method == 'POST':
            if form.is_valid():
                form.save()
                messages.success(request, "Usuario creada correctamente")
                return redirect('home')
        return render(request, 'add_record.html', {'form': form})  
    else:
        messages.error(request, "Debes iniciar sesión para agregar un usuario")
        return redirect('home')   
        