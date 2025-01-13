from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model


# Create your tests here.

class UserTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username='skibidi', password='testpass')
        login = self.client.post('/ImageProcessor/login/', {'username': 'skibidi', 'password': 'testpass'}, format='json')
        self.token = login.data['tokens']['access']
      
    def test_ValidLogin(self):
        response = self.client.post('/ImageProcessor/login/', {'username': 'skibidi', 'password': 'testpass'}, format='json')
        self.assertEqual(response.status_code, 200)
    
    def test_invalidLogin(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post('/ImageProcessor/login/', {'username': 'skibidooi', 'password': 'teostpass'}, format='json')
        self.assertEqual(response.status_code, 401)
        
    def test_invalidCharacterRegister(self):
        response = self.client.post('/ImageProcessor/register/', {'username': 'skib("£*di', 'email' : 'signit@gmail.com', 'password': 'testpass'}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_invalidCharacterLogin(self):
        response = self.client.post('/ImageProcessor/login/', {'username': 'skib("£*di', 'password': 'testpass'}, format='json')
        self.assertEqual(response.status_code, 401)
     
    #Test Trying to register with the same address

    