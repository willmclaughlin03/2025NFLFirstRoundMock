from rest_framework import serializers

from authentication.models import User
from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password


User = get_user_model()
class UserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only = True, required = True)
    email_address = serializers.EmailField(required = True)
    class Meta:
        model = User
        fields = [ 
                  'email_address', 
                  'username', 
                  'password',]


        def validate_password(self, value):

            if len(value) < 6:
                raise serializers.ValidationError("Password must be longer than 6 characters")
            
        def validate_email_address(self, value):
            if User.objects.filter(email_address = value).exists():
                raise ValidationError("Email is already being used!")
            return value
            


        def create(self, validated_data):

        # Create the user instance
            try:
                user = User.objects.create_user(
                username = validated_data['username'],
                email_address = validated_data['email_address'],
                password=validated_data['password']
                
            )

        # Save the user to the database
                user.save()

                return user
            except Exception as e:
                raise serializers.ValidationError(f"An error occurred: {str(e)}")
        
        def update(self, instance, validated_data):

            if 'password' in validated_data:
                validated_data['password'] = make_password(validated_data['password'])

            return super().update(instance, validated_data)