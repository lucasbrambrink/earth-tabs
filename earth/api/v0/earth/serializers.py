from rest_framework import serializers
from api.models import EarthImage


class EarthImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = EarthImage
        exclude = ('id')
