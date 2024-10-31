from django.contrib import admin
from .models import BikeInventory, Addon, RentalLog

class BikeInventoryAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'brand', 'license_plate', 'bike_class', 'status')
    search_fields = ('vehicle', 'brand', 'license_plate')
    list_filter = ('bike_class', 'status')
    ordering = ('brand',)

class AddonAdmin(admin.ModelAdmin):
    list_display = ('name', 'rate')
    search_fields = ('name',)

class RentalLogAdmin(admin.ModelAdmin):
    list_display = ('member', 'vehicle', 'start_datetime', 'end_datetime', 'rental_days', 'rental_price', 'paid')
    search_fields = ('member__full_name', 'vehicle__vehicle', 'paid')
    list_filter = ('paid', 'start_datetime')
    ordering = ('-start_datetime',)


admin.site.register(BikeInventory, BikeInventoryAdmin)
admin.site.register(Addon, AddonAdmin)
admin.site.register(RentalLog, RentalLogAdmin)