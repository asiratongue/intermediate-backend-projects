from django.db import models
from .storage import MediaStorage
import uuid
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    class Meta:
        verbose_name = 'CustomUser'
        verbose_name_plural = 'Users'
        db_table = 'custom_user'


class Product(models.Model):
    name = models.CharField(max_length=900, unique=True)
    description = models.CharField(max_length=900, null=True)
    image = models.ImageField(max_length=900, upload_to='images/', storage=MediaStorage(), null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default = 0.00)

    def __str__(self):
        return self.name


class ShoppingCart(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)  

    def __str__(self):
        return f"Cart for {self.user.username}" 
    
    


class CartItem(models.Model):

    cart = models.ForeignKey(ShoppingCart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    def totalCost(self):
        return float(self.product.price * self.quantity)
    


                                


