from django.test import TestCase
from rest_framework.test import APIRequestFactory
from authentication.models import User
from .views import UserCreateView
from .serializers import UserSerializer
from rest_framework.authtoken.models import Token
import json

class RegisterTest(TestCase):

    def setUp(self):

        self.factory = APIRequestFactory()

# tests to register acc

    def test_register_success(self):
        # Create the JSON payload
        payload = {
            'username': 'mynameiswill',
            'password': 'hijklmnop9876',
            'first_name': 'lliw',
            'last_name': 'liwww',
            'email_address': 'testcase@gmail.com'
        }

        # Create the POST request
        request = self.factory.post(
            '/register/',
            data=json.dumps(payload),  # Convert payload to JSON
            content_type='application/json'
        )

        # Validate the payload using the serializer
        serializer = UserSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)  # Ensure the payload is valid

        # calls the view
        response = UserCreateView.as_view()(request)

        # debuggimg
        print(response.data)

        # Assert the response status code
        self.assertEqual(response.status_code, 201)
        self.assertIn('token', response.data)

        # Check if the user was created in the database
        user_exists = User.objects.filter(username='mynameiswill').exists()
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

