from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
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

        user = serializer.save()

        token, created = Token.objects.get_or_create(user = user)

# test response
        return Response({
            'token': token.key,
            'user': serializer.data
        }, status=status.HTTP_201_CREATED)

# handles retrieval updating and destroying of user
class UserRUDView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

