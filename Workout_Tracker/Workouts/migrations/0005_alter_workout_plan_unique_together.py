# Generated by Django 5.1.4 on 2024-12-29 08:51

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("Workouts", "0004_alter_exercise_name_alter_workout_plan_name_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="workout_plan",
            unique_together={("user", "name")},
        ),
    ]