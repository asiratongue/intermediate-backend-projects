from django.urls import include, path
from . import views


app_name = 'EcomAPI'

urlpatterns = [
    path("products/view/", views.ProductListAPIView.as_view(), name="login"),
    path("products/search/", views.SearchProducts.as_view(), name="search"),
    path("products/retrieve/<str:name>", views.RetrieveProduct.as_view(), name='retrieve'),
    path('products/health/', views.HealthCheckView.as_view(), name='product-health-check'),
]



