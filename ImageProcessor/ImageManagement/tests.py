from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from pathlib import Path
from ImageManagement.models import ImageModel

#python manage.py test ImageManagement

class ImageManagementTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username='testuser', password='testpass')
        login = self.client.post('/ImageProcessor/login/', {'username': 'testuser', 'password': 'testpass'}, format='json')
        self.token = login.data['tokens']['access'] 
        test_file = SimpleUploadedFile(name= 'test.jpg', content=open('C:/Users/A/Pictures/Cool/test.jpg', 'rb').read(), content_type='image/jpg')        
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        x = self.client.post('/ImageProcessor/upload/', {"Image" : test_file}, format='multipart') 
 
    def test_InvalidUploadImage(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post('/ImageProcessor/upload/')
        self.assertEqual(response.status_code, 400)  

        invalid_file = SimpleUploadedFile(name = 'invalid£file.jpg', content = b'not a real image', content_type='image/jpeg')      
        response = self.client.post('/ImageProcessor/upload/', {"Image" : invalid_file}, format='multipart')           
        self.assertEqual(response.status_code, 400)  

    def test_invalidRetrieveImage(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get('/ImageProcessor/get/234235/') 
        self.assertEqual(response.status_code, 400)

        response2 = self.client.get('/ImageProcessor/get/PrinceNaseem.jpg/')
        self.assertEqual(response2.status_code, 404)     
   
    def test_deleteImageDoesNotExist(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.delete('/ImageProcessor/remove/1243/') 
        self.assertEqual(response.status_code, 404)

        response = self.client.get('/ImageProcessor/remove/PrinceNaseem.jpg/')
        self.assertEqual(response.status_code, 404)         

    def test_NoJwtAccess(self):
        response = self.client.get('/ImageProcessor/get/1/')
        self.assertEqual(response.status_code, 401)  #bugged out fam

    def test_InvalidTokenAccess(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + 'invalid_token')
        response = self.client.get('/ImageProcessor/get/1/')
        self.assertEqual(response.status_code, 401)

    def test_TransformImageDoesNotExist(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post('/ImageProcessor/transform/1243/', {"Crop": {"x": 200, "y": 200, "width" : 500, "height" : 500}}, format='json')                     
        self.assertEqual(response.status_code, 404)

    def test_TransformMispeltKeys(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post('/ImageProcessor/transform/1/', {"Cronp": {"x": 200, "y": 200, "width" : 500, "height" : 500}}, format='json')
        print(response.content)
        self.assertEqual(response.status_code, 400)                  

    def test_TransformEdgeCases(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post('/ImageProcessor/transform/1/', {"Rotate": 438394743978}, format='json')
        print(response.content)
        self.assertEqual(response.status_code, 400)

        response2 = self.client.post('/ImageProcessor/transform/1/', {"Resize": {"width": 49405808, "height": 304242595}}, format='json')
        print(response2.content)        
        self.assertEqual(response.status_code, 400)

        response3 = self.client.post('/ImageProcessor/transform/1/', {"TextWatermark": {"text" : "yoooo", "colour" :  [106, 90, 205] , "Placement" : "BottomRightskrt"}}, format='json' )
        print(response3.content)     
        self.assertEqual(response3.status_code, 400)

        response4 = self.client.post('/ImageProcessor/transform/1/', {"ChangeFormat": "invalidimageformat"}, format='json')
        print(response4.content)
        self.assertEqual(response4.status_code, 400)

        response5 = self.client.post('/ImageProcessor/transform/1/', {"Filter": "khalabandor"}, format='json')
        print(response5.content)
        self.assertEqual(response5.status_code, 400)
        
#python manage.py test ImageManagement

#python manage.py test ImageManagement.tests.ImageManagementTests.test_TransformEdgeCases

#python manage.py test ImageManagement.tests.ImageManagementTests.test_TransformMispeltKeys