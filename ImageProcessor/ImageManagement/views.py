import PIL.Image
import PIL.ImageFilter
import PIL.ImageOps
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from .models import ImageModel
from rest_framework import status
import PIL, os, boto3, redis
from io import BytesIO
from PIL import ImageFont
from PIL import ImageDraw
from django.core.files.base import ContentFile 
from . import Tables
from django.core.cache import cache
from rest_framework.throttling import UserRateThrottle
from pathlib import Path

s3_client = boto3.client('s3')
r = redis.Redis(host='localhost', port=6379, db=0)


class UploadPhoto(APIView):
    model = ImageModel
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    throttle_classes = [UserRateThrottle] 

    def post(self, request):
        user = request.user
        try:
            if 'Image' not in request.FILES:
                return Response({"error" : "No image provided"}, status=status.HTTP_400_BAD_REQUEST)
            
            Image_file = request.FILES.get('Image')

            if Image_file.size < 10000:
                return Response({"error" : "invalid file path or path does not exist"}, status=status.HTTP_400_BAD_REQUEST)
            
            ImageObj = ImageModel.objects.create(user = user, image = Image_file) 
            ImageObj.save()
            basename = str(ImageObj.image.name).split('Images/', 1)[1]
            extension = os.path.splitext(basename)[1]
  

            return Response({"message" : f"you have successfully uploaded {ImageObj.image.name}",
                            "url" : ImageObj.image.url,
                            "metadata": {"image size:" :f"{ImageObj.image.size}",
                                        "image width:" : f"{ImageObj.image.width}",
                                        "image extension:" : f"{extension}"} 
                            })
        except ValueError as e:
            return Response({"error" : f"{e}"}, status=status.HTTP_400_BAD_REQUEST)
        
class GetPhotoIDs(APIView):
    model = ImageModel
    permission_classes = [IsAuthenticated] 
    throttle_classes = [UserRateThrottle] 
 
    def get(self, request):
        user = request.user
        try:
            IDList = []
            ImageObjs = ImageModel.objects.filter(user = user)
            return Response({"Images" :f"{[["ID: " + obj.id, "SIZE: " +  obj.image.size, "URL: " +  obj.image.url] for obj in ImageObjs]}"}, 
                            status=status.HTTP_200_OK) # return the sizes too!
        
        except ImageModel.DoesNotExist:
            return Response({"Error" : "no images were found"}, status=status.HTTP_404_NOT_FOUND)
        
class RetrieveImage(APIView):
    model = ImageModel
    permission_classes = [IsAuthenticated] 
    throttle_classes = [UserRateThrottle] 
 
    def get(self, request, id):
        try:
            ImageGet = ImageModel.objects.get(pk = id)
            return Response({"Message" : f"Image {ImageGet.id} retrieved successfully", 
                                "Image size" : f"{ImageGet.image.size}",
                                "Image url" : f"{ImageGet.image.url}"}, status=status.HTTP_200_OK)
        
        except ImageModel.DoesNotExist:
            return Response({"Error" : "no images were found"}, status=status.HTTP_400_BAD_REQUEST)
            
class DeleteImage(APIView):
    model = ImageModel
    permission_classes = [IsAuthenticated] 
    throttle_classes = [UserRateThrottle] 
 
    def delete(self, request, id):   
            try:
                ImageGet = ImageModel.objects.get(pk = id)
                s3key = "media/" + ImageGet.image.name
                s3_client.delete_object(Bucket = 'imageprocessingbucket2', Key= s3key)
                ImageGet.delete()


                return Response({"Message" : f"Image deleted successfully!"}, status=status.HTTP_200_OK)
            
            except ImageModel.DoesNotExist:
                return Response({"Error" : "no images were found"}, status=status.HTTP_404_NOT_FOUND)           


