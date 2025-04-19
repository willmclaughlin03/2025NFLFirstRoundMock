from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import UserSerializer
from .models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSignUpTempView(CreateView):
    template_name = 'registration/signup.html'
    model = User
    serializer_class = UserSerializer
    success_url = reverse_lazy('login')
    fields = ['email_address', 'username', 'password']

    def form_valid(self, form):
        user = form.save(commit = False)
        password = form.cleaned_data.get('password')
        user.set_password(password)
        user.save()

        # Create token for the user
        token, created = Token.objects.get_or_create(user = user)

        messages.success(self.request, 'Account created successfully!')
        return super().form_valid(form)
    
class UserLoginTempView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('draft_home')
    
    def form_invalid(self, form):
        messages.error(self.request, 'Invalid Username or Password')
        return super().form_invalid(form)
    
class UserProfileView(LoginRequiredMixin, DetailView):
    template_name = 'registration/user_profile.html'
    model = User
    
    def get_object(self, queryset = None):
        return self.request.user
    


# create user view with token auth
class UserCreateAPIView(generics.CreateAPIView):
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

        Token.objects.filter(user=user).delete()

        # Debugging: Print user details
        #print(f"User created: {user}")
        #print(f"User type: {type(user)}")
        #print(f"User attributes: username={user.username}, email={user.email_address}")

        # GET or CREATE for user
        token = Token.objects.create(user=user)

        messages.success(self.request, 'Account created successfully!')

# test response
        return Response(
            {
                'token': token.key,
                'username' : user.username, # changed to use the instance not class
                'email_address' : user.email_address,
            }, 
            status=status.HTTP_201_CREATED,)

class UserLogoutView(LogoutView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    next_page = reverse_lazy('login')



# handles retrieval updating and destroying of user
class UserRUDView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

'''
#removed for session auth
class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        
        #Debug
        #print("Request data:", request.data)  
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if not serializer.is_valid():

            print("Validation errors:", serializer.errors, status = status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user = user)

    
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'email_address': user.email_address,
        })

'''