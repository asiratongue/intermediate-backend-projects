# Generated by Django 5.1.3 on 2024-12-15 14:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Workouts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Scheduler',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField()),
                ('duration', models.DurationField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('Active', 'Completed'), ('incomplete', 'Incomplete')], default='Pending', max_length=20)),
                ('workout', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Workouts.workout_session')),
            ],
        ),
    ]