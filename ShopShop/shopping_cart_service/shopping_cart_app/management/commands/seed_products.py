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

        try:
            with connection.cursor() as cursor:
                for data in zip(product_names, image_list):
                    cursor.execute(f"""INSERT INTO "shopping_cart_app_product" (name,image)
                                    VALUES (%s, %s)""", data)

                self.stdout.write(self.style.SUCCESS("data seeded successfully!"))

        except Exception as e:            
            self.stdout.write(
                self.style.ERROR(f'Error: {str(e)}'))        