class TransformPhoto(APIView): 
    model = ImageModel
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle] 

    def __init__(self, **kwargs):

        self.operations = {
        "Resize" : self.ResizeImage,
        "Crop" :  self.CropImage,
        "Rotate" : self.RotateImage,
        "TextWatermark" : self.TextWatermark,
        "ImageWatermark" : self.ImageWatermark,
        "Flip" : self.FlipImage,
        "Compression" : self.CompressImage,
        "ChangeFormat" : self.ChangeFormat,
        "Filter" : self.ApplyFilters
        }
        super().__init__(**kwargs)   

    def post(self, request, id=None): 

        if id:
            try:
                user = request.user
                image = ImageModel.objects.get(pk = id) 

                x = self.process(request, id) 
                Img2Edit = x[-1]

                if isinstance(Img2Edit, Response):
                    return(Img2Edit)
                
                if isinstance(Img2Edit, str):
                    return Response({"error": Img2Edit}, status=status.HTTP_400_BAD_REQUEST)
                
                elif isinstance(Img2Edit, ContentFile):
                    DjangoImgObj = Img2Edit
                    basename = str(image.image.name).split('Images/', 1)[1]                
                    prename = os.path.splitext(basename)[0] 
                    DjangoImgObj.name = prename + "." + DjangoImgObj.name 

                else:
                    Img2Edit_io = BytesIO()
                    Img2Edit.save(Img2Edit_io, format='PNG')
                    Img2Edit_io.seek(0)
                    basename = str(image.image.name).split('Images/', 1)[1]
                    prename = os.path.splitext(basename)[0] 
                    ImageName = prename + ".png"
                    DjangoImgObj = ContentFile(Img2Edit_io.read(), name = ImageName)

                TransformedImage = ImageModel.objects.create(user = user, image = DjangoImgObj, source_image = image)

                return Response({"Message!" :  "Transformation Success", "url" :f"{TransformedImage.image.url}"}, status=status.HTTP_200_OK)
            
            except ImageModel.DoesNotExist:
                return Response({"error" : "invalid ID/Image does Not exist"}, status=status.HTTP_404_NOT_FOUND)

    def process(self, request, id):
        Image = ImageModel.objects.get(pk = id)
        results = []
        stored_etag = cache.get(f"etag_{id}")
 

        try:
            if stored_etag != None:
                s3key = "media/" + Image.image.name
                s3_response = s3_client.get_object(Bucket = 'imageprocessingbucket2', Key = s3key, IfNoneMatch=stored_etag)
                new_etag = s3_response('ETag')
                cache.set(f'etag_{id}', new_etag)
                image_data = s3_response['Body'].read()
                r.set(f"image_{id}", image_data)

            else:
                s3key = "media/" + Image.image.name
                print(s3key)
                s3_response = s3_client.get_object(Bucket = 'imageprocessingbucket2', Key = s3key)
                new_etag = s3_response['ETag']
                cache.set(f'etag_{id}', new_etag)
                image_data = s3_response['Body'].read()
                r.set(f"image_{id}", image_data)

        except s3_client.exceptions.ClientError as e:
            if e.response['Error']['Code'] == '304':

                image_data = r.get(f"image_{id}")

            else:
                raise
        
        img = PIL.Image.open(BytesIO(image_data))
        for i, (operation, params) in enumerate(request.data.items()):
            
            if operation not in self.operations:
                results.append(f"Error: Unknown operation {operation}")
                continue
            
            try:
                if i == 0:                   
                    results.append(self.operations[operation](img, request))               
                else:
                    results.append(self.operations[operation](results[i-1], request))

            except Exception as e:
                results.append(f"Error: {str(e)}") 

        return results
 
    def ResizeImage(self, imagex, request): 
 
        try:
            Resizedata = (request.data["Resize"]["width"], request.data["Resize"]["height"])


            if isinstance(imagex, ImageModel):                    
                Img2Edit = PIL.Image.open(imagex.image)

            else:
                Img2Edit = imagex
                
            if (Resizedata[0] > 10000 or Resizedata[0] < 0) or (Resizedata[1] > 10000 or Resizedata[1] < 0):
                return Response({"error": "you can resize up to 10000 pixels, no negative numbers allowed "}, status=status.HTTP_400_BAD_REQUEST)


            Img2Edit  = Img2Edit.resize(size= Resizedata) 
            return (Img2Edit)                
                
        except KeyError as e:
              return Response ({"KeyError" : f"{e}"}, status=status.HTTP_400_BAD_REQUEST)
        
        except ImageModel.DoesNotExist as e:
             return Response ({"error" : f"{e}"}, status=status.HTTP_404_NOT_FOUND)
       
    def CropImage(self, imagex, request): 

        try:
            Cropdata = (request.data["Crop"]["x"], request.data["Crop"]["y"], request.data["Crop"]["width"], request.data["Crop"]["height"]) 
            if isinstance(imagex, ImageModel):                    
                Img2Edit = PIL.Image.open(imagex.image)

            else:
                Img2Edit = imagex
             
            if (Cropdata[0] > Img2Edit.width or Cropdata[1] > Img2Edit.height):
                return Response({"error": "invalid coordinates (further than image)"}, status=status.HTTP_400_BAD_REQUEST)
                            
            if (Cropdata[2] > Img2Edit.width or Cropdata[3] > Img2Edit.height):
                return Response({"error": "invalid crop value (larger than image)"}, status=status.HTTP_400_BAD_REQUEST)
            
            Img2Edit  = Img2Edit.crop(Cropdata)
            return (Img2Edit)     
            
        except KeyError as e:
             return Response ({"KeyError" : f"{e}"}, status=status.HTTP_400_BAD_REQUEST)
        
        except ImageModel.DoesNotExist as e:
             return Response ({"error" : f"{e}"}, status=status.HTTP_404_NOT_FOUND)
        
    def RotateImage(self, imagex, request):  #maybe need 2 write serialisers for these

        try:

            if isinstance(imagex, ImageModel):                    
                Img2Edit = PIL.Image.open(imagex.image)
                
            else:
                Img2Edit = imagex

            if request.data["Rotate"] > 3600 or request.data["Rotate"] < -3600:
                return Response({"error": "max limit is 10 rotations (3600, or -3600 degrees)"}, status=status.HTTP_400_BAD_REQUEST)
            
            Img2Edit  = Img2Edit.rotate(request.data["Rotate"])
            return (Img2Edit)
                 
        except KeyError as e:
             return Response ({"KeyError" : f"{e}"}, status=status.HTTP_400_BAD_REQUEST)
        
        except ImageModel.DoesNotExist as e:
             return Response ({"error" : f"{e}"}, status=status.HTTP_404_NOT_FOUND)
                    

    def TextWatermark(self, imagex, request):
        
        try:
            WatermarkText = request.data["TextWatermark"]["text"]
            WatermarkColour  = request.data["TextWatermark"]["colour"]
            colour_tuple = tuple(WatermarkColour)
            WatermarkPlacement  = request.data["TextWatermark"]["Placement"]  
            if isinstance(imagex, ImageModel):                    
                Img2Edit = PIL.Image.open(imagex.image)
            else:
                Img2Edit = imagex 

            draw = ImageDraw.Draw(Img2Edit)
            w, h = Img2Edit.size
            margin_x = int(w / 20)  
            margin_y = int(h / 20)

            if WatermarkPlacement == "TopLeft":
                x, y = margin_x, margin_y
            elif WatermarkPlacement == "TopRight":
                x, y = w - margin_x, margin_y 
            elif WatermarkPlacement == "BottomLeft":
                x, y = margin_x, h - margin_y  
            elif WatermarkPlacement == "BottomRight":
                x, y = w - margin_x, h - margin_y  

            else:
                return Response({"error" : "mispelt placement - check your positioning"}, status=status.HTTP_400_BAD_REQUEST)
       
            if x > y:
                font_size = margin_y*5
            elif y > x:
                font_size = margin_x*5
            else:  
                font_size = margin_x*5
            
            font = ImageFont.truetype("arial.ttf", int(font_size/10))
 
            draw.text((x, y), WatermarkText, fill=colour_tuple, font=font, anchor='ms')
            return (Img2Edit)
            
        except KeyError as e:
             return Response ({"KeyError" : f"{e}"}, status=status.HTTP_400_BAD_REQUEST)
        
        except ImageModel.DoesNotExist as e:
             return Response ({"error" : f"{e}"}, status=status.HTTP_404_NOT_FOUND)                 
  

    def ImageWatermark(self, imagex, request):  
         
         try:
            WatermarkPath = request.data["ImageWatermark"]["Image"]
            Transparency = request.data["ImageWatermark"]["Transparency"]
            WatermarkPlacement = request.data["ImageWatermark"]["Placement"]
            watermarkOpen = PIL.Image.open(WatermarkPath)
            watermark = watermarkOpen.copy()
            watermark = watermark.convert('RGBA')
            if isinstance(imagex, ImageModel):                    
                Img2Edit = PIL.Image.open(imagex.image)
            else:
                Img2Edit = imagex  

            alpha = watermark.split()[3]
            alpha = alpha.point(lambda p: p* (Transparency  / 255))   
            watermark.putalpha(alpha)
            w, h = Img2Edit.size
            margin_x = int(w / 20)  
            margin_y = int(h / 20)

            if WatermarkPlacement == "TopLeft":
                x, y = margin_x, margin_y
            elif WatermarkPlacement == "TopRight":
                x, y = w - margin_x, margin_y 
            elif WatermarkPlacement == "BottomLeft":
                x, y = margin_x, h - margin_y  
            elif WatermarkPlacement == "BottomRight":
                x, y = w - margin_x, h - margin_y

            else:
                return Response({"error" : "mispelt placement - check your positioning"}, status=status.HTTP_400_BAD_REQUEST)

            Img2Edit.paste(watermark, (x, y), watermark)

            return (Img2Edit)
                          
         except KeyError as e:
             return Response ({"KeyError" : f"{e}"}, status=status.HTTP_400_BAD_REQUEST)
         
         except OSError as e:
             return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        
         except ImageModel.DoesNotExist as e:
             return Response ({"error" : f"{e}"}, status=status.HTTP_404_NOT_FOUND)  
         
    def FlipImage(self, imagex, request):

        try:
            if isinstance(imagex, ImageModel):                    
                Img2Edit = PIL.Image.open(imagex.image)
            else:
                Img2Edit = imagex  

            if request.data["Flip"] == "Horizontal":
                Img2Edit  = Img2Edit.transpose(PIL.Image.FLIP_LEFT_RIGHT)

            elif request.data["Flip"] == "Vertical":
                Img2Edit  = Img2Edit.transpose(PIL.Image.FLIP_TOP_BOTTOM)

            return (Img2Edit)     
            
        except KeyError as e:
             return Response ({"KeyError" : f"{e}"}, status=status.HTTP_400_BAD_REQUEST)
        
        except ImageModel.DoesNotExist as e:
             return Response ({"error" : f"{e}"}, status=status.HTTP_404_NOT_FOUND)
        
    def CompressImage(self, imagex, request):

        try:
            quality = request.data["Compression"]
            if isinstance(imagex, ImageModel):                    
                Img2Edit = PIL.Image.open(imagex.image) 
            else:
                Img2Edit = imagex  
 
            Img2Edit_io = BytesIO()
            Img2Edit = Img2Edit.save(Img2Edit_io, quality=quality,  format='JPEG', optimize=True)
            Img2Edit_io.seek(0)
            DjangoImgObj = ContentFile(Img2Edit_io.read(), name = 'jpg')            
            return (DjangoImgObj)     
            
        except KeyError as e:
             return Response ({"KeyError" : f"{e}"}, status=status.HTTP_400_BAD_REQUEST)
        
        except ImageModel.DoesNotExist as e:
             return Response ({"error" : f"{e}"}, status=status.HTTP_404_NOT_FOUND)
        
    def ChangeFormat(self, imagex, request):

        try:
            Type = request.data["ChangeFormat"]
            if isinstance(imagex, ImageModel):                    
                Img2Edit = PIL.Image.open(imagex.image)
            else: 
                Img2Edit = imagex

            Img2Edit_io = BytesIO()

            Img2Edit = Img2Edit.save(Img2Edit_io,  format=Type, optimize=True)  
            Img2Edit_io.seek(0)
            DjangoImgObj = ContentFile(Img2Edit_io.read(), name = str(Type))            
            return (DjangoImgObj)
            
        except KeyError as e:
             return Response ({"KeyError" : f"{e}"}, status=status.HTTP_400_BAD_REQUEST)
        
        except ImageModel.DoesNotExist as e:
             return Response ({"error" : f"{e}"}, status=status.HTTP_404_NOT_FOUND)
        
    def ApplyFilters(self, imagex, request):

        try:
            Filter = request.data["Filter"]
            print(Filter)

            if isinstance(imagex, ImageModel):                    
                Img2Edit = PIL.Image.open(imagex.image)
            else:
                Img2Edit = imagex

            if Filter == "Grayscale":                                 
                Img2Edit = PIL.ImageOps.grayscale(image=Img2Edit)

            elif Filter == "Sepia":  
                Img2Edit = Tables.sepia(Img2Edit)

            elif Filter == "HighContrast":  
                Img2Edit = Tables.HighContrast(Img2Edit)

            elif Filter == "Warmth":  
                Img2Edit = Tables.Warmth(Img2Edit)

            elif Filter == "Coolness":  
                Img2Edit = Tables.Coolness(Img2Edit)

            elif Filter == "Vintage":  
                Img2Edit = Tables.Vintage(Img2Edit)

            elif Filter == "fallenAngel":  
                Img2Edit = Tables.fallenAngel(Img2Edit)

            else:
                return Response({"error": "invalid filter/filter doesnt exist"}, status=status.HTTP_400_BAD_REQUEST)
 
            return (Img2Edit)
            
        except KeyError as e:
             return Response ({"KeyError" : f"{e}"}, status=status.HTTP_400_BAD_REQUEST)
        
        except ImageModel.DoesNotExist as e:
             return Response ({"error" : f"{e}"}, status=status.HTTP_404_NOT_FOUND)            