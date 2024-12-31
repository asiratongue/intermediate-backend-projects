import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from Workouts.models import Muscle_Group, Exercise


class Command(BaseCommand):
    help = "Seed the database with workout data."

    def add_arguments(self, parser):
        parser.add_argument('--number', type=int, help='Number of workout sessions to create')

    def handle(self, *args, **kwargs):
        number = kwargs.get('number', 1)
        self.stdout.write("Running the custom seed command from workouts app...")

        # Create some Muscle Groups
        muscle_groups = [
            Muscle_Group.objects.get_or_create(name=name)[0]
            for name in ['Chest', 'Back', 'Legs', 'Arms', 'Shoulders', 'Core']
        ]

        exercise_list = ["Push-Up", "Pull-Up", "Squat", "Deadlift", "Bench Press", "Overhead Press", "Bicep Curl", "Tricep Dip", "Lunge", "Plank"]

        # Create some Exercises
        exercises = [
            Exercise.objects.get_or_create(
                name=f"{x}",
                description=f"Description for {x}",
                category=random.choice(['cardio', 'flexibility', 'strength'])
            )[0]
            for x in exercise_list
        ]

        # Assign random Muscle Groups to Exercises
        for exercise in exercises:
            exercise.MuscleGroup.set(random.sample(muscle_groups, k=random.randint(1, 3)))


        self.stdout.write(self.style.SUCCESS(f"Successfully seeded {number} workout sessions."))

#python manage.py seed Workouts --number=5

# run the seeder in django shell()