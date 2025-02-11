from rest_framework import serializers
from Users.models import CustomUser


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only':True}, 'id' : {'read_only':True}}


    def validate_user(self, value):
        import re
        if not re.match("^[A-Za-z0-9]*$", value):
            raise serializers.ValidationError("Only letters and numbers are allowed!")
        return value
    

    def create(self, validated_data):
        print("creating user:", validated_data)
        user = CustomUser(
            username=validated_data['username'],
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    
    