from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth.models import User
from .serializers import UserSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate



class RegisterUserAPIView(APIView):
    model = User 

    def post(self, request):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save() 

            token_serializer = TokenObtainPairSerializer(data={
                "username": user.username,
                "password": request.data["password"]    
            })

            if token_serializer.is_valid():
                tokens = token_serializer.validated_data
    
                return Response({
                    'message': 'register success!, keep your tokens safe.',
                    'user' : serializer.data,
                    'tokens' : tokens
                }, status=status.HTTP_201_CREATED)
            
            else:
                print(serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            print("errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class LoginUserAPIView(APIView):
    model = User 

    def post(self, request):
            user = authenticate(username = request.data["username"],
                                 password = request.data["password"])

            token_serializer = TokenObtainPairSerializer(data={
                "username": request.data["username"],
                "password": request.data["password"]    
            })

            if token_serializer.is_valid():
                tokens = token_serializer.validated_data

                if user is not None:
                    return Response({f"hello { request.data['username'] }!" : 
                                     "login authenticated successfully", 
                                     'tokens' : tokens}, status=status.HTTP_201_CREATED)
                
                else:
                    return Response({"detail": "Invalid credentials. Please try again."}, 
                                    status=status.HTTP_400_BAD_REQUEST)        
            else:
                return Response({"detail": "Invalid credentials. Please try again."}, 
                                status=status.HTTP_401_UNAUTHORIZED)
            