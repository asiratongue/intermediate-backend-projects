# Generated by Django 5.1.5 on 2025-01-26 09:52

import MovieReservations.models
import MovieReservations.storage
import django.core.validators
import simple_history.models
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Genre",
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
                ("name", models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name="HistoricalTransaction",
            fields=[
                (
                    "id",
                    models.BigIntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                (
                    "amount",
                    models.DecimalField(decimal_places=2, max_digits=10, null=True),
                ),
                ("transaction_date", models.DateTimeField(blank=True, editable=False)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("approved", "Approved"),
                            ("declined", "Declined"),
                            ("refunded", "Refunded"),
                            ("partial_refund", "Partial Refund"),
                        ],
                        default="Refunded",
                        max_length=20,
                    ),
                ),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")],
                        max_length=1,
                    ),
                ),
            ],
            options={
                "verbose_name": "historical transaction",
                "verbose_name_plural": "historical transactions",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="Movie",
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
                ("title", models.CharField(max_length=50)),
                ("description", models.CharField(max_length=500, null=True)),
                (
                    "poster",
                    models.ImageField(
                        storage=MovieReservations.storage.MediaStorage(),
                        upload_to="Posters/",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="MovieScreening",
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
                (
                    "showtime",
                    models.DateTimeField(
                        validators=[MovieReservations.models.future_date_validator]
                    ),
                ),
                (
                    "price",
                    models.DecimalField(decimal_places=2, max_digits=10, null=True),
                ),
                (
                    "seats",
                    models.PositiveIntegerField(
                        validators=[django.core.validators.MaxValueValidator(500)]
                    ),
                ),
                (
                    "seats_sold",
                    models.PositiveIntegerField(
                        default=0,
                        validators=[django.core.validators.MaxValueValidator(100)],
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Revenue",
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
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("month", models.DateField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Ticket",
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
                ("unique_code", models.UUIDField(default=uuid.uuid4, editable=False)),
                ("cost", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("valid", "Valid"),
                            ("used", "Declined"),
                            ("cancelled", "Refunded"),
                        ],
                        default="Valid",
                        max_length=30,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Transaction",
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
                (
                    "amount",
                    models.DecimalField(decimal_places=2, max_digits=10, null=True),
                ),
                ("transaction_date", models.DateTimeField(auto_now_add=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("approved", "Approved"),
                            ("declined", "Declined"),
                            ("refunded", "Refunded"),
                            ("partial_refund", "Partial Refund"),
                        ],
                        default="Refunded",
                        max_length=20,
                    ),
                ),
            ],
        ),
    ]
