from django.contrib import admin
from django.urls import path, include
from .views import UserCreateAPIView, UserRUDView, UserLoginTempView,  UserLogoutView, UserSignUpTempView, UserProfileView, CustomAuthToken
# auth token built in 


urlpatterns = [
    path('api-token-auth/', CustomAuthToken.as_view(), name='api_token_auth'),
    path('signup/', UserSignUpTempView.as_view(), name='signup'),
    path('login/', UserLoginTempView.as_view(), name='login'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('logout/', UserLogoutView.as_view(next_page='login'), name='logout'),

    # API Views
    path('api/signup/', UserCreateAPIView.as_view(), name='api_signup'),

         

]
