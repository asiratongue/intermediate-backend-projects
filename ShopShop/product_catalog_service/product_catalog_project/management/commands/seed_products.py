from django.core.management.base import BaseCommand
from django.db import connection
from pathlib import Path
import os

image_list = []
cwd = Path(__file__).parent
image_dir = os.path.join(cwd, "seed images")

for root, dirs, files in os.walk(image_dir): 
    for file in files:
        s3_path = os.path.join("images", file)
        image_list.append(s3_path)


class Command(BaseCommand):
    
    def handle(self, *args, **kwargs):

        product_names = ["Wireless Headphones", "Smartphone Stand", "USB-C Hub", "Bluetooth Speaker", "Portable Charger"]

        short_descriptions = ["High-quality wireless headphones with noise cancellation.", "Adjustable stand for smartphones and tablets.",
            "Multi-port USB-C hub with HDMI and USB 3.0.", "Compact Bluetooth speaker with powerful sound.",
            "High-capacity portable charger with fast charging."]

        prices = [79.99, 14.99, 29.99, 39.99, 24.99]

        stock_levels = [150, 300, 200, 120, 250]

        try:
            with connection.cursor() as cursor:
                for data in zip(product_names, short_descriptions, prices, stock_levels, image_list):
                    cursor.execute(f"""INSERT INTO "product_catalog_project_product" (name, description, price, stock, image)
                                    VALUES (%s, %s, %s, %s, %s)""", data)

                self.stdout.write(self.style.SUCCESS("data seeded successfully!"))

        except Exception as e:            
            self.stdout.write(
                self.style.ERROR(f'Error: {str(e)}'))        
            
#docker-compose exec product-service python manage.py seed_products.py