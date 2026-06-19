from django.db import models
from django.contrib.auth.models import User

class Perfil(models.Model):
    ROL_USUARIO = 'usuario'
    ROL_ADMIN = 'admin'
    ROL_CHOICES = [
        (ROL_USUARIO, 'Usuario normal'),
        (ROL_ADMIN, 'Administrador'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.TextField(blank=True)
    departamento = models.CharField(max_length=100, blank=True)
    municipio = models.CharField(max_length=100, blank=True)
    codigo_postal = models.CharField(max_length=20, blank=True)
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default=ROL_USUARIO)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"

    def es_admin(self):
        return self.rol == self.ROL_ADMIN or self.user.is_staff or self.user.is_superuser

    def etiqueta_rol(self):
        if self.user.is_superuser:
            return 'Superusuario'
        if self.es_admin():
            return 'Administrador'
        return 'Usuario normal'


class Publicacion(models.Model):
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-creado']
        verbose_name = "Publicación"
        verbose_name_plural = "Publicaciones"

    def __str__(self):
        return self.titulo