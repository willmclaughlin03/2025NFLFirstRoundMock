from rest_framework import serializers

from authentication.models import User

from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(required = True)
    class Meta:
        model = User
        fields = ['id', 
                  'created_at'
                  'first_name', 
                  'last_name', 
                  'email_address,', 
                  'username', 
                  'password',]
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {'password' : {'write_only' : True}}


        def validate_password(self, value):

            if len(value) < 6:
                raise serializers.ValidationError("Password must be longer than 8 characters")
            


        def create(self, validated_data):
            validated_data['password'] = make_password(validated_data['password'])

            return super().create(validated_data)
        
        def update(self, instance, validated_data):

            if 'password' in validated_data:
                validated_data['password'] = make_password(validated_data['password'])

            return super().update(instance, validated_data)