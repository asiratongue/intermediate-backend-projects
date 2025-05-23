# Generated by Django 5.1.4 on 2025-01-02 07:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ImageManagement", "0002_imagemodel_delete_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="imagemodel",
            name="source_image",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="edits",
                to="ImageManagement.imagemodel",
            ),
        ),
        migrations.AddField(
            model_name="imagemodel",
            name="type",
            field=models.CharField(
                choices=[("source", "Source Image"), ("edited", "Edited Image")],
                default="source",
                max_length=10,
            ),
        ),
    ]
