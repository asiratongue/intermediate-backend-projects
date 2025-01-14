
ImageProcessor app is an app which allows users to register, sign in, upload, and transform their favourite images,  or retrieve individual or all listed images. Users are able to crop, rotate, resize, add filters and much more.         

Built with Django, and PIL as the tool for image manipulation. Cloud storage is run with aws s3, and there is a redis server for caching images at the `/transform` endpoint.  




#### **to run and test on windows** 

1) Clone the repo with svn:  
   `svn export https://github.com/asiratongue/intermediate-backend-projects/tree/main/Workout_Tracker`

2) Create and activate the virtual environment from terminal with:  
`python3 -m venv venv` 
`PS venv\Scripts\activate (on windows)`

3) Install the dependencies from terminal with:  
`pip install -r requirements.txt`

4) Set up a .env file with your AWS s3 bucket credentials, eg:

     
    `# .env`

    `AWS_ACCESS_KEY_ID='YOUR_ACCESS_KEY_ID'`    
    `AWS_SECRET_ACCESS_KEY='YOUR_AWS_SECRET_ACCESS_KEY'`    
    `AWS_STORAGE_BUCKET_NAME='YOUR_AWS_STORAGE_BUCKET_NAME'`    
    `AWS_S3_REGION_NAME='YOUR_AWS_S3_REGION_NAME'`


5) start the redis broker on wsl:  
`sudo service redis-server start`

6) start the django app:  
`python manage.py runserver`


## **Endpoints**


### **Users**

**POST** `/ImageProcessor/register/`   
Register a new user, recieve a JWT code.

**POST** `/ImageProcessor/login/`   
User Login, recieve a JWT code.




### **ImageManagement**

**POST** `upload/`  
Upload an existing image to the app/cloud storage.  


**GET** `list/`  
List all currently uploaded images; returns urls to the cloud location + info about the image.


**GET** `get/<int:id>/`
 Retrieve a single image by ID.


 **DELETE** `remove/<int:id>/`  
 Delete an image from your db and from the cloud.

 
**POST** `transform/<int:id>/`
Make a transformation/series of transformations on image with given ID.


## **Transformation Parameters**
**Resize** - takes 2 arguments, Width and Height, max 10000 pixels for both




**Crop** - takes  4 arguments, X and Y for location of crop, Width and Height for the size of crop.


**Rotate** - takes  one argument, rotation degree.


**TextWatermark** - takes 3 arguments, text, colour (3 unit RGB array), and placement (either TopRight, BottomRight, TopLeft, or BottomLeft)


**ImageWatermark** - takes 3 arguments, imagepath, transparency, and placement (either TopRight, BottomRight, TopLeft, or BottomLeft)


**Flip** - takes one argument, either horizontal or vertical.


**Compression** - takes one argument, compression amount as integer.


**ChangeFormat** - takes one argument, image format to change to. (supports, .jpg, .jpeg, .gif, .png, .tiff)


**Filter** - takes one argument, filter type, available filters are as follows: Grayscale, Sepia, HighContrast, Warmth, Coolness, Vintage, fallenAngel


multiple transformations can be chained like so:

`'{"Crop": {"x": 200, "y": 200, "width" : 500, "height" : 500}, "Rotate": 84}'`


all transformations must be formatted properly in json.


Thank you :)










