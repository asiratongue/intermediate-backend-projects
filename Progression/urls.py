from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = 'WorkoutTracker'

urlpatterns = [
    path('schedule/<int:idx>/', views.ScheduleWorkout.as_view(), name='schedule'),
    path('schedule/', views.ScheduleWorkout.as_view(), name='mark_as_pending'),
    path('schedule/remove/<int:idx>/', views.DeleteScheduledWorkout.as_view(), name ='delete_scheduled_workout'),
    path('schedule/update/<int:idx>/', views.UpdateScheduledWorkout.as_view(), name ='update_scheduled_workout'),
    path('report/', views.Report.as_view(), name='report'),
    path('schedule/search/', views.QueryScheduledWorkouts.as_view(), name = 'report_query'),
    path('schedule/list/', views.ListScheduledWorkouts.as_view(), name = 'List_Scheduled_Workouts'),
]