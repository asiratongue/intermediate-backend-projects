from django.db import models
import uuid
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    class Meta:
        verbose_name = 'CustomUser'
        verbose_name_plural = 'CustomUsers'
        db_table = 'custom_user'


#make migrations + changes to views
class Order(models.Model):
    order_status_choices = [("awaiting payment", "Awaiting Payment"),("awaiting dispatch", "Awaiting Dispatch"), 
                            ("shipped", "Shipped"), ("delivered", "Delivered"), ("cancelled", "Cancelled")]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    phone_number = PhoneNumberField(null=True)
    order_status = models.CharField(choices = order_status_choices, default = "awaiting payment")  
    total = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.TextField(max_length=900, blank=True)
    billing_address = models.TextField(max_length=700, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def formatted_create_time(self):
        x = self.created_at.strftime('%a %d %b %Y, %I:%M%p')
        return x
    def formatted_update_time(self):
        x = self.updated_at.strftime('%a %d %b %Y, %I:%M%p')
        return x 
    
    def __str__(self):
        return f"Order {self.order_number}"
    
    def save(self, *args, **kwargs):

        if self.pk and not self._state.adding:
            old_status = Order.objects.get(pk=self.pk).order_status
            
            super().save(*args, **kwargs)
            
            if old_status != self.order_status:
                OrderStatusHistory.objects.create(
                    order=self,
                    old_status=old_status,
                    new_status=self.order_status
                )
        else:
            super().save(*args, **kwargs)
            
            OrderStatusHistory.objects.create(
                order=self,
                old_status=None,
                new_status=self.order_status
            )        




class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product_name = models.TextField(max_length=900)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Cart for {self.user.username}" 
    

class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    old_status = models.CharField(max_length=20, null=True, blank=True)
    new_status = models.CharField(max_length=20)
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        if self.old_status:
            return f"{self.order}: {self.old_status} → {self.new_status} at {self.timestamp}"
        return f"{self.order}: Created as {self.new_status} at {self.timestamp}"