from django.contrib import admin
from django.contrib.auth.models import User
from .models import Perfil

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_superuser', 'is_active')

class PerfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'telefono', 'direccion', 'fecha_creacion')
    search_fields = ('user__username', 'user__email')
    list_filter = ('fecha_creacion',)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Perfil, PerfilAdmin)