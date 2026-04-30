from django.urls import path
from . import views

app_name = 'reports'
urlpatterns = [
    path('', views.report_list, name='list'),
    path('create/', views.report_create, name='create'),
    path('<int:pk>/', views.report_detail, name='detail'),
    path('<int:pk>/contact/', views.contact_request_create, name='contact'),
    path('<int:pk>/edit/', views.report_edit, name='edit'),
    path('<int:pk>/delete/', views.report_delete, name='delete'),
    path('<int:pk>/photos/<int:photo_pk>/delete/', views.report_photo_delete, name='photo_delete'),
]
