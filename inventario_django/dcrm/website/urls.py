from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register, name='register'),
    path('customer-record/<int:pk>/', views.customer_record, name='customer_record'),
    path('customer-update/<int:pk>/', views.customer_update, name='customer_update'),
    path('foro/', views.foro, name='foro'),
    path('foro/tema/<int:pk>/update/', views.tema_foro_update, name='tema_foro_update'),
    path('foro/tema/<int:pk>/delete/', views.tema_foro_delete, name='tema_foro_delete'),
    path('add-record/', views.add_record, name='add_record'),
    path('delete-record/<int:pk>/', views.delete_record, name='delete_record'),
]