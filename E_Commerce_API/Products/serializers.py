from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):

        def validate_product(self, value):

            import re
            if not re.match("^[A-Za-z0-9]*$", value):
                raise serializers.ValidationError("Only letters and numbers are allowed!")
            return value
        
        class Meta:
            model = Product
            fields = ['Name', 'Cost']
            extra_kwargs = {'id' : {'read_only':True}}
            
        def create(self, validated_data):
        
            return super().create(validated_data)