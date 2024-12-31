from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from .models import Product



class ProductsAPIView(APIView):
    model = User
    permission_classes = [IsAuthenticated] 

    def get (self, request):
        
        ProductDict = {}
        product_query = request.GET.get('product')
        price_max = request.GET.get('pricemax')
        if product_query == None and price_max == None:

            try:
                all_products = Product.objects.all()

                for queryobj in all_products:
                    ProductDict[queryobj.id] = {"Product" : queryobj.Name, "Cost" : queryobj.Cost, "In Stock:" : queryobj.Quantity} 

                return Response({"all the products we have in stock:" : ProductDict})
            
            except Product.DoesNotExist:
                return Response({"error": "No matches found"}, status=status.HTTP_404_NOT_FOUND)

        elif price_max == None:

                SearchResult = Product.objects.filter(Name__icontains=product_query)

                if not SearchResult:
                    return Response({"error": "No matches found"}, status=status.HTTP_404_NOT_FOUND)
                else:
                
                    for queryobj in SearchResult:
                        ProductDict[queryobj.id] = {"Product" : queryobj.Name, "Cost" : queryobj.Cost, "In Stock:" : queryobj.Quantity}

                    return Response ({"Search Results from product query!" : ProductDict})
            

        elif product_query == None:

           
            price_max = int(price_max)
            SearchResult2 = Product.objects.filter(Cost__lte=price_max)

            if not SearchResult2:
                return Response({"error": "No matches found"}, status=status.HTTP_404_NOT_FOUND)
            else:

                for queryobj in SearchResult2:
                    ProductDict[queryobj.id] = {"Product" : queryobj.Name, "Cost" : queryobj.Cost, "In Stock:" : queryobj.Quantity}

                return Response ({"Search Results from pricemax query!" : ProductDict})
            


        else:

            SearchResult = Product.objects.filter(Name__icontains=product_query).filter(cost__lte=price_max)
            if not SearchResult2:
                return Response({"error": "No matches found"}, status=status.HTTP_404_NOT_FOUND)
            else:

                for queryobj in SearchResult:
                    ProductDict[queryobj.id] = {"Product" : queryobj.Name, "Cost" : queryobj.Cost, "In Stock:" : queryobj.Quantity}

                return Response ({"Search Results from 2 queries!" : ProductDict})
                