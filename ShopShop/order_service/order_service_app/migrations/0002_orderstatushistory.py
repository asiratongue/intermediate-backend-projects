# Generated by Django 5.1.4 on 2025-03-31 09:23

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("order_service_app", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="OrderStatusHistory",
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
                ("old_status", models.CharField(blank=True, max_length=20, null=True)),
                ("new_status", models.CharField(max_length=20)),
                ("timestamp", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="status_history",
                        to="order_service_app.order",
                    ),
                ),
            ],
            options={
                "ordering": ["-timestamp"],
            },
        ),
    ]
