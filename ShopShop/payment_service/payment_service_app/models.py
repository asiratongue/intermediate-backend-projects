from django.db import models

class Payment(models.Model):
    payment_statuses = [('FAILED', 'Failed'), ('COMPLETED', 'Completed'), ('PENDING', 'Pending'), ('REFUNDED', 'Refunded')]

    order_id = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=255)
    payment_status = models.CharField(choices=payment_statuses)
    payment_id = models.CharField(max_length=255, null=True)
    
    
