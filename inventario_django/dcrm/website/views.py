from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import RegisterForm, LoginForm

def home(request):
    if request.user.is_authenticated:
        # Usuario autenticado, mostrar página de inicio
        usuarios = User.objects.all()
        return render(request, 'home.html', {'usuarios': usuarios})
    else:
        # Usuario no autenticado, mostrar página de login
        return render(request, 'login.html', {})


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