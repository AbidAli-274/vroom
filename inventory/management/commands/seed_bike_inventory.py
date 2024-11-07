import os
import csv
import cloudinary
import cloudinary.uploader
from django.core.management.base import BaseCommand
from inventory.models import BikeInventory

# Configure Cloudinary
cloudinary.config(
    cloud_name='daj0lzvak',
    api_key='222713357542916',
    api_secret='fyA1-yiKYPoL0ODKUWfqNse-D54',
)

class Command(BaseCommand):
    help = 'Seed BikeInventory data'

    def handle(self, *args, **kwargs):
        BikeInventory.objects.all().delete()

        file_path = os.path.join(os.path.dirname(__file__), 'bike_inventory_data.csv')

        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                
                    # Function to convert currency strings to integers
                    def parse_currency(value):
                        return int(value.replace('$', '').replace(',', '')) if value else None

                    # Upload photo to Cloudinary in the "inventory" folder if URL is provided
                    photo_url = row['photo']
                    cloudinary_img_url = None
                    if photo_url:
                        upload_result = cloudinary.uploader.upload(
                            photo_url, 
                            folder='inventory',  # Specify the folder
                            use_filename=True
                        )
                        cloudinary_img_url = upload_result.get('url')
                    # Create the BikeInventory record
                    BikeInventory.objects.create(
                        vehicle=row['vehicle'],
                        photo=cloudinary_img_url,
                        brand=row['brand'],
                        color_edition=row['colourEdition'] or None,
                        license_plate=row['licencePlate'],
                        bike_class=row['class'],
                        daily_deposit=parse_currency(row['dailyDeposit']),
                        monthly_deposit=parse_currency(row['monthlyDeposit']),
                        daily_rental=parse_currency(row['dailyRental']),
                        weekly_rental=parse_currency(row['weeklyRental']),
                        status=row['status'] or None,
                        remarks=row['remarks'] or None
                    )
                except Exception as e:
                    print(f"Failed to insert a bike data: {e}")

        self.stdout.write(self.style.SUCCESS('BikeInventory data seeded successfully'))
