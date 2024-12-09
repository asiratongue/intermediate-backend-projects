from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from Carts.models import Cart, CartItem
from Products.models import Product



class CartTests(TestCase):

    def setUp(self):

        self.client = APIClient()

        self.user = get_user_model().objects.create_user(username='testuser', password='testpass')
        self.test_cart = Cart.create_cart(user = self.user)
        Product.objects.create(id=1, Name= "Test Product", Cost = 1293, Quantity = 1)
        login = self.client.post('/EcomAPI/login/', {'username': 'testuser', 'password': 'testpass'}, format='json')
        self.token = login.data['tokens']['access']
      
    def test_addInvalidProduct(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get('/EcomAPI/cart/add/12222/')
        self.assertEqual(response.status_code, 404)
        
    def test_addwithoutJWTAuth(self):
        response = self.client.get('/EcomAPI/cart/add/1/')
        self.assertEqual(response.status_code, 401)

    def test_viewemptyCart(self):

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get('/EcomAPI/cart/')
        self.assertEqual(response.status_code, 200)

    def test_addtocart(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get('/EcomAPI/cart/add/1/')
        print(response.data)
        self.assertEqual(response.status_code, 200)


    def test_deleteinvalidproduct(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.delete('/EcomAPI/cart/remove/12222/')
        self.assertEqual(response.status_code, 404)

# viewing an empty cart, 

# deleting invalid product from your cart, deleting when item does not exist