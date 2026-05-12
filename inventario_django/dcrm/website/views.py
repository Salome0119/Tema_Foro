from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

def home(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "¡Bienvenido! Has iniciado sesión correctamente.")
            return redirect('home')
        else:
            messages.error(request, "Credenciales incorrectas. Por favor verifica tu usuario y contraseña.")
    return render(request, 'home.html', {})


def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Credenciales inválidas")
            return redirect('login')
    return render(request, 'login.html', {})


def logout_user(request):
    logout(request)
    messages.success(request, "Cerraste sesion correctamente")
    return redirect('login')


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        
        if password1 != password2:
            messages.error(request, "Las contraseñas no coinciden")
            return redirect('register')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "El usuario ya existe")
            return redirect('register')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "El correo ya está registrado")
            return redirect('register')
        
        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()
        
        from website.models import Perfil
        Perfil.objects.create(user=user)
        
        messages.success(request, "Cuenta creada exitosamente. Por favor, inicia sesión.")
        return redirect('login')
    
    return render(request, 'register.html', {})