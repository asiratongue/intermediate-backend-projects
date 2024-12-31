from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework import generics
from .serializers import URLSerializer
from .models import URL
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import random
import hashlib
#curl -X POST http://127.0.0.1:8000/UrlShortenerAPI/shorten/ \-H "Content-Type: application/json" \-d '{"url" : "https://www.example.com/some/long/url"}'
#curl -X GET http://127.0.0.1:8000/UrlShortenerAPI/shorten/ac987e/ 
#curl -X PUT http://127.0.0.1:8000/UrlShortenerAPI/shorten/494a97/ \-H "Content-Type: application/json" \-d '{"url" : "https://t.me/BullXBetaBot"}'
#curl -X DELETE http://127.0.0.1:8000/UrlShortenerAPI/shorten/ac987e/
#curl -X GET http://127.0.0.1:8000/UrlShortenerAPI/shorten/ac987e/stats/
#c2685a, ac987e


class CreateSUrlAPIView(APIView):

    def post(self, request):

        serializer = URLSerializer(data=request.data, partial=True)

        
        if serializer.is_valid():
            url = serializer.save()


            random.seed(url.url) 
            unique_hash = hashlib.md5(url.url.encode()).hexdigest()
            shortcode = unique_hash[:6]

            serializer.instance.shortCode = shortcode
            serializer.instance.save()  # Save the instance if shortCode is a model field

            
            return Response({"id" : url.id,
                            "url" : url.url,
                            "shortCode" : url.shortCode,
                            "created at" : url.createdat,
                            "updated at" : url.updatedat
                            }, status=status.HTTP_201_CREATED)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
 
class ShortenUrlOpsAPIView(APIView):

    def get(self, request, shortenedurl = None):
        if shortenedurl:

            try:
                getdata = URL.objects.get(shortCode = shortenedurl)
                getdata.accesscount += 1
                getdata.save()

                return Response({"id" : getdata.id, 
                                 "url" : getdata.url, 
                                 "shortCode": getdata.shortCode, 
                                 "createdAt" : getdata.createdat, 
                                 "updatedAt" : getdata.updatedat,
                                 "accessCount" : getdata.accesscount})

            except URL.DoesNotExist:
                return Response({"error": "URL not found"}, status=status.HTTP_404_NOT_FOUND)
            
        else:
            return Response({"error":"check your request url!"})       
    
    def put(self, request, shortenedurl = None):
        if shortenedurl:

            try:
                url2update = URL.objects.get(shortCode = shortenedurl)
                newurl = request.data.get('url')

                url2update.url = newurl
                url2update.save()

                return Response({"you have successfully updated the url!": f"id:{url2update.id}", "New_Url" : f"{url2update.url}", "shortCode" : f"{url2update.shortCode}"})

            except URL.DoesNotExist:
                return Response({"error": "URL not found"}, status=status.HTTP_404_NOT_FOUND)

        else:
            return Response({"error":"check your request url!"})
        

    def delete(self, request, shortenedurl = None):
        if shortenedurl:

            try:
                url2delete = URL.objects.get(shortCode = shortenedurl)
                url2delete.delete()
                return Response ({"message": "successfully deleted!"}, status=status.HTTP_204_NO_CONTENT)

            except URL.DoesNotExist:
                return Response({"error": "URL not found"}, status=status.HTTP_404_NOT_FOUND)
            
        else:
            return Response({"error":"check your request url!"})
        

class ShortenUrlStatsAPIView(APIView):

    def get(self, request, shortenedurl = None, stats = None):
        if stats and shortenedurl:

            try:
                getdata = URL.objects.get(shortCode = shortenedurl)

                return Response({"id" : getdata.id, 
                                 "url" : getdata.url, 
                                 "shortCode": getdata.shortCode, 
                                 "createdAt" : getdata.createdat, 
                                 "updatedAt" : getdata.updatedat,
                                 "accessCount" : getdata.accesscount})

            except URL.DoesNotExist:
                return Response({"error": "URL not found"}, status=status.HTTP_404_NOT_FOUND)
            
        else:
            return Response({"error":"check your request url!"})       

#Views is where logic and data manipulation for your individual "views"/"pages" are written up, the data they work on is provided by django models, and html templates.
#they return said completed operations either as rendered html pages, or httpresponses, or a model object.