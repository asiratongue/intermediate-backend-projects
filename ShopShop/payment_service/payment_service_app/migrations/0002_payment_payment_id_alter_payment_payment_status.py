# Generated by Django 5.1.4 on 2025-03-23 14:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("payment_service_app", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="payment",
            name="payment_id",
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="payment",
            name="payment_status",
            field=models.CharField(
                choices=[
                    ("FAILED", "Failed"),
                    ("COMPLETED", "Completed"),
                    ("PENDING", "Pending"),
                    ("REFUNDED", "Refunded"),
                ]
            ),
        ),
    ]
