# Generated by Django 5.1.2 on 2024-11-12 10:17

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='URL',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=100)),
                ('shortCode', models.CharField(max_length=50)),
                ('createdat', models.DateField(auto_now_add=True, verbose_name='User Created At')),
                ('updatedat', models.DateField(auto_now=True, verbose_name='User Last Updated At')),
            ],
        ),
    ]
