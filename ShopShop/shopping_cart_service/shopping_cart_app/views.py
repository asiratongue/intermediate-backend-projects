from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import Product, CartItem, ShoppingCart
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
from django.db import transaction
import requests, json
from django.dispatch import receiver
from .models import CartItem
from .tasks import publish_quantity_event
from django.dispatch import Signal
from shopping_cart_service.logger_setup import logger

User = get_user_model()

cart_item_updated = Signal()

@receiver(cart_item_updated)
def CartItem_created_or_updated(sender, **kwargs):
    """
    Receiver for cart_item_updated signal.
    Expected kwargs:
    - instance: CartItem instance
    - quantity: int
    - request_path: str
    
    """
    instance = kwargs['instance']
    quantity = kwargs.get("quantity", 1)
    path = kwargs.get("request_path", '')
    event_type = ''

    if 'api/carts/add/' in path:
        event_type = "quantity.add"

    elif 'api/carts/remove/' in path:
        event_type = "quantity.remove"

    else:
        print("wrong path!")

    cart_data = {"quantity" : quantity,
                 "product" : instance.product.name}
    
    logger.info(json.dumps({
        "level" : "INFO",
        "message" : "receiver trigger",
        "data" : cart_data
    }))

    publish_quantity_event(event_type, cart_data)



class AddToCartAPIView(APIView):
    model = ShoppingCart
    permission_classes = [IsAuthenticated]

    def post (self, request, name):
        user = request.user
        quantity = request.data.get("quantity", 1)
        headers = {'Authorization' : request.headers.get( 'Authorization', '')}


        try:
            response = requests.get(f"http://nginx/api/products/retrieve/{name}", headers=headers, timeout=5)
            if response.status_code != 200:
                logger.error(json.dumps({"level" : "ERROR", "error" : response.text, "service" : {"name" : "shopping-cart-service"}}))
                return Response({'error': response.text}, status=response.status_code)
            data = response.json()
            product = Product.objects.get(name=name)

            if int(data["stock"]) < quantity:
                logger.error(json.dumps({"level" : "ERROR", "error" : f"you are trying to buy more {product.name} than available!",  "service" : {"name" : "shopping-cart-service"} }))

                return Response({"error" : f"you are trying to buy more {product.name} than available!"}, 
                                status=status.HTTP_400_BAD_REQUEST)
            cart, created = ShoppingCart.objects.get_or_create(user = user)
            cart_item, created = CartItem.objects.get_or_create(product = product, cart = cart)
            cart_item_updated.send(sender=CartItem, instance=cart_item, quantity = quantity, request_path = request.path)

            if created == True:
                cart_item.quantity += (quantity-1)
            else:
                cart_item.quantity += quantity

            with transaction.atomic():
                cart.save(), cart_item.save(), product.save()
            response_text = {"message" : f"you have added {quantity} {product.name}(s) to your cart"}

            logger.info(json.dumps({"level" : "INFO", "response" : response_text, "service" : {"name" : "shopping-cart-service"}})) 
            return Response(response_text, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(json.dumps({"level" : "ERROR", "error" : f"exception occurred, {e}",  "service" : {"name" : "shopping-cart-service"} }))
            return Response ({"error" : f"exception occurred, {e}"}, status=status.HTTP_400_BAD_REQUEST)

class RemoveFromCartAPIView(APIView):
    model = ShoppingCart
    permission_classes = [IsAuthenticated]

    def delete (self, request, name):
        user = request.user
        quantity = request.data.get("quantity", 1)

        try:            
            product = Product.objects.get(name=name)
            user_cart = ShoppingCart.objects.get(user = user)
            cart_item = CartItem.objects.get(cart = user_cart, product = product)
            
            if cart_item.quantity < quantity:
                logger.error(json.dumps({"level" : "ERROR", "error" : "cannot remove more items then exist the in cart", "service" : {"name" : "shopping-cart-service"} }))
                return Response({"error" : "cannot remove more items then exist the in cart"}, 
                                status=status.HTTP_400_BAD_REQUEST)
            
            cart_item.quantity -= quantity
            cart_item.save()
            cart_item_updated.send(sender=CartItem, instance=cart_item, quantity = quantity, request_path = request.path)
            if cart_item.quantity == 0:
                cart_item.delete()
            else:
                cart_item.save()
            product.save()

            response = {"message" :f"{quantity} {product.name}(s) successfully deleted" }
            logger.info(json.dumps({"level" : "INFO", "response" : response, "service" : {"name" : "shopping-cart-service"}}))
            return Response({"message" :f"{quantity} {product.name}(s) successfully deleted" }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(json.dumps({"level" : "ERROR", "error" : f"exception occured, {e}", "service" : {"name" : "shopping-cart-service"}}))
            return Response({"error" : f"exception occured, {e}"}, status=status.HTTP_400_BAD_REQUEST)


class ViewCartAPIView(APIView):
    model = ShoppingCart
    permission_classes = [IsAuthenticated]

    def get (self, request):
        user = request.user
        response_dict = {}
        grand_total = 0

        try:
            user_cart = ShoppingCart.objects.get(user=user)
            items = CartItem.objects.filter(cart = user_cart)
            for item in items:
                grand_total += item.totalCost()
                item_dict = {f"quantity": str(item.quantity), "unit_price": str(item.product.price), "image" : item.product.image.url, 
                             "description" : item.product.description, "subtotal": str(item.totalCost())}
                response_dict[item.product.name] = item_dict

            response_dict["User"] = user.username
            response_dict["id"] = user_cart.id
            response_dict["Grand Total"] = str(grand_total)
            logger.info(json.dumps({"level" : "INFO", "response" : response_dict, "service" : {"name" : "shopping-cart-service"}}))
            return Response(response_dict)
        except Exception as e:
            logger.error(json.dumps({"level" : "ERROR", "error" : f"exception occured, {e}", "service" : {"name" : "shopping-cart-service"}}))
            return Response({"error" : f"exception occured, {e}"}, status=status.HTTP_400_BAD_REQUEST) 


class HealthCheckView(APIView):
    def get(self, request):
        logger.info(json.dumps({"level" : "INFO", "message" : "Health check status", "status" : "ok", "service" : {"name" : "shopping-cart-service"}}))
        
        return Response({"status": "ok"})
