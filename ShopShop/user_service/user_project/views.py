from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .serializers import UserSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate, get_user_model
from rest_framework.permissions import IsAuthenticated
from user_service.logger_setup import logger
import json


class RegisterUserAPIView(APIView):
    User = get_user_model()
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
                get_response = {
                    'message': 'register success!, keep your tokens safe.',
                    'user' : serializer.data,
                    'tokens' : tokens
                }

                logger.info(json.dumps({"level" : "INFO", "response" : get_response, "service" : {"name" : "user-service"}})) 
                return Response(get_response, status=status.HTTP_201_CREATED)
                
            
            else:
                logger.error(json.dumps({"level" : "ERROR", "error" : serializer.errors, "service" : {"name" : "user-service"}}))
                return Response({"error" : serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            logger.error(json.dumps({"level" : "ERROR", "error" : serializer.errors, "service" : {"name" : "user-service"}}))
            return Response({"error" : serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        

class LoginUserAPIView(APIView):
    User = get_user_model()
    def post(self, request):
            user = authenticate(username = request.data["username"], password = request.data["password"])
            error_response = {"error": "Invalid credentials. Please try again."}

            token_serializer = TokenObtainPairSerializer(data={
                "username": request.data["username"],
                "password": request.data["password"]    
            })

            if token_serializer.is_valid():
                tokens = token_serializer.validated_data

                if user is not None:
                    post_response = {"message" : f"login authenticated successfully for { request.data['username']}", 'tokens' : tokens}
                    logger.info(json.dumps({"level" : "INFO", "response": post_response, "service" :  {"name" : "user-service"}}))
                    return Response(post_response, status=status.HTTP_201_CREATED)
                
                else:
                    logger.error(json.dumps(error_response))
                    return Response(error_response, status=status.HTTP_UNAUTHORIZED)        
            else:
                logger.error(error_response)
                return Response(error_response, status=status.HTTP_401_UNAUTHORIZED)


class UpdateUserDetails(APIView):
    permission_classes = [IsAuthenticated]
    def put(self, request):
        User = get_user_model()
        try:
            user = request.user    
            new_email = request.data.get("email", user.email)
            new_username = request.data.get("username", user.username)
            new_password = request.data.get("password", None)
            user.email, user.username = new_email, new_username

            if new_password != None:
                user.set_password(new_password)

            user.save()
            put_response = {"message" : f"updated user details - new email {user.email}, new username {user.username}, new password hash{user.password}"}
            logger.info(json.dumps({"level" : "INFO", "response" : put_response, "service" :  {"name" : "user-service"}}))
            return Response(put_response, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(json.dumps({"level" : "ERROR", "error" : f"details {e}", "service" :  {"name" : "user-service"}}))
            return Response ({"error" : f"details {e}"}, status=status.HTTP_400_BAD_REQUEST)


class DeleteAccount(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request):
        User = get_user_model()
        try:
            #implement password required for deletion.
            user = request.user
            user_id = user.id
            user.delete()
            logger.info(json.dumps({ "level" : "INFO", "response" : {"message" : f"user {user_id} has been deleted", "service" :  {"name" : "user-service"}}}))
            return Response ({"message" : f"user {user_id} has been deleted"}, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error({"level" : "ERROR", "error" : f"details {e}", "service" :  {"name" : "user-service"}})
            return Response ({"error" : f"details {e}"}, status=status.HTTP_400_BAD_REQUEST)


class HealthCheckView(APIView):
    def get(self, request):
        logger.info(json.dumps({
            "level" : "INFO",
            "message" : "Health check status",
            "status" : "ok",
            "service" :  {"name" : "user-service"}}))
        
        return Response({"status" : "ok"})         


class ValidateToken(APIView):
    permission_classes = [IsAuthenticated]    
    def post(self, request):
        return Response({"auth" : True}, status=status.HTTP_200_OK)


