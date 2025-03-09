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
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception = True)

        serializer.is_valid(raise_exception = True)
        user = serializer.validated_data
        print(user)
        print(type(user))

        token, created = Token.objects.get_or_create(user = user)

# test response
        return Response({
                'token': token.key,
                'username' : User.username,
                'email_address' : User.email_address,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

# handles retrieval updating and destroying of user
class UserRUDView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

