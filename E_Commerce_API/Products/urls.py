from django.urls import path
from . import views

app_name = 'EcomAPI'

urlpatterns = [

path('product/', views.ProductsAPIView.as_view(), name="products"),

]