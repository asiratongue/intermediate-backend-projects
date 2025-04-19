from celery import shared_task
import redis
import json

@shared_task(queue = "product_queue")
def publish_product_event(event_type, product_data):
    event = {'event_type' : event_type,
             'product_data' : product_data}
    
    redis_client = redis.StrictRedis(host ='redis', port=6379, db=0)

    redis_client.publish('product_events', json.dumps(event))
    print(f"Published event to Redis: {json.dumps(event, indent=2)}")    
