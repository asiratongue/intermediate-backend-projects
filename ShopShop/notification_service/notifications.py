from twilio.rest import Client
import redis
import json
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
from logger_setup import logger


redis_client = redis.StrictRedis(host='redis', port=6379, db=0)
load_dotenv()

account_sid = os.getenv('account_sid')
auth_token = os.getenv('auth_token')
sendgrid_api_key = os.getenv('sendgrid_api_key')

print(f"account_sid: {account_sid}")
print(f"auth_token: {auth_token}")
print(f"sendgrid_api_key: {sendgrid_api_key}")

client = Client(account_sid, auth_token)

def consume_notification_events():
    client = Client(account_sid, auth_token)
    redis_client = redis.StrictRedis(host='redis', port=6379, db=0) 
    pubsub = redis_client.pubsub()
    pubsub.subscribe('notification_data', 'payment_notification_data')

    print("listening for notifications . . . ")
    for message in pubsub.listen():
        print(f"Received message: {message}")
        channel_name = message['channel'].decode('utf-8')
        if message['type'] == 'message':
            try:
                event = json.loads(message['data'])
                print(f"Processing event: {event}")

                if channel_name == 'notification_data':
                    create_order_notification_event(event)
                elif channel_name == 'payment_notification_data':
                    create_payment_notification_event(event)

            except Exception as e:
                print(f"Error processing message: {e}")

def create_order_notification_event(data):
    message_dict = {"awaiting dispatch" : f"order number {data['order_id']} is now awaiting dispatch!", "shipped" : f"order number {data['order_id']} has now been shipped!", 
                    "delivered" : f"order number {data['order_id']} has now been delivered!" }
    status = data["status"]
    message_add = f"\nto view more details about your order click here: (insert order link located on the website)"

    try:
        message = client.messages.create(
        to= data["phone"],
        from_="+447492884792",
        body=message_dict[status])    
        print(f"sms delivered, {message.sid}")
        logger.info(json.dumps({"level" : "INFO", "message" : f"sms delivered, {message.sid}", "service" : {"name" : "notification-service"}}))

        message = Mail(
            from_email='heresyexo@gmail.com',
            to_emails=data["email"],
            subject='Order Update',
            html_content=f'<strong>{message_dict[status]}{message_add}</strong>')
        try:
            sg = SendGridAPIClient(api_key = sendgrid_api_key)
            mail_json = message.get()
            response = sg.client.mail.send.post(request_body=mail_json)
            mail_result = {"mail_status_code" : response.status_code, "response_body" : response.body, "response_headers" : response.headers}
            logger.info(json.dumps({"level" : "INFO", "response" : mail_result, "service" : {"name" : "notification-service"}}))

        except Exception as e:
            logger.error(json.dumps({"level" : "ERROR", "error" : f"details, {e}", "service" : {"name" : "notification-service"}}))
            
    except Exception as e:
        logger.error(json.dumps({"level" : "ERROR", "error" : f"details, {e}", "service" : {"name" : "notification-service"}}))
        return

def create_payment_notification_event(data):
    message_dict = {"Paid" : f"Your payment for order {data["order_id"]} has successfully been processed", "Failed" : "Your payment for your order has failed", "Refunded" : "Your payment has successfully been refunded"}
    type = data["type"]
    try:
        message = client.messages.create(
        to= data["contact"],
        from_="+447492884792",
        body=message_dict[type])    
        print(f"sms delivered, {message.sid}")
        logger.info(json.dumps({"level" : "INFO", "message" : f"sms delivered, {message.sid}", "service" : {"name" : "notification-service"}}))

    except Exception as e:
        logger.error(json.dumps({"level" : "ERROR", "error" : f"details, {e}", "service" : {"name" : "notification-service"}}))
        return



if __name__ == '__main__':
    consume_notification_events()

