from django.urls import path
from . import views

app_name = 'EcomAPI'

urlpatterns = [

    path("login/", views.LoginUserAPIView.as_view(), name="login"),
    path("register/", views.RegisterUserAPIView.as_view(), name="register"),

]