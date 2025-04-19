from django.urls import include, path
from . import views

app_name = 'EcomAPI'

urlpatterns = [
    path("users/login/", views.LoginUserAPIView.as_view(), name="login"),
    path("users/register/", views.RegisterUserAPIView.as_view(), name="register"),
    path("users/validate/", views.ValidateToken.as_view(), name="validate"),
    path("users/update/", views.UpdateUserDetails.as_view(), name="update"),
    path("users/delete/", views.DeleteAccount.as_view(), name="delete"),
    path("users/health/", views.HealthCheckView.as_view(), name="health-check"),

]