from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):

    def validate_user(self, value):
        import re
        if not re.match("^[A-Za-z0-9]*$", value):
            raise serializers.ValidationError("Only letters and numbers are allowed!")
        return value
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only':True}, 'id' : {'read_only':True}}




    def create(self, validated_data):
        print("creating user:", validated_data)
        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user