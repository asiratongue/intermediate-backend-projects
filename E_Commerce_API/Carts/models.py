from django.db import models
from django.contrib.auth.models import User
from Products.models import Product




class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    @classmethod
    def create_cart(cls, user):
        return cls.objects.create(user=user)

class CartItem(models.Model):

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)

    def totalCost(self):
        return self.product.Cost * self.quantity
    


    @classmethod
    def create_CartItem(cls, cart):
        return cls.objects.create(cart = cart, product = "x", quantity = 1)