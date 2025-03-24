from django.shortcuts import render
from rest_framework import generics, status, response
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import UserSerializer
from .models import User
from django.contrib.auth.views import LoginView, LogoutView

from django.contrib import messages

# create user view with token auth
class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    # retrieves serializer, saves, then creates token for user
    def create(self, request, *args, **kwargs):
        # to validate 
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception = True)

        # saves the instance of the user
        user = serializer.save()

        # Debugging: Print user details
        print(f"User created: {user}")
        print(f"User type: {type(user)}")
        print(f"User attributes: username={user.username}, email={user.email_address}")

        # GET or CREATE for user
        token, created = Token.objects.get_or_create(user = user)

# test response
        return Response(
            {
                'token': token.key,
                'username' : user.username, # changed to use the instance not class
                'email_address' : user.email_address,
            }, 
            status=status.HTTP_201_CREATED,)
    
class UserLoginView(LoginView):
    queryset = User.objects.all()
    serializer_class = UserSerializer 
    permission_classes = [AllowAny]

    redirect_authenticated_user = True

    def get_success_url(self):
        #return main_page('draft')
        return None

    def form_invaid(self, form):
        messages.error(self.request, 'Invalid Username or Password')
        return self.render_to_response(self.get_context_data(form=form))

class UserLogoutView(LogoutView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]




# handles retrieval updating and destroying of user
class UserRUDView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

