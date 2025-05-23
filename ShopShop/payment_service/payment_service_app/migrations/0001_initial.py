# Generated by Django 5.1.7 on 2025-03-19 14:28

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Payment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("order_id", models.CharField(max_length=255)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("payment_date", models.DateTimeField(auto_now_add=True)),
                ("payment_method", models.CharField(max_length=255)),
                ("payment_status", models.CharField(max_length=255)),
            ],
        ),
    ]
