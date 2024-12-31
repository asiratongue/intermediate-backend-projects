from django.db import models
from django.contrib.auth.models import User



class Muscle_Group(models.Model):
    name = models.CharField(max_length=200)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)


class Exercise(models.Model):

    WORKOUT_TYPES = [
        ('cardio', 'Cardio'),
        ('flexibility', 'Flexibility'),
        ('strength', 'Strength'),
    ]

    name = models.CharField(max_length=200, unique=True)
    description = models.CharField(max_length=2000, blank = True)
    category = models.CharField(choices=WORKOUT_TYPES, default='Cardio', max_length=20)
    MuscleGroup = models.ManyToManyField(Muscle_Group, blank= True)

    @classmethod
    def Create_Exercise(cls, name = 'ultimate real nigga exercise', description = 'blow up your balls', category = 'Strength', MuscleGroup=None):
        exercise = cls.objects.create(
        name=name,
        description=description,
        category=category
    )
    
  
        if MuscleGroup:
            exercise.MuscleGroup.add(*MuscleGroup)
        
        return exercise

    def __str__ (self):
        return f"{self.name}, {self.description}, {self.category}"

class Exercise_Session(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    sets = models.PositiveIntegerField(default=0)
    repetitions = models.PositiveIntegerField(default=0)
    weights = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ['exercise', 'sets', 'repetitions', 'weights']

    @classmethod
    def create_Exercise_Session(cls, user, exercise, sets=10, repetitions=12, weights=100):
        return cls.objects.create(user=user, exercise = exercise, sets = sets, repetitions = repetitions, weights = weights)

    def __str__ (self):
        return f"{self.user}, {self.exercise}, {self.sets}, {self.repetitions}, {self.weights}"

class Workout_Plan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True, unique=True)
    Exercise_Session = models.ManyToManyField(Exercise_Session, blank=True)
    comments = models.CharField(max_length=2000, blank=True)

    class Meta:
        unique_together = ['user', 'name']

    
    def __str__ (self):
        return f"{self.user}, {self.name}, {self.Exercise_Session}, {self.comments}"
