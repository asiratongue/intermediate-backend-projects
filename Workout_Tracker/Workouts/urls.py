from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = 'WorkoutTracker'

urlpatterns = [
    path('workout/create/', views.CreateWorkout.as_view(), name='create_workout'),
    path('exercises/', views.ListExercises.as_view(), name='list_exercises'),
    path('exercises/<int:id>/', views.GetExercise.as_view(), name='get_exercise'),
    path('workout/remove/<int:id>/', views.RemoveWorkout.as_view(), name='remove_workout'),
    path('workout/update/<int:id>/', views.UpdateWorkout.as_view(), name='update_workout'),
    path('workout/list/', views.ListWorkout.as_view(), name='list_workout'),
    path('exercise/sessions/', views.ListExerciseSessions.as_view(), name='list_exercise_sessions')
]



