from django.urls import include, path
from . import views

app_name = 'EcomAPI'

urlpatterns = [
    path("carts/add/<str:name>/", views.AddToCartAPIView.as_view(), name="add"),
    path("carts/remove/<str:name>/", views.RemoveFromCartAPIView.as_view(), name="remove"),
    path("carts/view/", views.ViewCartAPIView.as_view(), name="view_cart"),
    path('carts/health/', views.HealthCheckView.as_view(), name='health-check'),
]