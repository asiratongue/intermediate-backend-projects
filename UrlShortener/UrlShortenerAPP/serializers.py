from rest_framework import serializers
from UrlShortenerAPP.models import URL

#error could be here, copy asiraproject

class URLSerializer(serializers.ModelSerializer):
    class Meta:
        model = URL
        fields = ['url', 'shortCode', 'createdat', 'updatedat', 'accesscount']

        def create(self, validated_data):
         
            return super().create(validated_data)