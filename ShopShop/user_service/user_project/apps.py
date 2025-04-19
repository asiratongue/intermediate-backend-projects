from django.apps import AppConfig
import consul 
import socket, json 
from user_service.logger_setup import logger


class UserServiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user_project'

    def ready(self):
        from . import signals
        #logger.info("starting user-service")
        try:
            c = consul.Consul(host='consul', port=8500)

            service_id = 'django-user-service'
            service_name = 'django-user-service'
            service_port = 8000

            host_ip = 'user-service'
            print(f'http://{host_ip}:{service_port}/api/users/health/')

            c.agent.service.register(name= service_name, 
                                    service_id=service_id,
                                    address=host_ip,
                                    port=service_port,
                                    check={
                                        'http' : f'http://{host_ip}:{service_port}/api/users/health/?format=json',
                                        'interval' : '10s'
                                    })
            print(f"Registered service {service_id} at {host_ip}:{service_port} with health check every 10s")
            logger.info(json.dumps({"Service registration": {"service id" : service_id, "host_ip" : host_ip, "service_port" : service_port}}))
        except Exception as e:
            
            print(f"Error registering service with Consul: {e}")