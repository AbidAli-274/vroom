from django.db import models
from account.models import Member

class BikeInventory(models.Model):
    vehicle = models.CharField(max_length=100)
    photo = models.CharField(max_length=200, blank=True, null=True)
    brand = models.CharField(max_length=100)
    color_edition = models.CharField(max_length=100, blank=True, null=True)
    license_plate = models.CharField(max_length=20, unique=True)
    bike_class = models.CharField(max_length=50)
    daily_deposit = models.IntegerField(blank=True, null=True)
    monthly_deposit = models.IntegerField(blank=True, null=True)
    daily_rental = models.IntegerField(blank=True, null=True)
    weekly_rental = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.vehicle} ({self.license_plate})"


class Addon(models.Model):
    name = models.CharField(max_length=100)
    rate = models.IntegerField(blank=True, null=True)


class RentalLog(models.Model):
    vehicle = models.ForeignKey(BikeInventory, on_delete=models.CASCADE, related_name='rental_vehicle')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='rental_member')
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    addons = models.ManyToManyField(Addon, related_name='rental_addons', blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    paid = models.BooleanField()
    rental_days = models.IntegerField()
    rental_price = models.IntegerField(blank=True, null=True)
    price_deposit = models.IntegerField(blank=True, null=True)
    price_deposit_addon = models.IntegerField(blank=True, null=True)
    
    def __str__(self):
        return f"Rental Log for {self.member.full_name} - {self.vehicle.vehicle}"
