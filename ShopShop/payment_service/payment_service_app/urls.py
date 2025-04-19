from django.urls import include, path
from . import views


app_name = 'EcomAPI'

urlpatterns = [
    path("payments/checkout/<str:id>/", views.CheckoutOrder.as_view(), name="CheckoutOrder"),
    path("payments/success/", views.SuccessView.as_view(), name="payment_success"),
    path("payments/cancel/", views.CancelView.as_view(), name="payment_cancel"),
    path("payments/refund/<int:id>/", views.RefundEndpoint.as_view(), name='refund-order'),
    path("payments/delete/", views.DeletePayment.as_view(), name='delete-payment'),
    path("payments/webhook/stripe/", views.StripeWebhook, name='stripe-webhook'),
    path("payments/webhook/paypal/", views.PaypalWebhook, name='paypal-webhook'),
    path("payments/health/", views.HealthCheckView.as_view(), name='payment-health-check'),
    path("payments/webhook/coinbase/", views.CoinbaseWebhook, name='coinbase-webhook'),
]