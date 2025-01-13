from django.urls import path
from . import views

app_name = 'ImageProcessor'

urlpatterns = [
    path('upload/', views.UploadPhoto.as_view(), name='Upload'),
    path('list/', views.GetPhotoIDs.as_view(), name='ListIDS'),
    path('transform/<int:id>/', views.TransformPhoto.as_view(), name='Transform'),
    path('get/<int:id>/', views.RetrieveImage.as_view(), name='GetImage'),
    path('remove/<int:id>/', views.DeleteImage.as_view(), name='GetImage')
]