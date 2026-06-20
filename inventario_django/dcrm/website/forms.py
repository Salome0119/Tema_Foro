from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import Perfil, TemaForo

class LoginForm(forms.Form):
    username = forms.CharField(
        label="Usuario",
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Usuario'
        })
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            # Autenticar el usuario
            user = authenticate(username=username, password=password)
            if user is None:
                raise forms.ValidationError(
                    "Credenciales inválidas. Por favor verifica tu usuario y contraseña."
                )
            elif not user.is_active:
                raise forms.ValidationError(
                    "Esta cuenta está desactivada."
                )
            # Guardar el usuario en el cleaned_data para acceder a él después
            cleaned_data['user'] = user
        
        return cleaned_data

class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        label="Correo electrónico",
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Correo electrónico'
        })
    )
    first_name = forms.CharField(
        label="Nombre",
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre'
        })
    )
    last_name = forms.CharField(
        label="Apellido",
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apellido'
        })
    )
    rol = forms.ChoiceField(
        label="Tipo de cuenta",
        choices=Perfil.ROL_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    password1 = forms.CharField(
        label="Contraseña",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña'
        }),
        help_text="",
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        }),
        help_text="",
    )

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "rol", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar widgets y labels
        self.fields['username'].label = "Usuario"
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Usuario'
        })
        self.fields['first_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nombre'
        })
        self.fields['last_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Apellido'
        })
        self.fields['rol'].widget.attrs.update({
            'class': 'form-control'
        })
        # Sobrescribir mensajes de error en español para las contraseñas
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''
        # Sobrescribir los mensajes de error predeterminados en español
        self.fields['password1'].error_messages = {
            'required': 'Por favor ingrese una contraseña.',
        }
        self.fields['password2'].error_messages = {
            'required': 'Por favor confirme su contraseña.',
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError(
                "Un usuario con ese nombre ya existe."
            )
        import re
        if not re.match(r'^[a-zA-Z0-9_]{4,}$', username):
            raise forms.ValidationError(
                "El usuario debe tener al menos 4 caracteres y solo puede contener letras, números y guiones bajos."
            )
        return username

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if first_name:
            import re
            if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', first_name):
                raise forms.ValidationError(
                    "El nombre solo puede contener letras y espacios."
                )
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if last_name:
            import re
            if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', last_name):
                raise forms.ValidationError(
                    "El apellido solo puede contener letras y espacios."
                )
        return last_name

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "El correo ya está registrado"
            )
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("No coinciden.")
        return password2

    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        if password and len(password) < 8:
            raise forms.ValidationError("Debe contener al menos 8 caracteres.")
        if password:
            import re
            if not re.search(r'[A-Z]', password):
                raise forms.ValidationError("Debe contener al menos una letra mayúscula.")
            if not re.search(r'[a-z]', password):
                raise forms.ValidationError("Debe contener al menos una letra minúscula.")
            if not re.search(r'[0-9]', password):
                raise forms.ValidationError("Debe contener al menos un número.")
        return password


class AdminRegisterForm(RegisterForm):
    rol = forms.ChoiceField(
        label="Rol",
        choices=Perfil.ROL_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rol'].widget.attrs.update({
            'class': 'form-control'
        })

class UserEditForm(forms.ModelForm):
    rol = forms.ChoiceField(
        label="Rol",
        choices=Perfil.ROL_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'rol']
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = False
        self.fields['last_name'].required = False
        if self.instance.pk:
            perfil, _ = Perfil.objects.get_or_create(user=self.instance)
            self.fields['rol'].initial = perfil.rol

    def save(self, commit=True):
        user = super().save(commit=False)
        rol = self.cleaned_data.get('rol')
        user.is_staff = rol == Perfil.ROL_ADMIN
        user.is_superuser = False
        if commit:
            user.save()
            perfil, _ = Perfil.objects.get_or_create(user=user)
            perfil.rol = rol
            perfil.save()
        return user

    def clean_username(self):
        import re
        username = self.cleaned_data.get('username')
        if not re.match(r'^[a-zA-Z0-9_]{4,}$', username):
            raise forms.ValidationError(
                "El usuario debe tener al menos 4 caracteres y solo puede contener letras, números y guiones bajos."
            )
        if User.objects.filter(username__iexact=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Un usuario con ese nombre ya existe.")
        return username

    def clean_first_name(self):
        import re
        first_name = self.cleaned_data.get('first_name')
        if first_name and not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', first_name):
            raise forms.ValidationError("El nombre solo puede contener letras y espacios.")
        return first_name

    def clean_last_name(self):
        import re
        last_name = self.cleaned_data.get('last_name')
        if last_name and not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', last_name):
            raise forms.ValidationError("El apellido solo puede contener letras y espacios.")
        return last_name

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("El correo ya está registrado por otro usuario.")
        return email

class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['telefono', 'direccion', 'departamento', 'municipio', 'codigo_postal']
        labels = {
            'telefono': 'Teléfono',
            'direccion': 'Dirección',
            'departamento': 'Departamento',
            'municipio': 'Municipio',
            'codigo_postal': 'Código Postal',
        }
        widgets = {
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Dirección', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'direccion':
                field.widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': field.label
                })


class TemaForoForm(forms.ModelForm):
    class Meta:
        model = TemaForo
        fields = ['titulo', 'contenido']
        labels = {
            'titulo': 'Título del tema',
            'contenido': 'Contenido',
        }
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título del tema'
            }),
            'contenido': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Escribe el contenido del tema',
                'rows': 5
            }),
        }

    def clean_titulo(self):
        titulo = (self.cleaned_data.get('titulo') or '').strip()
        if len(titulo) < 3:
            raise forms.ValidationError('El título debe tener al menos 3 caracteres.')
        return titulo

    def clean_contenido(self):
        contenido = (self.cleaned_data.get('contenido') or '').strip()
        if len(contenido) < 10:
            raise forms.ValidationError('El contenido debe tener al menos 10 caracteres.')
        return contenido
