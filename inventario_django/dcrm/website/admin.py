from django.contrib import admin
from django.contrib.auth.models import User
from .models import ComentarioForo, DenunciaForo, Perfil, ReaccionForo, TemaForo

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'es_admin', 'is_staff', 'date_joined')
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_superuser', 'is_active')

    def es_admin(self, obj):
        try:
            perfil = obj.perfil
        except (AttributeError, Perfil.DoesNotExist):
            perfil = None
        if perfil:
            return perfil.etiqueta_rol()
        if obj.is_superuser:
            return 'Superusuario'
        if obj.is_staff:
            return 'Administrador'
        return 'Usuario normal'
    es_admin.short_description = 'Rol'

class PerfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'telefono', 'direccion', 'fecha_creacion')
    search_fields = ('user__username', 'user__email')
    list_filter = ('fecha_creacion',)

class TemaForoAdmin(admin.ModelAdmin):
    list_display = ('id_tema', 'titulo', 'id_usuario', 'fecha_publicacion', 'last_update')
    search_fields = ('titulo', 'contenido', 'id_usuario__username')
    list_filter = ('fecha_publicacion', 'last_update')

class ComentarioForoAdmin(admin.ModelAdmin):
    list_display = ('id_comentario', 'id_tema', 'id_usuario', 'fecha_comentario')
    search_fields = ('contenido', 'id_tema__titulo', 'id_usuario__username')
    list_filter = ('fecha_comentario',)

class ReaccionForoAdmin(admin.ModelAdmin):
    list_display = ('id_reaccion', 'id_tema', 'id_usuario', 'tipo', 'fecha_reaccion', 'last_update')
    search_fields = ('id_tema__titulo', 'id_usuario__username')
    list_filter = ('tipo', 'fecha_reaccion', 'last_update')

class DenunciaForoAdmin(admin.ModelAdmin):
    list_display = ('id_denuncia', 'id_tema', 'id_usuario', 'fecha_denuncia')
    search_fields = ('motivo', 'id_tema__titulo', 'id_usuario__username')
    list_filter = ('fecha_denuncia',)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Perfil, PerfilAdmin)
admin.site.register(TemaForo, TemaForoAdmin)
admin.site.register(ComentarioForo, ComentarioForoAdmin)
admin.site.register(ReaccionForo, ReaccionForoAdmin)
admin.site.register(DenunciaForo, DenunciaForoAdmin)