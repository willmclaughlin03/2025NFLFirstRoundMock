from django.contrib import admin
from django.urls import path, include
from .views import UserCreateView, UserRUDView, UserLoginView,  UserLogoutView
from rest_framework.authtoken.views import obtain_auth_token # auth token built in 


urlpatterns = [
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('register/', UserCreateView.as_view(), name = 'register'),
    path('edit/', UserRUDView.as_view(), name = 'edit-account'),
    path('login/', UserLoginView.as_view() , name = 'login'),
    path('logout/', UserLogoutView.as_view(next_page='login'),name='logout')

         

]
