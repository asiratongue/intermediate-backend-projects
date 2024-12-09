from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model


class CartTests(TestCase):

    def setUp(self):

        self.client = APIClient()

        self.user = get_user_model().objects.create_user(username='testuser', password='testpass')
        login = self.client.post('/EcomAPI/login/', {'username': 'testuser', 'password': 'testpass'}, format='json')
        self.token = login.data['tokens']['access']

    def test_unauthenticatedviewingstock(self):
        response = self.client.get('/EcomAPI/product/')
        self.assertEqual(response.status_code, 401)

    def test_ProductQueryThatDoesntExist(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get('/EcomAPI/product/?product=zdwsafasf')
        self.assertEqual(response.status_code, 404)

    def test_PriceQueryThatDoesntExist(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get('/EcomAPI/product/?pricemax=34202485')
        self.assertEqual(response.status_code, 404)

