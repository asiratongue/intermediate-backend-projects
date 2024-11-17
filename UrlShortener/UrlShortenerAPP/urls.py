from django.urls import path
from . import views


app_name = "UrlShortenerAPP"

urlpatterns = [
    
    path("shorten/", views.CreateSUrlAPIView.as_view(), name="shorten"),
    path("shorten/<str:shortenedurl>/", views.ShortenUrlOpsAPIView.as_view(), name="shortenOps"),
    path("shorten/<str:shortenedurl>/<str:stats>/", views.ShortenUrlStatsAPIView.as_view(), name="shortenStats"),
    
    ]



# So URLS, is the place where uniform resource locator endpoints are stored, and references for them are made.
# the data and logic required of them is retrieved with .views ygm