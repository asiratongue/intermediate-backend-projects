from rest_framework import serializers
from .models import Exercise_Session, Workout_Plan



class ExerciseSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise_Session
        fields = ['user', 'exercise', 'sets', 'repetitions', 'weights']


    def validate(self, data):

        for field in ['sets', 'repetitions', 'weights']:
            value = data.get(field)

            if not isinstance(value, int):
                raise serializers.ValidationError(f"{field} must be a number!")
            
        sets = data.get('sets')
        reps = data.get('repetitions')
        weights = data.get('weights')

        
        constraints = [
            Exercise_Session.UniqueConstraint(
                fields=['exercise','sets', 'reps', 'weights'],
                condition=Exercise_Session.Q(is_active=True),  # Only enforce uniqueness for active sessions
                name='unique_active_session',
                violation_error_message='This exact combination already exists!'
            )
        ]


        if self.instance:
            existing_session = existing_session.exclude(pk=self.instance.pk)

        if existing_session.exists():
            # Provide a helpful error message that explains exactly what's wrong
            raise serializers.ValidationError(
                f"An exercise session with {sets} sets, {reps} reps, and {weights} weights "
                "already exists. Please modify at least one of these values."
            )
            
        return data
    

    def create(self, validated_data):

            instance, created = Exercise_Session.objects.get_or_create(
                user=validated_data['user'],
                exercise=validated_data['exercise'],
                sets=validated_data['sets'],
                repetitions=validated_data['repetitions'],
                weights=validated_data['weights']
            )
            return instance
