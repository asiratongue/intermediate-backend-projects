# Generated by Django 5.1.4 on 2025-04-02 12:41

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("shopping_cart_app", "0002_product_price"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="description",
            field=models.CharField(max_length=900, null=True),
        ),
    ]
