from django.db import models
from .storage import MediaStorage
import uuid
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class Product(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(max_length=900)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=20)
    image = models.ImageField(max_length=900, upload_to='images/', storage=MediaStorage(), null=True)

    def __str__(self):
        return self.name

