from rest_framework import serializers
from .models import Addon, BikeInventory, RentalLog


class BikeInventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BikeInventory
        fields = ['id', 'vehicle', 'photo', 'brand', 'color_edition', 'license_plate']


class AddonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Addon
        fields = "__all__"


class RentalLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = RentalLog
        fields = "__all__"