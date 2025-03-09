from rest_framework import serializers

from authentication.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(required = True)
    class Meta:
        model = User
        fields = ['id',
                  'first_name', 
                  'last_name', 
                  'email_address', 
                  'username', 
                  'password',]
        extra_kwargs = {'password' : {'write_only' : True}}


        def validate_password(self, value):

            if len(value) < 6:
                raise serializers.ValidationError("Password must be longer than 6 characters")
            


        def create(self, validated_data):

            email_address = validated_data.get('email_address')
            try:
                validate_email(email_address)
            except:
                raise serializers.ValidationError({"email_address" : "Please use a valid email!"})

            user = User(
                username = validated_data.get('username'),
                first_name = validated_data.get('first_name'),
                last_name = validated_data.get('last_name'),
            )
            user.set_password(validated_data.get('password'))
            user.save()
            return user
        
        def update(self, instance, validated_data):

            if 'password' in validated_data:
                validated_data['password'] = make_password(validated_data['password'])

            return super().update(instance, validated_data)