from django.shortcuts import render
import requests, json
import phonenumbers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from .models import Order, OrderItem, OrderStatusHistory
from rest_framework import status, permissions
from django.conf import settings
from django.http import HttpResponse
from django.db.models import Sum
from .tasks import send_notification_data
from phonenumber_field.phonenumber import PhoneNumber
from phonenumber_field.validators import validate_international_phonenumber
from django.core.exceptions import ValidationError
from .validate_address import validate_address
from order_service.logger_setup import logger
from order_service.permissions import InternalOrJWTAuthentication

class IsAdminToken(permissions.BasePermission):

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


class CreateOrder(APIView):
    """Create an order, fetching the authenticated users cart"""
    models = Order
    permission_classes = [IsAuthenticated]

    def post(self, request):
        User = get_user_model()
        user = request.user
        print(f"Authenticated user: {user}")

        if not user.is_authenticated:
           
           logger.error(json.dumps({"level" : "ERROR", "error" : {"error": "User not authenticated"}, "service" : {"name" : "order-service"}}))
           return Response({"error": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:

            shipping_addr = request.data.get("shipping", "not provided")
            billing_addr = request.data.get("billing", "not provided")
            phone_num = request.data.get("contact", "not provided")
            
            phone_number = phonenumbers.parse(phone_num, 'GB')

            if not phonenumbers.is_valid_number(phone_number):

                logger.error({"level" : "ERROR", "error" : {"error": f"Invalid phone number: {str(e)}"}, "service" : {"name" : "order-service"}})
                return Response({"error": f"Invalid phone number: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
            
            if shipping_addr == 'not provided':

                logger.error({"level" : "ERROR", "error" : {"error" : "no shipping address was provided"}, "service" : {"name" : "order-service"}})
                return Response({"error" : "no shipping address was provided"}, status=status.HTTP_400_BAD_REQUEST)
            
            if billing_addr == 'not provided':

                logger.error({"level" : "ERROR", "error" : {"error" : "no shipping address was provided"}, "service" : {"name" : "order-service"}})
                return Response({"error" : "no billing address was provided"}, status=status.HTTP_400_BAD_REQUEST)
            
            shipping_validation = validate_address(shipping_addr)
            billing_validation = validate_address(billing_addr)

            if "error" in shipping_validation:

                logger.error(json.dumps({"level" : "ERROR", "error" : shipping_validation, "service" : {"name" : "order-service"}})) 
                return Response(shipping_validation, status=status.HTTP_400_BAD_REQUEST)
            
            if "error" in billing_validation:
                logger.error({"level" : "ERROR", "error" : billing_validation, "service" : {"name" : "order-service"}})
                return Response(billing_validation, status=status.HTTP_400_BAD_REQUEST)

            new_order = Order.objects.create(customer_id = user, shipping_address = shipping_addr, 
                                            billing_address = billing_addr, phone_number = phone_num, total = 0)

            try:
                response = requests.get("http://nginx/api/carts/view/", headers = {"Authorization" : f"{request.headers.get('Authorization')}"}, timeout=10)
                response.raise_for_status()
            except requests.RequestException as e:
                logger.error(json.dumps({"level" : "ERROR", "error" : f"Failed to fetch cart data, details : {e}", "service" : {"name" : "order-service"}}))
                return Response({"error" : f"Failed to fetch cart data, details : {e}"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
            cart_data = response.json()
            new_order.total = cart_data["Grand Total"]
            cart_data.pop('User'), cart_data.pop('id'), cart_data.pop('Grand Total')
            item_data = cart_data

            for k, v in item_data.items():
                OrderItem.objects.create(order = new_order, product_name = str(k), 
                                        quantity = v["quantity"], unit_price = v["unit_price"], subtotal = v["subtotal"])
            all_items = OrderItem.objects.filter(order = new_order)
            new_order.save()

            order_items = [
                {
                    "item_id": str(item.id),
                    "order_id": str(item.order.id),
                    "product": item.product_name, 
                    "quantity": item.quantity,
                    "image" :  item_data[item.product_name]["image"],
                    "description" : item_data[item.product_name]["description"],
                    "unit_price": str(item.unit_price), 
                    "subtotal": str(item.subtotal)
                }
                for item in all_items
            ]
            

            response_dict = {"user" : user.username, 
                            "order id": str(new_order.id), 
                            "shipping address": new_order.shipping_address,
                            "billing address": new_order.billing_address, 
                            "created at": new_order.formatted_create_time(), 
                            "total": str(new_order.total), 
                            "order items:" : order_items}
            
            logger.info(json.dumps({"level" : "INFO", "response" : response_dict, "service" : {"name" : "order-service"}}))
            return Response({"message" : response_dict}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(json.dumps({"level" : "INFO", "error" : {"error" : f"Details: {str(e)}"}, "service" : {"name" : "order-service"}}))
            return Response({"error" : f"Details: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

class OrderEndpoint(APIView):
    models = Order
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        """get order details"""
        try:
            order = Order.objects.get(id = id)
            all_items = OrderItem.objects.filter(order = order)

            try:
                response = requests.get("http://nginx/api/carts/view/", headers = {"Authorization" : f"{request.headers.get('Authorization')}"}, timeout=10)
                response.raise_for_status()
            except requests.RequestException as e:
                logger.error(json.dumps({"level" : "ERROR", "error" : {"error" : f"Failed to fetch cart data, details : {e}"}, "service" : {"name" : "order-service"}}))
                return Response({"error" : f"Failed to fetch cart data, details : {e}"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
            email = order.customer_id.email
            cart_data = response.json()


            order_items = [
            {
                "item id" : str(item.id),
                "order id": str(item.order.id) ,
                "product": item.product_name, 
                "quantity": item.quantity, 
                "unit price": str(item.unit_price), 
                "subtotal": str(item.subtotal),
                "image" : cart_data[item.product_name]["image"],
                "description" : cart_data[item.product_name]["description"]
            }
            for item in all_items
        ]
            response_dict = {"shipping address" : order.shipping_address, "billing address" : order.billing_address,  "contact" : str(order.phone_number),
                        "email" : email, "created at": str(order.created_at), "total": str(order.total), "order items": order_items}
            
            logger.info(json.dumps({"level" : "INFO", "response" : response_dict, "service" : {"name" : "order-service"}}))

            return Response(response_dict, status=status.HTTP_200_OK)
                         
        except Exception as e:

            logger.error(json.dumps({"level" : "ERROR", "error" : {"error" : f"Details {e}"}, "service" : {"name" : "order-service"}}))
            return Response({"error" : f"Details {e}"}, status=status.HTTP_400_BAD_REQUEST)
        
    
    def put(self, request, id):
        """update an order"""

        try:
            order = Order.objects.get(id = id)
            new_shipping = request.data.get("shipping", order.shipping_address)
            new_billing = request.data.get("billing", order.billing_address)
            new_phone = request.data.get("contact", order.phone_number)
    
            phone_number = phonenumbers.parse(new_phone, "GB")
            if not phonenumbers.is_valid_number(phone_number):
                logger.error(json.dumps({"level" : "ERROR", "error" : {"error" : "Invalid phone number"}, "service" : {"name" : "order-service"}}))
                return Response({"error" : "Invalid phone number"}, status=status.HTTP_400_BAD_REQUEST)

            shipping_validation = validate_address(new_shipping)
            billing_validation = validate_address(new_billing)

            if "error" in shipping_validation:
                logger.error(json.dumps({"level" : "ERROR", "error" : shipping_validation, "service" : {"name" : "order-service"}}))  
                return Response(shipping_validation, status=status.HTTP_400_BAD_REQUEST)
            
            if "error" in billing_validation:
                logger.error(json.dumps({"level" : "ERROR", "error" : billing_validation, "service" : {"name" : "order-service"}}))
                return Response(billing_validation, status=status.HTTP_400_BAD_REQUEST)

            order.shipping_address, order.billing_address, order.phone_number = new_shipping, new_billing, new_phone
            if new_phone:
                order.phone_number = new_phone

            order.save()
            response = {"message" : {"new shipping address" : order.shipping_address, "new billing address": order.billing_address, "new phone number" : str(order.phone_number)}}
            logger.info(json.dumps({"level" : "INFO", "response" : response, "service" : {"name" : "order-service"}}))
            return Response(response, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(json.dumps({"level" : "ERROR", "error" : {"error" : f"Details {e}"}, "service" : {"name" : "order-service"}}))
            return Response({"error" : f"Details {e}"}, status=status.HTTP_400_BAD_REQUEST)


class DeleteOrder(APIView):
    """Delete an order"""
    models = Order
    permission_classes = [IsAuthenticated]
    
    def delete(self, request):     
        try:
            deleted_ids = []
            orders_2_delete = request.data.get("orders", None)
            if orders_2_delete == None:
                logger.error(json.dumps({"level" : "ERROR", "error" : {"error" : "order ids not provided"}, "service" : {"name" : "order-service"}}))
                return Response ({"error" : "order ids not provided"}, status=status.HTTP_400_BAD_REQUEST)
            
            for identity in orders_2_delete:
                order = Order.objects.get(id = identity)
                deleted_ids.append(order.id)
                order.delete()
            logger.info(json.dumps({"level" : "info", "response" : {"message" : f"orders {deleted_ids} have been deleted"}, "service" : {"name" : "order-service"}}))
            return Response({"message" : f"orders {deleted_ids} have been deleted"}, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.info(json.dumps({"level" : "ERROR", "error" :{"error" : f"Details {e}"}, "service" : {"name" : "order-service"}}))
            return Response({"error" : f"Details {e}"}, status=status.HTTP_400_BAD_REQUEST)

     

class UpdateOrderStatus(APIView):
    """Update an orders status, sends an SMS + Email notification"""
    models = Order
    permission_classes = [IsAuthenticated]

    def post(self, request, id):

        try:
            user = request.user
            status_update = request.data.get("status", "awaiting payment")
            order_2_update = Order.objects.get(id=id)
            old_status = order_2_update.order_status
            order_2_update.order_status = status_update
            order_2_update.save()
            notification_data = {"email" : user.email, "status" : status_update.lower(), "phone" : str(order_2_update.phone_number), "order_id" : str(order_2_update.id)}
            send_notification_data.delay(data=notification_data)

            response = {"message" : f"order number {order_2_update.id} has been updated from {old_status} to {order_2_update.order_status}"}

            logger.info(json.dumps({"level" : "INFO", "response" : response, "service" : {"name" : "order-service"}}))
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(json.dumps({"level" : "ERROR", "error" : {"error" : f"details: {e}"}, "service" : {"name" : "order-service"}}))
            return Response({"error" : f"details: {e}"}, status=status.HTTP_400_BAD_REQUEST)


class GetOrderHistory(APIView):
    """Get an orders status history"""
    model = OrderStatusHistory
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        user = request.user
        try:
            order_history_queryset = OrderStatusHistory.objects.filter(order=id).order_by('timestamp')
            order_history = [{"old_status" : order.old_status,
                              "new_status" : order.new_status,
                              "timestamp" : str(order.timestamp)} 
                              for order in order_history_queryset]
            
            logger.info(json.dumps({"level" : "INFO", "response" : order_history, "service" : {"name" : "order-service"} }))           
            return Response(order_history, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(json.dumps({"level" : "ERROR", "error" : {"error" :f"details:{e}"}, "service" : {"name" : "order-service"}}))
            return Response({"error" :f"details:{e}"}, status=status.HTTP_400_BAD_REQUEST)


class HealthCheckView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        logger.info(json.dumps({"level" : "INFO", "response" : {"status": "ok"}, "service" : {"name" : "order-service"}}))
        return Response({"status": "ok"}, status=status.HTTP_200_OK)


class GetContactDetails(APIView):
    """Get phone number for SMS (internal use)"""
    model = Order
    permission_classes = [InternalOrJWTAuthentication]

    def get(self, request, id):
        user = request.user
        try:
            order = Order.objects.get(id = id)
            contact = order.phone_number
            return Response ({"contact" : str(contact)}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response ({"error" : f"couldnt find the order {e}"}, status=status.HTTP_400_BAD_REQUEST)