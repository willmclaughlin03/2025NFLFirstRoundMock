from django.test import TestCase
from rest_framework.test import APIRequestFactory
from authentication.models import User
from .views import UserCreateView
from .serializers import UserSerializer
import json

class RegisterTest(TestCase):

    def setUp(self):

        self.factory = APIRequestFactory()

# tests to register acc

    def test_register_success(self):

        
        request = self.factory.post(
            '/register/', 
            data = json.dumps({'id' : '1', 
                               'username': 'mynameiswill', 
             'password' : 'hijklmnop9876', 
             'first_name' : 'lliw', 
             'last_name' : 'liwww',
             'email_address' : 'testcase@gmail.com' 
             }), 
             content_type = 'application/json')
        
        
        serializer = UserSerializer(data = request)
        
        response = UserCreateView.as_view()(request)

        print(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertIn('token', response.data)

        user_exists = User.objects.filter(username = 'mynameiswill').exists()
        self.assertTrue(user_exists)

    def test_register_fail(self):

        request = self.factory.post(
            '/register/',
            data = json.dumps({'username': 'mynameiswill'}),
            content_type = 'application/json'

        )

        response = UserCreateView.as_view()(request)

        self.assertEqual(response.status_code, 400)

        self.assertIn('password', response.data)

