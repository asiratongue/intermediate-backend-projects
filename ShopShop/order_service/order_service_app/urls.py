from django.urls import include, path
from . import views

app_name = 'EcomAPI'

urlpatterns = [
    path("orders/ops/create/", views.CreateOrder.as_view(), name = "create_order"),
    path("orders/<str:id>/", views.OrderEndpoint.as_view(), name = "order_endpoint"),
    path("orders/status/<str:id>/", views.UpdateOrderStatus.as_view(), name = "update_order_status"),
    path("orders/ops/delete/", views.DeleteOrder.as_view(), name = "delete_order"),
    path("orders/history/<str:id>/", views.GetOrderHistory.as_view(), name = "order_history"),
    path('orders/consul/health/', views.HealthCheckView.as_view(), name='orders-health-check'),
    path('orders/contact/<str:id>/', views.GetContactDetails.as_view(), name='contact_endpoint'),
]

