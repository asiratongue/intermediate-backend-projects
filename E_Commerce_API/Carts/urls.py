from django.urls import path
from . import views

app_name = 'EcomAPI'

urlpatterns = [


    path('cart/add/<int:id>/', views.AddToCartAPIView.as_view(), name="add_to_cart"),
    path('cart/', views.ViewCartAPIView.as_view(), name="view_cart"),
    path('cart/remove/<int:id>/', views.RemoveFromCartAPIView.as_view(), name = "remove_from_cart"),
    path('cart/checkout/', views.StripeCheckoutAPIView.as_view(), name = "stripe_checkout"),

]

