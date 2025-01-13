from .models import ImageModel, Metadata
from rest_framework import serializers


class ImageModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageModel
        fields = ['user', 'image', 'size', 'created_at', 'type', 'source_image']
