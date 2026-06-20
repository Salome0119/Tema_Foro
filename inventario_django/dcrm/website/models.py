from django.db import models
from django.contrib.auth.models import User

class Perfil(models.Model):
    ROL_USUARIO = 'usuario'
    ROL_ADMIN = 'admin'
    ROL_PENDIENTE = 'pendiente'
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
        if self.rol == self.ROL_PENDIENTE:
            return 'Pendiente de aprobación'
        if self.user.is_superuser:
            return 'Superusuario'
        if self.es_admin():
            return 'Administrador'
        return 'Usuario normal'


class SolicitudAdministrador(models.Model):
    PENDIENTE = 'pendiente'
    APROBADA = 'aprobada'
    RECHAZADA = 'rechazada'
    ESTADO_CHOICES = [
        (PENDIENTE, 'Pendiente'),
        (APROBADA, 'Aprobada'),
        (RECHAZADA, 'Rechazada'),
    ]

    id_solicitud = models.AutoField(primary_key=True)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='solicitud_admin'
    )
    solicitante = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='solicitudes_admin_enviadas'
    )
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default=PENDIENTE)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)
    resuelto_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='solicitudes_admin_resueltas'
    )

    class Meta:
        db_table = 'solicitud_administrador'
        ordering = ['-fecha_solicitud', '-id_solicitud']
        indexes = [
            models.Index(fields=['estado', 'fecha_solicitud'], name='idx_solicitud_estado_fecha'),
        ]
        verbose_name = "Solicitud de administrador"
        verbose_name_plural = "Solicitudes de administrador"

    def __str__(self):
        return f'Solicitud de {self.user.username} ({self.get_estado_display()})'


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


class TemaForo(models.Model):
    id_tema = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=100, null=True, blank=True)
    contenido = models.TextField(null=True, blank=True)
    id_usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='id_usuario',
        related_name='temas_foro'
    )
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tema_foro'
        ordering = ['-fecha_publicacion', '-id_tema']
        indexes = [
            models.Index(fields=['id_usuario', 'fecha_publicacion'], name='idx_tema_foro_usuario_fecha'),
        ]
        verbose_name = "Tema de foro"
        verbose_name_plural = "Temas de foro"

    def __str__(self):
        return self.titulo or f'Tema #{self.id_tema}'


class ComentarioForo(models.Model):
    id_comentario = models.AutoField(primary_key=True)
    id_tema = models.ForeignKey(
        TemaForo,
        on_delete=models.CASCADE,
        db_column='id_tema',
        related_name='comentarios'
    )
    id_usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='id_usuario',
        related_name='comentarios_foro'
    )
    contenido = models.TextField()
    fecha_comentario = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'comentario_foro'
        ordering = ['fecha_comentario']
        indexes = [
            models.Index(fields=['id_tema', 'fecha_comentario'], name='idx_comentario_tema_fecha'),
        ]
        verbose_name = "Comentario de foro"
        verbose_name_plural = "Comentarios de foro"

    def __str__(self):
        return f'Comentario #{self.id_comentario}'


class ReaccionForo(models.Model):
    ME_GUSTA = 'me_gusta'
    NO_ME_GUSTA = 'no_me_gusta'
    REACCION_CHOICES = [
        (ME_GUSTA, 'Me gusta'),
        (NO_ME_GUSTA, 'No me gusta'),
    ]

    id_reaccion = models.AutoField(primary_key=True)
    id_tema = models.ForeignKey(
        TemaForo,
        on_delete=models.CASCADE,
        db_column='id_tema',
        related_name='reacciones'
    )
    id_usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='id_usuario',
        related_name='reacciones_foro'
    )
    tipo = models.CharField(max_length=20, choices=REACCION_CHOICES)
    fecha_reaccion = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reaccion_foro'
        ordering = ['-fecha_reaccion', '-id_reaccion']
        indexes = [
            models.Index(fields=['id_tema', 'tipo'], name='idx_reaccion_tema_tipo'),
            models.Index(fields=['id_usuario', 'tipo'], name='idx_reaccion_usuario_tipo'),
        ]
        constraints = [
            models.UniqueConstraint(fields=['id_tema', 'id_usuario'], name='uniq_tema_usuario_reaccion'),
        ]
        verbose_name = "Reacción de foro"
        verbose_name_plural = "Reacciones de foro"

    def __str__(self):
        return f'{self.get_tipo_display()} en Tema #{self.id_tema_id}'


class DenunciaForo(models.Model):
    id_denuncia = models.AutoField(primary_key=True)
    id_tema = models.ForeignKey(
        TemaForo,
        on_delete=models.CASCADE,
        db_column='id_tema',
        related_name='denuncias'
    )
    id_usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='id_usuario',
        related_name='denuncias_foro'
    )
    motivo = models.TextField()
    fecha_denuncia = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'denuncia_foro'
        ordering = ['-fecha_denuncia', '-id_denuncia']
        indexes = [
            models.Index(fields=['id_tema', 'fecha_denuncia'], name='idx_denuncia_tema_fecha'),
        ]
        constraints = [
            models.UniqueConstraint(fields=['id_tema', 'id_usuario'], name='uniq_tema_usuario_denuncia'),
        ]
        verbose_name = "Denuncia de foro"
        verbose_name_plural = "Denuncias de foro"

    def __str__(self):
        return f'Denuncia #{self.id_denuncia} en Tema #{self.id_tema_id}'
