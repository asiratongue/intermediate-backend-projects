from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Product
from .tasks import publish_product_event

@receiver(post_save, sender=Product)
def Product_created_or_updated(sender, instance, created, **kwargs):

    event_type = 'product.created' if created else 'product.updated'
    product_data = {
        "id" : instance.id,
        "name" : instance.name,
        "description" : instance.description,
        "price" : str(instance.price),
        "stock" : instance.stock,
        "image" : str(instance.image),
    }

    publish_product_event(event_type, product_data)