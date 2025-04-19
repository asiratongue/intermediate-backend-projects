import json, os
import redis
import django
import threading 

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shopping_cart_service.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def consume_user_events():
    print("starting user events consumer...")
    redis_client = redis.StrictRedis(host='redis', port=6379, db=0)
    pubsub = redis_client.pubsub()
    pubsub.subscribe('user_events')

    print("Listening for user events...")
    for message in pubsub.listen():
        print(f"Received message: {message}")
        if message['type'] == 'message':
            try:
                event = json.loads(message['data'])
                print(f"Processing event: {event}")
                handle_user_event(event)
            except Exception as e:
                print(f"Error processing message: {e}")

def consume_product_events():
    print("starting product events consumer...")
    redis_client = redis.StrictRedis(host='redis', port=6379, db=0)
    pubsub = redis_client.pubsub()
    pubsub.subscribe('product_events')

    print("listening for product events...")
    for message in pubsub.listen():
        print(f"Received message: {message}")
        if message['type'] == 'message':
            try:
                event = json.loads(message['data'])
                print(f"Processing event: {event}")
                handle_product_event(event)
            except Exception as e:
                print(f"Error processing message: {e}")



def handle_user_event(event):

    event_type = event['event_type']
    user_data = event['user_data']

    if event_type == 'user.created':

        try:
            print(f"Creating user: {user_data}")
            new_user = User.objects.create_user(id = user_data["id"], username = user_data["username"], email = user_data["email"], 
                                first_name = user_data["first_name"], last_name = user_data["last_name"], password = user_data["password"])
            print(f"User {new_user.username} created successfully.")            
        except Exception as e:
            print(f"error creating new user : {e}")
        
    elif event_type == 'user.updated':
        print(f"Updating user: {user_data}")
        try:
            user = User.objects.get(pk=user_data["id"])
            user.email = user_data["email"]
            user.first_name = user_data["first_name"]
            user.last_name = user_data["last_name"]
            user.username = user_data["username"]
            user.password = user_data["password"]
            user.save()
            print("user updated successfully")
        except Exception as e:
            print(f"error creating new user : {e}")


    elif event_type == 'user.deleted':
        try:
            print(f"Deleting user: {user_data}")
            user = User.objects.get(pk=user_data["id"])
            user.delete()
            print("user deleted successfully.")
        except Exception as e:
            print(f"error creating new user : {e}")



def handle_product_event(event):
    
    from shopping_cart_app.models import Product
    event_type = event['event_type']
    product_data = event['product_data']

    if event_type == 'product.created':

        try:
            print(f"Creating Product: {product_data}")
            new_product = Product.objects.create(name = product_data["name"], image = product_data["image"], price = product_data["price"])
            print(f"Product {new_product.name} created successfully.")            
        except Exception as e:
            print(f"error creating new user : {e}")
        
    elif event_type == 'product.updated':
        print(f"Updating product: {product_data}")
        Product = Product.objects.get(pk=product_data["id"])
        Product.name = product_data["name"]
        Product.image = product_data["image"]
        Product.price = product_data["price"]
        Product.save()

if __name__ == '__main__':

    t1 = threading.Thread(target=consume_user_events, daemon=True)
    t1.start()

    consume_product_events()