from django.apps import AppConfig
import consul
import socket


class OrderServiceAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "order_service_app"

    def ready(self):
        try:
            c = consul.Consul(host='consul', port=8500)

            service_id = 'order-service-api'
            service_name = 'order-service-api'
            service_port = 8000  # Make sure this matches your runserver port

            # Get the local machine IP
            host_ip = 'order-service'

            # Register service with a TTL-based health check
            c.agent.service.register(
                name=service_name,
                service_id=service_id,
                address=host_ip,
                port=service_port,
                check={
                    'http': f'http://{host_ip}:{service_port}/api/orders/consul/health/?format=json',
                    'interval': '10s'
                }
            )
            print(f"Registered service {service_id} at {host_ip}:{service_port} with health check every 10s")
        except Exception as e:
            print(f"Error registering service with Consul: {e}")