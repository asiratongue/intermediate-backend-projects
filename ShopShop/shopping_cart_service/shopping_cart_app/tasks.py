from celery import shared_task
import requests
import logging, redis, json


logger = logging.getLogger(__name__)

@shared_task(queue = "quantity_queue")
def publish_quantity_event(event_type, cart_data):

    event = {'event_type' : event_type,
             'cart_data' : cart_data}
    
    redis_client = redis.StrictRedis(host ='redis', port=6379, db=0)

    redis_client.publish('cart_events', json.dumps(event))
    print(f"Published event to Redis: {json.dumps(event, indent=2)}")       