from django.urls import path

from . import views

app_name = 'fleet'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('vehicles/', views.vehicle_list, name='vehicle_list'),
    path('vehicles/add/', views.vehicle_create, name='vehicle_create'),
    path('vehicles/<int:pk>/', views.vehicle_detail, name='vehicle_detail'),
    path('vehicles/<int:pk>/edit/', views.vehicle_edit, name='vehicle_edit'),
    path('vehicles/<int:pk>/status/', views.vehicle_change_status, name='vehicle_change_status'),
    path('vehicles/<int:pk>/documents/add/', views.document_create, name='document_create'),
    path('documents/<int:pk>/edit/', views.document_edit, name='document_edit'),
    path('documents/<int:pk>/download/', views.document_download, name='document_download'),
    path('documents/<int:pk>/download/signed/', views.document_download_signed, name='document_download_signed'),
    path('documents/<int:pk>/delete/', views.document_delete, name='document_delete'),
    path('bookings/', views.booking_list, name='booking_list'),
    path('bookings/add/', views.booking_create, name='booking_create'),
    path('bookings/<int:pk>/', views.booking_detail, name='booking_detail'),
    path('bookings/<int:pk>/edit/', views.booking_edit, name='booking_edit'),
    path('bookings/<int:pk>/pickup/', views.booking_pickup, name='booking_pickup'),
    path('bookings/<int:pk>/return/', views.booking_return, name='booking_return'),
    path('drivers/', views.driver_list, name='driver_list'),
    path('drivers/add/', views.driver_create, name='driver_create'),
    path('drivers/<int:pk>/edit/', views.driver_edit, name='driver_edit'),
    path('drivers/<int:pk>/', views.driver_detail, name='driver_detail'),
    path('maintenance/', views.maintenance_list, name='maintenance_list'),
    path('vehicles/<int:pk>/maintenance/add/', views.maintenance_create, name='maintenance_create'),
    path('maintenance/<int:pk>/edit/', views.maintenance_edit, name='maintenance_edit'),
    path('maintenance/<int:pk>/delete/', views.maintenance_delete, name='maintenance_delete'),
    path('violations/', views.violation_list, name='violation_list'),
    path('violations/add/', views.violation_create, name='violation_create'),
    path('violations/<int:pk>/edit/', views.violation_edit, name='violation_edit'),
    path('violations/<int:pk>/delete/', views.violation_delete, name='violation_delete'),
]
