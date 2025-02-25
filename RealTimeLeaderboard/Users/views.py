from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status 
from django.contrib.auth.models import User
from .serializers import UserSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate


class RegisterUser(APIView):
    model = User

    def post (self, request):
        Serializer = UserSerializer(data = request.data)

        if Serializer.is_valid():
            user = Serializer.save()

            Tokens = TokenObtainPairSerializer(data = {"username" : user.username, "password" : request.data["password"]})

            if Tokens.is_valid():
                tokens = Tokens.validated_data

                return Response ({"message" : "you have registered successfully!", "user" : Serializer.data, "tokens" : tokens}, status=status.HTTP_201_CREATED)
        
            else:
                return Response({"error" : Serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({"error" : Serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
class LoginUser(APIView):
    model = User

    def post (self, request):
        user = authenticate(username = request.data["username"], password = request.data["password"])
        Tokens = TokenObtainPairSerializer(data = {"username" : request.data["username"], "password" : request.data["password"]})

        if Tokens.is_valid():
            tokens = Tokens.validated_data

            if user is not None:
                return Response ({"login authenticated successfully" : f"welcome back {user.username}", "tokens" : tokens}, status=status.HTTP_200_OK)
            
            else:
                return Response ({"error": "invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        
        else:
            return Response ({"error": "invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)



