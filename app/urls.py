from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('add_edit_vehicle/', views.add_edit_vehicle, name='add_vehicle'),
    path('add_edit_vehicle/<int:vehicle_id>/', views.add_edit_vehicle, name='edit_vehicle'),
    path('delete_vehicle/<int:vehicle_id>/', views.delete_vehicle, name='delete_vehicle'),
    path('add_maintenance_schedule/<int:vehicle_id>/', views.add_maintenance_schedule, name='add_maintenance_schedule'),
    path('get_maintenance_schedule/<int:vehicle_id>/', views.get_maintenance_schedule, name='get_maintenance_schedule'),
]