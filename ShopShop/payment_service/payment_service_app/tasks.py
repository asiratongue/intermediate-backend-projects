from celery import shared_task
import requests
import redis
import json

@shared_task(queue='notification_queue')
def send_notification_data(data):

    redis_client = redis.StrictRedis(host='redis', port=6379, db=0)
    redis_client.publish('payment_notification_data', json.dumps(data))
    print(f"Published data to Redis: {json.dumps(data, indent=2)}")
    print("NIGGER NIGGER NIGGER")


@shared_task
def test_task():
    print("Test task executed!")