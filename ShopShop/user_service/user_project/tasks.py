from celery import shared_task
import requests
import logging
import json
import redis

logger = logging.getLogger(__name__)


@shared_task(queue = "user_queue")
def publish_user_event(event_type, user_data):
    event = {'event_type' : event_type,
             'user_data' : user_data}
    
    redis_client = redis.StrictRedis(host ='redis', port=6379, db=0)

    redis_client.publish('user_events', json.dumps(event))
    print(f"Published event to Redis: {json.dumps(event, indent=2)}")
    

        
