from django.apps import AppConfig
import consul
import socket, json
from shopping_cart_service.logger_setup import logger

class ShoppingCartAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "shopping_cart_app"

    try:
        c = consul.Consul(host='consul', port=8500)

        service_id = 'shopping-cart-api'
        service_name = 'shopping-cart-api'
        service_port = 8000  # Make sure this matches your runserver port

        # Get the local machine IP
        host_ip = 'cart-service'

        # Register service with a TTL-based health check
        c.agent.service.register(
            name=service_name,
            service_id=service_id,
            address=host_ip,
            port=service_port,
            check={
                'http': f'http://{host_ip}:{service_port}/api/carts/health/?format=json',
                'interval': '10s'
            }
        )
        print(f"Registered service {service_id} at {host_ip}:{service_port} with health check every 10s")
        logger.info(json.dumps({"Service registration" : {"service id" : service_id, "host_ip" : host_ip, "service_port" : service_port}}))
    except Exception as e:
        print(f"Error registering service with Consul: {e}") 