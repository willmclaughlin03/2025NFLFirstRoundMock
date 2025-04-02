from django.urls import path
from .views import (
    UserSignUpTempView, 
    UserLoginTempView, 
    UserProfileView, 
    UserCreateAPIView, 
    UserRUDView, 
    CustomAuthToken,
    UserLogoutView
)

urlpatterns = [
    # Template views
    path('signup/', UserSignUpTempView.as_view(), name='signup'),
    path('login/', UserLoginTempView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    
    # API views
    path('api/register/', UserCreateAPIView.as_view(), name='user-create'),
    path('api/user/', UserRUDView.as_view(), name='user-detail'),
    path('api/token/', CustomAuthToken.as_view(), name='api-token'),
]
