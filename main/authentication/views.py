from django.shortcuts import render
from rest_framework import generics, status, response
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import UserSerializer
from .models import User

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


# handles retrieval updating and destroying of user
class UserRUDView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

