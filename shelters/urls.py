from django.urls import path
from . import views

app_name = 'shelters'
urlpatterns = [
    path('', views.directory, name='directory'),
    path('pet/<int:pk>/', views.pet_detail, name='pet_detail'),
    path('<int:pk>/', views.shelter_detail, name='detail'),
    path('<int:pk>/contact/', views.shelter_contact, name='shelter_contact'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/edit/', views.shelter_edit, name='shelter_edit'),
    path('dashboard/pets/new/', views.pet_create, name='pet_create'),
    path('dashboard/pets/<int:pk>/edit/', views.pet_edit, name='pet_edit'),
    path('dashboard/pets/<int:pk>/delete/', views.pet_delete, name='pet_delete'),
    path('dashboard/import/', views.csv_import, name='csv_import'),
]
