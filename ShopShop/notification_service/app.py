from flask import Flask, request, jsonify
import consul
import socket, json
from logger_setup import logger


app = Flask(__name__)

try:
    c = consul.Consul(host='consul', port=8500)
    service_id = 'notification-service-api'
    service_name = 'notification-service-api'
    service_port = 5000


    host_ip = 'notification-service'

    c.agent.service.register(
        name=service_name,
        service_id=service_id,
        address=host_ip,
        port=service_port,
        check={
            'http': f'http://{host_ip}:5000/notification/health/',
            'interval': '10s'
        }
    )
    logger.info(json.dumps({"Service registration" : {"service id" : service_id, "host_ip" : host_ip, "service_port" : service_port}}))
    print(f"Registered service {service_id} at {host_ip}:{service_port} with health check every 10s") 

except Exception as e:
    logger.error(json.dumps({"level" : "ERROR", "error" : f"Error registering service with consul: {e}", "service" : {"name" : "notification-service"}}))

@app.route('/notification/health/', methods = ['GET'])
def health_check_endpoint():

    if request.method == "GET":
        logger.info(json.dumps({"level" : "INFO", "response" : {"status" : "ok"}, "service" : {"name" : "notification-service"}}))
        return jsonify({"status" : "ok"}), 200


if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000, debug=True)


#curl -v http://127.18.0.16:5000/notification/health/