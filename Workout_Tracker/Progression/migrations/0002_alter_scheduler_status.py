# Generated by Django 5.1.3 on 2024-12-19 07:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Progression', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scheduler',
            name='status',
            field=models.CharField(choices=[('STARTED', 'Started'), ('COMPLETED', 'Completed'), ('PENDING', 'Pending')], default='Pending', max_length=20),
        ),
    ]