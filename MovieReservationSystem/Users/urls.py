from django.urls import path
from . import views

app_name = 'MovieReservationSystem'

urlpatterns = [
    path('register/', views.RegisterUser.as_view(), name='register'),
    path('login/', views.LoginUser.as_view(), name='login'),
]

