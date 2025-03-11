from django.urls import path
from .views import magang_views

urlpatterns = [
    path('', magang_views.magang_dashboard, name='magang_dashboard'),
    path('edit-profil/', magang_views.edit_profil_magang, name='edit_profil_magang'),
]
