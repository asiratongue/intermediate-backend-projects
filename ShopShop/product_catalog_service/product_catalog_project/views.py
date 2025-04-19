from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, get_user_model
from .serializers import ProductSerializer
from .models import Product
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from product_catalog_service.logger_setup import logger
import json


User = get_user_model()

class ProductListAPIView(APIView):
    model = Product
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializer 
    def get(self, request):

        try:
            products = Product.objects.all()
            order_items = [
                {
                    "product id" : product.id,
                    "stock" : product.name ,
                    "description" : product.description, 
                    "price" : product.price, 
                    "image url" : product.image.url, 
                    "stock" : product.stock
                }
                for product in products
            ]

            logger.info(json.dumps({"level" : "INFO", "response" : order_items, "service" : {"name" : "product-service"}}))     
            return Response(order_items, status=status.HTTP_200_OK)

        except (Product.DoesNotExist):
            logger.error(json.dumps({"level" : "ERROR", "error" : {"error" : "No matches found"}, "service" : {"name" : "product-service"}}))
            return Response ({"error" : "No matches found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(json.dumps({"level" : "ERROR", "error" : {"error" : str(e)}, "service" : {"name" : "product-service"}}))
            return Response({"error" : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SearchProducts(APIView):
    model = Product
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializer 
    def get(self, request):
        query_dict = {}
        title = request.GET.get('title', '*')
        sort_by = request.GET.get('sort_by', None)

        try:
            max_price = int(request.GET.get('max', 99999))
            min_price = int(request.GET.get('min', 0))
        except ValueError:
            logger.error(json.dumps({"level" : "ERROR", "error" : {"error": "Price values must be integers."}, "service" : {"name" : "product-service"}}))
            return Response({"error": "Price values must be integers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if (not isinstance(title, str) or (max_price < 0 or max_price > 99999) or (min_price < 0 or min_price > 99999)):
                logger.error(json.dumps({"level" : "ERROR", "error" : {"error" : "invalid input values."}, "service" : {"name" : "product-service"}}))
                return Response({"error" : "invalid input values."}, status=status.HTTP_400_BAD_REQUEST)

            if title != '*':
                all_products = Product.objects.filter(name__icontains=title, price__lte=max_price, price__gte = min_price)
            else:
                all_products = Product.objects.filter(price__lte=max_price, price__gte = min_price)

            for product_obj in all_products:
                query_dict[product_obj.name] = {"description" : product_obj.description, "price" : product_obj.price, 
                                                "stock" : product_obj.stock, "image" : product_obj.image.url}
                
            if sort_by == 'ascending':
                sorted_items = sorted(query_dict.items(), key=lambda item: item[1]['price'])

            elif sort_by == 'descending':
                sorted_items = sorted(query_dict.items(), key=lambda item: item[1]['price'], reverse=True)

            elif sort_by == 'a2z':
                sorted_items = sorted(query_dict.items(), key=lambda x: str.lower(x[0]))

            elif sort_by == 'z2a':
                sorted_items = sorted(query_dict.items(), key=lambda x: str.lower(x[0]), reverse=True)

            else:
                sorted_items = query_dict.items()

            sorted_dict = {k: v for k, v in sorted_items}

            logger.info(json.dumps({"level" : "ERROR", "info" : sorted_dict, "service" : {"name" : "product-service"}}))
            return Response(sorted_dict, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(json.dumps({"level" : "ERROR", "error" : sorted_dict, "service" : {"name" : "product-service"}}))
            return Response({"error" : f"details: {e}"}, status=status.HTTP_400_BAD_REQUEST)
        
class RetrieveProduct(APIView):
    model = Product
    permission_classes = [IsAuthenticated]
    def get(self, request, name):
        try:
            product = Product.objects.get(name=name)
            product_details = {
                    "id" : product.id,
                    "name": product.name,
                    "description": product.description, 
                    "price": str(product.price), 
                    "image url": product.image.url, 
                    "stock": product.stock
            }

            logger.info(json.dumps({"level" : "INFO", "info" : product_details,  "service" : {"name" : "product-service"}}))
            return Response(product_details, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(json.dumps({"level" : "ERROR", "error" : {"error" : f"details: {e}"}}) )
            return Response({"error" : f"details: {e}"}, status=status.HTTP_400_BAD_REQUEST)


class ProductAdminViewSet(ModelViewSet):
    #FOR CENTRALISED ADMIN PANEL HEHE!
    pass



class HealthCheckView(APIView):
    def get(self, request):
        logger.info(json.dumps({"level" : "INFO", "message" : "Health check status", "status" : "ok", "service" : {"name" : "product-service"}}))
        return Response({"status": "ok"})