from rest_framework import serializers
from .models import Scheduler, Workout_Plan
from django.utils.dateparse import parse_datetime
from datetime import timedelta, datetime 
from django.utils import timezone               

class SchedulerObjSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scheduler
        fields = ['workout', 'start_time', 'duration', 'status', 'user']

    start_time = serializers.DateTimeField()
    duration = serializers.DurationField()

    def validate_start_time(self, value):

        if value < timezone.now():
            raise serializers.ValidationError("Cannot Schedule Workouts in the past!")
        if not isinstance(value, datetime):
            raise serializers.ValidationError("must be a datetime object!")
        return value
    
    def validate_duration(self, value):

        if value < timedelta(minutes=5):
            raise serializers.ValidationError("Scheduled workout must be at least 5 minutes long!")
        if not isinstance(value, timedelta):
            raise serializers.ValidationError("must be a datetime object!")
        return value 
    
    def validate(self, data):

        WorkoutSeshValue = data.get('workout')
        StartTimeVal = data.get('start_time')
        DurationVal = data.get('duration')

        if not isinstance(WorkoutSeshValue, Workout_Plan):
            raise serializers.ValidationError(f"{WorkoutSeshValue} must be a valid Workout Session!")
        
        return data




# {"start time": "2024-12-18 19:00:00",
#         "duration" : "00:30:00"
#   }'