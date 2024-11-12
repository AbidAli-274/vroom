from rest_framework import serializers
from .models import Addon, BikeInventory, RentalLog


class BikeInventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BikeInventory
        fields = "__all__"

class BikeInventoryLimitedSerializer(serializers.ModelSerializer):
    class Meta:
        model = BikeInventory
        fields = ['id', 'vehicle', 'photo', 'brand', 'color_edition', 'license_plate']


class AddonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Addon
        fields = "__all__"


class RentalLogSerializer(serializers.ModelSerializer):
    paid = serializers.BooleanField(required=False)
    rental_days = serializers.IntegerField(required=False)
    rental_price = serializers.IntegerField(required=False)
    price_deposit = serializers.IntegerField(required=False)
    price_deposit_addon = serializers.IntegerField(required=False)

    class Meta:
        model = RentalLog
        fields = "__all__"

    def create(self, validated_data):
        return self.calculate_and_save(validated_data)

    def update(self, instance, validated_data):
        return self.calculate_and_save(validated_data, instance)

    def calculate_and_save(self, validated_data, instance=None):
        print(validated_data)
        start_datetime = validated_data.get('start_datetime') if instance is None else validated_data.get('start_datetime', instance.start_datetime)
        end_datetime = validated_data.get('end_datetime') if instance is None else validated_data.get('end_datetime', instance.end_datetime)
        vehicle = validated_data.get('vehicle') if instance is None else validated_data.get('vehicle', instance.vehicle)

        # Calculate rental_days if start and end datetimes are available
        if start_datetime and end_datetime:
            rental_days = (end_datetime - start_datetime).days
            validated_data['rental_days'] = rental_days

            # Calculate rental_price based on rental_days
            daily_rental = vehicle.daily_rental or 0
            weekly_rental = vehicle.weekly_rental or 0
            monthly_deposit = vehicle.monthly_deposit or 0
            daily_deposit = vehicle.daily_deposit or 0

            if rental_days < 3:
                rental_price = (daily_rental * rental_days) + 30
            elif 3 <= rental_days <= 6:
                rental_price = daily_rental * rental_days
            elif rental_days == 7:
                rental_price = weekly_rental
            else:
                complete_weeks = rental_days // 7
                leftover_days = rental_days % 7
                rental_price = (weekly_rental * complete_weeks) + (daily_rental * leftover_days)

            validated_data['rental_price'] = rental_price

            # Calculate price_deposit based on rental days
            price_deposit = rental_price + (monthly_deposit if rental_days >= 30 else daily_deposit)
            validated_data['price_deposit'] = price_deposit

            addon_ids = [addon.id if isinstance(addon, Addon) else addon for addon in validated_data.get('addons', [])]
            addon_price = sum(Addon.objects.filter(id__in=addon_ids).values_list('rate', flat=True))
            price_deposit_addon = price_deposit + addon_price
            validated_data['price_deposit_addon'] = price_deposit_addon

        if instance is None:
            validated_data['paid'] = validated_data.get('paid', False)
        else:
            validated_data['paid'] = validated_data.get('paid', instance.paid)

        print(validated_data['paid'])

        addons_data = validated_data.pop('addons', instance.addons if instance else [])


        if instance is None:
            instance = RentalLog.objects.create(**validated_data)
        else:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

        if addons_data:
            instance.addons.set(addon_ids)

        return instance


