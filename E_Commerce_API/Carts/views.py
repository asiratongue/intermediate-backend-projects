from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from .models import Product, CartItem, Cart
import stripe 
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.views.generic import TemplateView
from django.http import  JsonResponse
from django.conf import settings 
import jwt 

stripe.api_key = settings.STRIPE_SECRET_KEY 



class AddToCartAPIView(APIView):

    model = Product
    permission_classes = [IsAuthenticated]

    def get (self, request, id=None):

        if id:

            try:
                Product2Grab = Product.objects.get(pk=id)
                user = request.user 

                Carte, created = Cart.objects.get_or_create(user = user) 
                CartGet = CartItem.objects.filter(cart = Carte, product = Product2Grab).first()

                if CartGet:

                    if Product2Grab.Quantity == 0:
                        return ({"error" : "this item is out of stock, sorry"})
                    
                    else:

                        CartGet.quantity += 1
                        Product2Grab.Quantity -= 1
                        CartGet.save()
                        Product2Grab.save()

                        return Response ({f"you have added the item {CartGet.product.Name} to your basket!": f"cost: {CartGet.product.Cost}, quantity: {CartGet.quantity}"})
                else:

                    CartObj = CartItem.objects.create(cart = Carte, product = Product2Grab)
                    CartObj.quantity += 1
                    CartObj.save()

                    Product2Grab.Quantity -= 1
                    Product2Grab.save()
    
                    return Response ({f"you have added the item {CartObj.product.Name} to your basket!": f"cost: {CartObj.product.Cost}, quantity: {CartObj.quantity}"})
            
            except Product.DoesNotExist:
                    return Response ({"error": "No matches found"},status=status.HTTP_404_NOT_FOUND)
            
        else:
            return Response({"error":"check your url!"},status=status.HTTP_400_BAD_REQUEST) 



class ViewCartAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get (self, request):

        try:
            cartItemz = CartItem.objects.all()
            CartObjList = []
            CartDict = {}
            user = request.user



            for cartObj in cartItemz:
                if cartObj.cart.user == user:
                    CartObjList.append(cartObj)

                else:
                    continue
                
            if CartObjList != []:

                for cartObj in CartObjList:   
                    CartDict[cartObj.id] = {"Product" : cartObj.product.Name, "Quantity" : cartObj.quantity, "cost per item:" : cartObj.product.Cost } 
                
                return Response(CartDict)
            
            else:
                return Response ("your cart is empty!")
            
        except (CartItem.DoesNotExist, AssertionError) as e:
            return Response({"error:" : f"{e}"}, status=status.HTTP_404_NOT_FOUND)   
    
class RemoveFromCartAPIView(APIView):
    def delete (self, request, id=None):        

        if id:

            try:
                Product2Remove = Product.objects.get(pk=id)
                user = request.user
                Carti = Cart.objects.get(user = user)
                ProductGet = CartItem.objects.get(cart = Carti, product = Product2Remove)




                if ProductGet.quantity != 1:
                    Product2Remove.Quantity += 1
                    Product2Remove.save()
                    
                    ProductGet.quantity -= 1
                    ProductGet.save()
                else:
                    Product2Remove.Quantity += 1
                    Product2Remove.save()

                    ProductGet.delete()

                return Response({f"you have deleted the item {ProductGet.product.Name} from your basket! " : "woop woop!"})

            
            except (Product.DoesNotExist, Cart.DoesNotExist, CartItem.DoesNotExist) as e:
                return Response({"error:" : f"{e} (there are no items in your basket!)"}, status=status.HTTP_404_NOT_FOUND)


class StripeCheckoutAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post (self, request):
        line_items = []

        Cartier = CartItem.objects.all()
        for cartObj in Cartier:
            line_items.append(
                {
                    'price_data': {
                        'currency': 'gbp',
                        'product_data': {
                            'name': cartObj.product.Name,
                        },
                        'unit_amount': int(cartObj.product.Cost * 100),
                        },  
                    'quantity': cartObj.quantity,
                },
            )

 

        domain = 'https://vocal-marten-driven.ngrok-free.app/'
        checkout_session = stripe.checkout.Session.create(
            payment_method_types = ['card'],
            line_items= line_items,

            mode='payment',
            success_url=domain + 'success/',
            cancel_url=domain + 'cancel/',

        )
        return JsonResponse({'checkout_url' : checkout_session.url}) 
        

class SuccessView(TemplateView):
    template_name = "success.html"


class CancelView(TemplateView):
    template_name = "cancel.html"