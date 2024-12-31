from django.db import models
from django.contrib.auth.models import User
from Workouts.models import Workout_Plan

#YYYY-MM-DD HH:MM:SS


class Scheduler(models.Model):
    status_options = [('STARTED', 'Started'), ('COMPLETED', 'Completed'), ('PENDING', 'Pending')]

    workout = models.ForeignKey(Workout_Plan, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, default=None)
    start_time = models.DateTimeField()   #you cant have a start_time set for the same time as another workout! 
    duration = models.DurationField()
    status = models.CharField(choices=status_options, default='PENDING', max_length=20)


