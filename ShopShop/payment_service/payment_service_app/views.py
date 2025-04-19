from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
import stripe, json, logging, uuid, requests, hmac, hashlib, os
from .models import Payment
from django.views.generic import TemplateView
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from dotenv import load_dotenv
from coinbase_commerce.client import Client
from coinbase_commerce.webhook import Webhook
from requests.auth import HTTPBasicAuth
from collections import OrderedDict
from rest_framework.exceptions import ParseError
import paypalrestsdk as paypal
from payment_service.logger_setup import logger
from django.utils.encoding import force_bytes
from .tasks import send_notification_data

stripe.api_key = settings.STRIPE_SECRET_KEY
coinbase_api_key = settings.COINBASE_SECRET_KEY
paypal_client_id = settings.PAYPAL_CLIENT_ID
paypal_client_secret = settings.PAYPAL_CLIENT_SECRET
internal_headers = settings.INTERNAL_API_KEY

class CheckoutOrder(APIView):
    """Allow users to pay for their items using one of three payment methods"""
    permission_classes = [AllowAny]
    model = Payment

    def post(self, request, id):
        line_items = []
        jwt = request.data.get("jwt", 1)
        method = request.data.get("method", "stripe")

        if jwt == 1:
            logger.error(json.dumps({"level" : "ERROR", "error" : {"error" : "no jwt was provided"}, "service" : {"name" : "payment-service"}}))
            return Response ({"error" : "no jwt was provided"}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            response = requests.post("http://nginx/api/users/validate/", headers= {"Authorization" : f"Bearer {jwt}"}, timeout=10)
            if response.status_code == 403:
                logger.error(json.dumps({"level" : "ERROR", "error" : {"error" : "invalid/expired jwt"}, "service" : {"name" : "payment-service"}}))
                return Response ({"error" : "invalid/expired jwt"}, status=status.HTTP_403_FORBIDDEN) 
            else:
                print("Authenticated successfully, loading payment page . . . ")
        except requests.RequestException as e:
            logger.error(json.dumps({"level" : "ERROR", "error" : {"error" : f"failed to fetch order data, details {e}"}, "service" : {"name" : "payment-service"}}))
            return Response({"error" : f"failed to fetch order data, details {e}"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        try:
            response = requests.get(f"http://nginx/api/orders/{id}/", headers = {"Authorization" :f"Bearer {jwt}"}, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(json.dumps({"level" : "ERROR", "error" : {"error" : f"failed to fetch order data, details {e}"}, "service" : {"name" : "payment-service"}}))
            return Response({"error" : f"failed to fetch order data, details {e}"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        order_data = response.json()
        shipping_address, billing_address, contact, created_at, total = order_data.pop("shipping address"), order_data.pop("billing address"), order_data.pop("contact"), order_data.pop("created at"), order_data.pop("total")
        total = float(total)

        if not order_data.get('order items'):
            logger.error(json.dumps({"level" : "ERROR", "error" : {"error" : f"failed to fetch order data, details {e}"}, "service" : {"name" : "payment-service"}}))
            raise ValueError("No order items found in the order data")


        #STRIPE PAYMENT
        if method.lower() == "stripe":
            for order_items in order_data["order items"]:
                    line_items.append(
                    {
                        'price_data': {
                            'currency': 'gbp',
                            'product_data': {
                                'name': order_items["product"], 
                            },
                            'unit_amount': int(float(order_items["unit price"]) * 100),
                            },  
                        'quantity': order_items["quantity"],
                    },
                )
            domain = 'http://localhost/api/payments/'
            checkout_session = stripe.checkout.Session.create(
                payment_method_types = ['card'],
                line_items = line_items,
                mode='payment',
                success_url=domain + 'success/',
                cancel_url = domain + 'cancel/',
                payment_intent_data={"metadata": {"order_id" : "123"}}
            )

            pymnt = Payment.objects.create(order_id = id, amount = total, payment_method = method, 
                                        payment_status = 'Pending', payment_id = checkout_session.id)
            
            status_update = {"status" : "awaiting dispatch"}
            response = requests.post(f'http://nginx/api/orders/status/{id}/', headers= {"Authorization" : f"Bearer {jwt}"}, json=status_update, timeout=10)
            logger.info(json.dumps({"level" : "INFO", "response" : {"payment_id" : pymnt.id, "checkout_url" : checkout_session.url}, "service" : {"name" : "payment-service"}}))
            return Response({"payment_id" : pymnt.id, 'checkout_url' : checkout_session.url}, status=status.HTTP_200_OK)


        #CRYPTO PAYMENT, VIA COINBASE COMMERCE
        elif method.lower() == "crypto":
            coinbase_client = Client(api_key=settings.COINBASE_SECRET_KEY)
            
            charge = coinbase_client.charge.create(
                name=f"Order {order_data['order items'][0]['order id']}",
                description="Payment for your order",
                local_price={"amount" : f"{total}", "currency" : "GBP"},
                pricing_type = "fixed_price",
                redirect_url ="http://localhost/api/payments/success/",
                cancel_url="http://localhost/api/payments/cancel/",
            )
            pymnt = Payment.objects.create(order_id = id, amount = f"{total:.2f}", payment_method = method, 
                                        payment_status = 'Pending', payment_id = charge.id)
            
            status_update = {"status" : "awaiting dispatch"}
            response = requests.post(f'http://nginx/api/orders/status/{id}/', headers= {"Authorization" : f"Bearer {jwt}"}, json=status_update, timeout=10)
            logger.info(json.dumps({"level" : "INFO", "response" : {"checkout_url" : charge.hosted_url}, "service" : {"name" : "payment-service"}}))
            return Response({"checkout_url" : charge.hosted_url}, status=status.HTTP_200_OK)


        #PAYPAL
        elif method.lower() == "paypal":
            headers = {"Content-Type" : "application/x-www-form-urlencoded"}
            data = {"grant_type" : "client_credentials"}
            basicauth = HTTPBasicAuth(paypal_client_id, paypal_client_secret)
            try:
                response = requests.post("https://api-m.sandbox.paypal.com/v1/oauth2/token", auth=basicauth, 
                                        headers=headers, data=data)
                response.raise_for_status()
                if response.status_code == 200:
                    access_token = response.json().get('access_token')
            except requests.RequestException as e:
                return Response({"error" : f"failed to fetch order data, details {e}"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)            

            paypal_request_id = str(uuid.uuid4())
            checkout_headers = {"PayPal-Request-Id" : paypal_request_id,
                                'Content-Type' : 'application/json',
                                'Authorization' : f'Bearer {access_token}'}
            

            
            pp_items_dict = [{"name" : order_unpacked["product"], "description" : order_unpacked["description"], 
                             "unit_amount" : {"currency_code" : "GBP", "value" : order_unpacked["unit price"]}, 
                             "quantity" : order_unpacked["quantity"], "category" : "PHYSICAL_GOODS", "sku": "sku01", 
                             "image_url" : order_unpacked["image"]} for order_unpacked in order_data['order items']]
            
            item_total = sum(float(item["unit_amount"]["value"]) * int(item["quantity"]) for item in pp_items_dict)

            data = {
                    "intent": "CAPTURE",
                    "payment_source": {
                        "paypal": {
                            "experience_context": {
                                "return_url": "http://localhost/api/payments/success/",
                                "cancel_url": "http://localhost/api/payments/cancel/",
                                "user_action": "PAY_NOW",
                                "payment_method_preference" : "IMMEDIATE_PAYMENT_REQUIRED",
                                "landing_page" : "LOGIN",
                                "shipping_preference" : "NO_SHIPPING",
                            }
                        }
                    }, 
                    "purchase_units": [
                        {"amount": {
                            "currency_code": "GBP", 
                            "value": f"{item_total:.2f}", 
                            "breakdown": {"item_total" : {"currency_code" : "GBP", "value" : f"{item_total:.2f}"
                                          },
                            "shipping" : {
                                "currency_code" : "GBP",
                                "value" : "0.00",
                            },
                            "tax_total": {
                                "currency_code" : "GBP",
                                "value" : "0.00",
                            }
                        }
                    },

                    "items": pp_items_dict,
                    "invoice_id" : f"INV-{uuid.uuid4().hex[:6]}",}]
                    }
                                                  
            try:

                checkout_response = requests.post('https://api-m.sandbox.paypal.com/v2/checkout/orders', headers=checkout_headers, json=data)
                checkout_response.raise_for_status()

                checkout_data = checkout_response.json()
                payment_id = checkout_data["id"]
                pymnt = Payment.objects.create(order_id = id, amount = f"{item_total:.2f}", payment_method = method, payment_status = 'Pending', payment_id = payment_id)

                approval_link = next((link["href"] for link in checkout_data["links"] if link["rel"] == "payer-action"), None)
                logger.info({"level" : "INFO", "response" : {"payment link" : f"{approval_link}"}, "service" : {"name" : "payment-service"}})
                return Response ({"payment link" : f"{approval_link}"}, status=status.HTTP_201_CREATED)
            
            except requests.RequestException as e:
                logger.error({"level" : "ERROR", "error" : {"error": f"Failed to create PayPal order: {str(e)}"}, "service" : {"name" : "payment-service"}})
                return Response({"error": f"Failed to create PayPal order: {str(e)}"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    
@csrf_exempt
def StripeWebhook(request):
    """Handles Stripe webhook payment updates through events"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    load_dotenv()
    endpoint_secret = os.environ.get('endpoint_secret')

    print(f"Payload (first 100 chars): {str(payload)[:100]}")

    try:
        print("constructing event . . . ")
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        logger.error({"level" : "ERROR", "error" : {'error': f'Invalid payload, details: {e}'}, "service" : {"name" : "payment-service"}})
        return JsonResponse({'error': f'Invalid payload, details: {e}'}, status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error({"level" : "ERROR", "error" : {'error': f'Invalid signature, details: {e}'}, "service" : {"name" : "payment-service"}})
        return JsonResponse({'error': f'Invalid signature, details: {e}'}, status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        payment_obj = Payment.objects.get(payment_id = session['id'])
        payment_obj.payment_status = "Completed"
        payment_obj.payment_id = session['payment_intent']
        payment_obj.save()
        order_id = payment_obj.order_id

        response = requests.get(f'http://nginx/api/orders/contact/{order_id}/', headers=internal_headers, timeout=10)
        order_data = response.json()
        print(order_data)
        print("LINE 236")
        notification_data = {"contact" : order_data["contact"], "type" : "Paid", "order_id" : order_id}
        send_notification_data.delay(data = notification_data)        

    logger.info({"level" : "INFO", "response" : {'status': 'success'}, "service" : {"name" : "payment-service"}})
    return JsonResponse({'status': 'success'}, status=200)

@csrf_exempt
def CoinbaseWebhook(request):
    """Handles Coinbase webhook payment updates through events"""
    webhook_secret = settings.COINBASE_WEBHOOK_SECRET
    request_sig = request.META.get('HTTP_X_CC_WEBHOOK_SIGNATURE', '')
    request_data = request.body

    if not webhook_secret:
        logger.error(json.dumps({"level": "ERROR", "message": "Coinbase webhook secret not configured."}))
        return HttpResponse(status=500)
    
    if request.method == 'POST':
        try:
            msg = force_bytes(request_data)
            sig = hmac.new(force_bytes(webhook_secret), msg, hashlib.sha256).hexdigest()

            if not hmac.compare_digest(sig, request_sig):
                logger.warning(json.dumps({"level": "WARNING", "message": "Invalid Coinbase webhook signature."}))
                return HttpResponse(status=400)
        
            event_json = json.loads(request_data.decode('utf-8'))
            event_type = event_json['event']['type']
            event_data = event_json['event']['data']
            charge_id = event_data.get('id')

            logger.info(json.dumps({"level": "INFO", "message": f"Received Coinbase webhook event: {event_type}", "charge_id": charge_id}))

            try:
                payment = Payment.objects.get(payment_id=charge_id, payment_method='crypto')
                order_id = payment.order_id
            except Payment.DoesNotExist:
                logger.warning(json.dumps({"level": "WARNING", "message": f"Payment record not found for Coinbase charge ID: {charge_id}"}))
                return HttpResponse(status=200) 

            if event_type == 'charge:confirmed':
                payment.payment_status = 'Paid'
                payment.save()
                logger.info(json.dumps({"level": "INFO", "message": f"Payment confirmed for order: {payment.order_id}", "charge_id": charge_id}))
                response = requests.get(f'http://nginx/api/orders/contact/{order_id}/', headers=internal_headers, timeout=10)
                order_data = response.json()
                notification_data = {"contact" : order_data["contact"], "type" : "Paid", "order_id" : payment.order_id}
                send_notification_data.delay(data = notification_data)

            elif event_type == 'charge:failed':
                payment.payment_status = 'Failed'
                payment.save()
                logger.warning(json.dumps({"level": "WARNING", "message": f"Payment failed for order: {payment.order_id}", "charge_id": charge_id}))
                response = requests.get(f'http://nginx/api/orders/contact/{order_id}/', headers=internal_headers, timeout=10)
                order_data = response.json()
                notification_data = {"contact" : order_data["contact"], "type" : "Failed", "order_id" : payment.order_id}
                send_notification_data.delay(data = notification_data)

            elif event_type == 'charge:pending':
                payment.payment_status = 'Pending'  
                payment.save()
                logger.info(json.dumps({"level": "INFO", "message": f"Payment pending for order: {payment.order_id}", "charge_id": charge_id}))

            elif event_type == 'charge:created':
                logger.info(json.dumps({"level": "INFO", "message": f"Charge created for order: {payment.order_id}", "charge_id": charge_id}))
        
            else:
                logger.info(json.dumps({"level": "INFO", "message": f"Unhandled Coinbase webhook event type: {event_type}", "charge_id": charge_id}))

            return HttpResponse(status=200)
        except json.JSONDecodeError:
            logger.error(json.dumps({"level": "ERROR", "message": "Invalid JSON payload in webhook request."}))
            return HttpResponse(status=400)
        except Exception as e:
            logger.error(json.dumps({"level": "ERROR", "message": f"Error processing Coinbase webhook: {str(e)}", "body": request_data.decode('utf-8') if request_data else ""}))
            return HttpResponse(status=500)
    else:
        return HttpResponse(status=405)



paypal_api = paypal.configure({
    'client_id': settings.PAYPAL_CLIENT_ID,
    'client_secret': settings.PAYPAL_CLIENT_SECRET,
    'mode': 'sandbox'  # 'sandbox' or 'live'
})

class PaypalSignatureVerificationError(ParseError):
    """Handles paypal signature verification errors."""

def verify_webhook_signature(request):
    """
    Verify PayPal webhook signature using both direct API and SDK as fallback
    """
    auth_algo = request.META.get("HTTP_PAYPAL_AUTH_ALGO")
    cert_url = request.META.get("HTTP_PAYPAL_CERT_URL")
    transmission_id = request.META.get("HTTP_PAYPAL_TRANSMISSION_ID")
    transmission_sig = request.META.get("HTTP_PAYPAL_TRANSMISSION_SIG")
    transmission_time = request.META.get("HTTP_PAYPAL_TRANSMISSION_TIME")
    webhook_id = settings.PAYPAL_WEBHOOK_ID
    
    # Use OrderedDict to maintain payload order for signature verification
    ordered_payload = json.loads(request.body, object_pairs_hook=OrderedDict)

    data = {
        'auth_algo': auth_algo,
        'cert_url': cert_url,
        'transmission_id': transmission_id,
        'transmission_sig': transmission_sig,
        'transmission_time': transmission_time,
        'webhook_id': webhook_id,
        'webhook_event': ordered_payload
    }

    try:
        signature_verification = paypal_api.post(
            "/v1/notifications/verify-webhook-signature",
            params=data,
            headers={"Content-Type": "application/json"}
        )
        
        if signature_verification.get("verification_status") == "SUCCESS":
            logger.info(json.dumps({"level" : "INFO", "message" : "webhook signature verified!", "service" : {"name" : "payment-service"}}))
            return True
            
    except Exception as api_err:
        logger.error(json.dumps({"level" : "ERROR", "error" : f"Error verifying event using API: {api_err}", "service" : {"name" : "payment-service"}}))
        try:
            if paypal.WebhookEvent.verify(
                transmission_id,
                transmission_time,
                webhook_id,
                request.body,
                cert_url,
                transmission_sig,
                auth_algo
            ):
                return True
        except Exception as sdk_err:
            logger.error(json.dumps({"level" : "ERROR", "error" : f"Error verifying event using SDK {sdk_err}", "service" : {"name" : "payment-service"}}))
            return("Error verifying event using SDK: %s", sdk_err)

    

@csrf_exempt
def PaypalWebhook(request):
    if request.method != 'POST':
        logger.error({"level" : "ERROR", "error" : "Method not allowed", "service" : {"name" : "payment-service"}})
        return JsonResponse({'error': "Method not allowed"}, status=405)

    try:
        verify_webhook_signature(request)
        event = json.loads(request.body)
        event_type = event.get('event_type')
        

        try:
            if event_type == 'PAYMENT.CAPTURE.COMPLETED':
                payment_id = event['resource'].get('invoice_id') or event['resource'].get('id')
                amount = event['resource']['amount']['value']
                
                logger.info(json.dumps({"level" : "INFO", "response" : f"Payment completed for order {payment_id}, amount {amount}", "service" : {"name" : "payment-service"}}))
                payment_obj = Payment.objects.filter(payment_id=payment_id)
                order_id = payment_obj.order_id 
                payment_obj.payment_status = 'Completed'
                payment_obj.save()

                response = requests.get(f'http://nginx/api/orders/status/{order_id}/', headers=internal_headers, timeout=10)
                order_data = response.json()

                notification_data = {"contact" : order_data["contact"], "type" : "Paid", "order_id" : payment_obj.order_id}
                send_notification_data.delay(data = notification_data)

            elif event_type == 'CHECKOUT.ORDER.APPROVED':
                payment_id = event['resource'].get('invoice_id') or event['resource'].get('id')
                amount = event['resource']['purchase_units'][0]['amount']['value']
                logger.info(json.dumps({"level" : "INFO", "response" : f"Payment completed for order {payment_id}, amount {amount}", "service" : {"name" : "payment-service"}}))
                Payment.objects.filter(payment_id=payment_id).update(payment_status='Completed')

            elif event_type == 'PAYMENT.CAPTURE.DENIED':

                payment_id = event['resource'].get('invoice_id') or event['resource'].get('id')
                logger.info(json.dumps({"level" : "INFO", "response" : f"Payment denied for order {payment_id}", "service" : {"name" : "payment-service"}}))

                payment_obj = Payment.objects.filter(payment_id=payment_id)
                payment_obj.payment_status = 'Failed'
                payment_obj.save()

                response = requests.get(f'http://nginx/api/orders/status/{order_id}/', headers=internal_headers, timeout=10)
                order_data = response.json()

                notification_data = {"contact" : order_data["contact"], "type" : "Failed", "order_id" : payment_obj.order_id}
                send_notification_data.delay(data = notification_data)

            elif event_type == 'PAYMENT.CAPTURE.REFUNDED':
                payment_id = event['resource'].get('invoice_id') or event['resource'].get('id')
                logger.info(json.dumps({"level" : "INFO", "response" : f"Payment refunded for order {payment_id}", "service" : {"name" : "payment-service"}}))
                payment_obj = Payment.objects.filter(payment_id=payment_id)
                payment_obj.payment_status = "Refunded"
                payment_obj.save()
                
                response = requests.get(f'http://nginx/api/orders/contact/{order_id}/', headers=internal_headers, timeout=10)
                order_data = response.json()

                notification_data = {"contact" : order_data["contact"], "type" : "Refunded", "order_id" : payment_obj.order_id}
                send_notification_data.delay(data = notification_data)                                

            else:
                logger.error(json.dumps({"level" : "ERROR", "response" : f"Unhandled event type received: {event_type}", "service" : {"name" : "payment-service"}}))

            logger.info(json.dumps({"level" : "INFO", "response" : {"status": "paypal webhook executed successfully"}, "service" : {"name" : "payment-service"}}))
            return JsonResponse({"status": "paypal webhook executed successfully"}, status=200)

        except KeyError as e:
            logger.error(json.dumps({"level" : "ERROR", "error" : f"Missing expected field in webhook event: {str(e)}", "service" : {"name" : "payment-service"}}))
            return JsonResponse({'error': f'Missing expected field: {str(e)}'}, status=400)
        except Exception as e:
            logger.error(json.dumps({"level" : "ERROR", "error" : f"Error processing event: {str(e)}", "service" : {"name" : "payment-service"}}))
            return JsonResponse({'error': f'Error processing event: {str(e)}'}, status=500)

    except Exception as e:
        logger.error({"level" : "ERROR", "error" : f"Signature verification failed: {str(e)}", "service" : {"name" : "payment-service"}})
        return JsonResponse({'error': 'Signature verification failed'}, status=400)


class SuccessView(TemplateView):
    template_name = "success.html"


class CancelView(TemplateView):
    template_name = "cancel.html"


class RefundEndpoint(APIView):  
    # add paypal + crypto refunds
    def post(self, request, id):
        jwt = request.data.get("jwt", 1)
        reason = request.data.get("reason", None)

        if jwt == 1:
            logger.error(json.dumps({"level" : "ERROR", "error" : {"error" : "no jwt was provided"}, "service" : {"name" : "payment-service"}}))
            return Response ({"error" : "no jwt was provided"}, status=status.HTTP_403_FORBIDDEN)
        if reason == None or reason not in ["duplicate", "fraudulent", "requested_by_customer"]:
            logger.error(json.dumps({"level" : "ERROR", "error" : {"error" : "no reason was given for giving a refund, options: duplicate, fraudulent, requested_by_customer"}, "service" : {"name" : "payment-service"}}))
            return Response ({"error" : "no reason was given for giving a refund, options: duplicate, fraudulent, requested_by_customer"}, status=status.HTTP_400_BAD_REQUEST)
               
        try:
            response = requests.post("http://nginx/api/users/validate/", headers= {"Authorization" : f"Bearer {jwt}"}, timeout=10)
            if response.status_code == 403:
                logger.error(json.dumps({"level" : "ERROR", "error" : {"error" : "invalid/expired jwt"}, "service" : {"name" : "payment-service"}}))
                return Response ({"error" : "invalid/expired jwt"}, status=status.HTTP_403_FORBIDDEN) 
            else:
                print("Authenticated successfully, refunding  . . . ")
        except requests.RequestException as e:
            logger.error(json.dumps({"level" : "ERROR", "error" : {"error" : f"failed to fetch order data, details {e}"}, "service" : {"name" : "payment-service"}}))
            return Response({"error" : f"failed to fetch order data, details {e}"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        pymnt_obj = Payment.objects.get(pk = id)
        if pymnt_obj.payment_method == 'stripe':    

            payment_intent = stripe.PaymentIntent.retrieve(pymnt_obj.payment_id)
            charge_id = payment_intent.latest_charge
            charge = stripe.Charge.retrieve(charge_id)
            try:
                refund = stripe.Refund.create(charge=charge, reason=reason)
                pymnt_obj.status = "Refunded"
                pymnt_obj.save()
                logger.info(json.dumps({"level" : "INFO", "response" : f"payment {pymnt_obj.payment_id} has been refunded", "service" : {"name" : "payment-service"}}))
                return Response({"message" : f"payment {pymnt_obj.payment_id} has been refunded"})
            except Exception as e:
                logger.error(json.dumps({"level" : "ERROR", "error" : {"error" : f"details {e}"}, "service" : {"name" : "payment-service"}}))
                return Response({"error" : f"details {e}"}, status=status.HTTP_400_BAD_REQUEST)


class DeletePayment(APIView):
    def post(self, request):
        jwt = request.data.get("jwt", 1)
        if jwt == 1:
            return Response ({"error" : "no jwt was provided"}, status=status.HTTP_403_FORBIDDEN)        
        try:
            response = requests.post("http://nginx/api/users/validate/", headers= {"Authorization" : f"Bearer {jwt}"}, timeout=10)
            if response.status_code == 403:
                logger.error(json.dumps({"level" : "ERROR", "error" : {"error" : "invalid/expired jwt"}, "service" : {"name" : "payment-service"}}))
                return Response ({"error" : "invalid/expired jwt"}, status=status.HTTP_403_FORBIDDEN) 
            else:
                print("Authenticated successfully, refunding  . . . ")
        except requests.RequestException as e:
            logger.error(json.dumps({"level" : "ERROR", "error" : {"error" : f"failed to fetch order data, details {e}"}, "service" : {"name" : "payment-service"}}))
            return Response({"error" : f"failed to fetch order data, details {e}"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        try:
            deleted_ids = []
            payments_2_delete = request.data.get("payments", None)
            if payments_2_delete == None:
                logger.error(json.dumps({"level" : "ERROR", "error" : {"error" : "payment ids not provided"}, "service" : {"name" : "payment-service"}}))
                return Response ({"error" : "payment ids not provided"}, status=status.HTTP_400_BAD_REQUEST)
            
            for identity in payments_2_delete:
                payment = Payment.objects.get(id = identity)
                deleted_ids.append(payment.id)
                payment.delete()
            logger.info(json.dumps({"level" : "INFO", "response" : {"message" : f"payments {deleted_ids} have been deleted"}, "service" : {"name" : "payment-service"}}))
            return Response({"message" : f"payments {deleted_ids} have been deleted"}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(json.dumps({"level" : "ERROR", "error" : {"error" : f"Details {e}"}, "service" : {"name" : "payment-service"}}))
            return Response({"error" : f"Details {e}"}, status=status.HTTP_400_BAD_REQUEST)
        

class HealthCheckView(APIView):
    def get(self, request):
        logger.info(json.dumps({"level" : "INFO", "response" : {"status": "ok"}, "service" : {"name" : "payment-service"}}))
        return Response({"status": "ok"})


