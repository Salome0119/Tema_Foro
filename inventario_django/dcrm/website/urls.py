from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register, name='register'),
    path('administrador/solicitudes-admin/', views.solicitudes_admin, name='solicitudes_admin'),
    path('administrador/solicitudes-admin/<int:pk>/aprobar/', views.aprobar_admin, name='aprobar_admin'),
    path('administrador/solicitudes-admin/<int:pk>/rechazar/', views.rechazar_admin, name='rechazar_admin'),
    path('customer-record/<int:pk>/', views.customer_record, name='customer_record'),
    path('customer-update/<int:pk>/', views.customer_update, name='customer_update'),
    path('foro/', views.foro, name='foro'),
    path('foro/tema/<int:pk>/update/', views.tema_foro_update, name='tema_foro_update'),
    path('foro/tema/<int:pk>/delete/', views.tema_foro_delete, name='tema_foro_delete'),
    path('publicaciones/', views.publicaciones_usuario, name='publicaciones_usuario'),
    path('administrador/publicaciones/', views.publicaciones_admin, name='publicaciones_admin'),
    path('publicaciones/<int:pk>/comentar/', views.comentar_publicacion_usuario, name='comentar_publicacion_usuario'),
    path('administrador/publicaciones/<int:pk>/comentar/', views.comentar_publicacion_admin, name='comentar_publicacion_admin'),
    path('publicaciones/<int:pk>/denunciar/', views.denunciar_publicacion_usuario, name='denunciar_publicacion_usuario'),
    path('administrador/publicaciones/<int:pk>/denunciar/', views.denunciar_publicacion_admin, name='denunciar_publicacion_admin'),
    path('publicaciones/<int:pk>/reaccion/<str:tipo>/', views.reaccion_publicacion_usuario, name='reaccion_publicacion_usuario'),
    path('administrador/publicaciones/<int:pk>/reaccion/<str:tipo>/', views.reaccion_publicacion_admin, name='reaccion_publicacion_admin'),
    path('add-record/', views.add_record, name='add_record'),
    path('delete-record/<int:pk>/', views.delete_record, name='delete_record'),
]