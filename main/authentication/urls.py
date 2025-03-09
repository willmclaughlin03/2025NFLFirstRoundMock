from django.contrib import admin
from django.urls import path, include
from .views import UserCreateView, UserRUDView


urlpatterns = [
    path('register/', UserCreateView.as_view(), name = 'register'),
    path('edit/', UserRUDView.as_view(), name = 'edit-account'),

         

]
