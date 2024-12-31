from django.db import models

class ProductTag(models.Model):
    name = models.CharField(
        max_length=100, help_text=("Designates the name of the tag.")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name
class Product(models.Model):

    Name = models.CharField(max_length=250, null=True)
    Cost = models.DecimalField(decimal_places=2, max_digits=10, default=0)
    Quantity = models.IntegerField(default=10)
    tags = models.ManyToManyField(ProductTag, blank=True)