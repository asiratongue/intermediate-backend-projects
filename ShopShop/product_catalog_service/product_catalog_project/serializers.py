from rest_framework import serializers
from .models import Product
import re

class ProductSerializer(serializers.ModelSerializer):

    def validate_product(self, value):      
        if not re.match("^[A-Za-z0-9]*$", value):
            raise serializers.ValidationError("Only letters and numbers are allowed!")
        return value
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'stock', 'image']

