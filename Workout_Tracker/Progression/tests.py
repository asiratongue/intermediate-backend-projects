from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from django.utils import timezone
from rest_framework.test import APIClient
from Workouts.models import Workout_Plan, Exercise_Session, Exercise, Muscle_Group
from Progression.models import Scheduler
from django.contrib.auth import get_user_model
from unittest.mock import patch, ANY
from .serializers import SchedulerObjSerializer
#python manage.py test Progression

class SchedulerTests(TestCase):

    def setUp(self):
        
        self.client = APIClient()
        Arms = Muscle_Group.objects.create(name = "Arms", date_created = datetime.now(), date_updated = datetime.now())
        Chest = Muscle_Group.objects.create(name = "Chest", date_created = datetime.now(), date_updated = datetime.now())
        self.user = get_user_model().objects.create_user(username='testuser', password='testpass')
        self.user2 = get_user_model().objects.create_user(username='userwithnodata', password='testpass')

        self.exercise = Exercise.Create_Exercise(MuscleGroup = [Arms, Chest])
        self.exercise_session = Exercise_Session.create_Exercise_Session(user = self.user, exercise=self.exercise)
        self.workout_plan = Workout_Plan.objects.create(user = self.user, name = "Ippos Workout", comments = "Takamura san")
        self.workout_plan.Exercise_Session.add(self.exercise_session)
        StartTime = datetime.strptime("2024-12-31 09:40:40", "%Y-%m-%d %H:%M:%S")
        Duration =  timedelta(minutes=int(30))
        self.Scheduler = Scheduler.objects.create(user = self.user, workout = self.workout_plan, start_time = StartTime, duration = Duration, status = "PENDING")
        login = self.client.post('/WorkoutTracker/login/', {'username': 'testuser', 'password': 'testpass'}, format='json')
        login2 = self.client.post('/WorkoutTracker/login/', {'username': 'userwithnodata', 'password': 'testpass'}, format='json')
        self.token = login.data['tokens']['access'] 
        self.token2 = login2.data['tokens']['access']



    def test_scheduler_invalid_key(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post("WorkoutTracker/schedule/3342",{"start_time": "2024-12-31 09:40:40", "duration": "00:30:00"}, format='json')
        self.assertEqual(response.status_code, 404)

    def test_schedule_with_wrong_users_workout_session(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token2)
        response = self.client.post("WorkoutTracker/schedule/1/",{"start_time": "2024-12-31 09:40:40", "duration": "00:30:00"}, format='json')
        self.assertEqual(response.status_code, 404)

          
    def test_schedule_with_bad_data(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post("WorkoutTracker/schedule/1",{"start_time": "202asf5-01-31 0erro9:40:40", "duration": "00r:30:00"}, format='json')
        self.assertEqual(response.status_code, 404) 

    @patch('Progression.views.check_workout_started.apply_async')
    @patch('Progression.views.check_workout_completed.apply_async')
    def test_schedule_workout_future_time(self, mock_completed, mock_started):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        future_time = timezone.now() + timedelta(hours=1)
        completion_time = future_time + timedelta(minutes=30)
        response = self.client.post("/WorkoutTracker/schedule/1/", {'start_time': future_time,'duration': timedelta(minutes=30)}, format='json')

        print("Response data:", response.data)  
        self.assertEqual(response.status_code, 201)

        mock_started.assert_called_once()
        mock_completed.assert_called_once()
        
        started_kwargs = mock_started.call_args[1]
        self.assertEqual(started_kwargs['eta'], future_time)
        
        completed_kwargs = mock_completed.call_args[1]
        self.assertEqual(completed_kwargs['eta'], completion_time)

    @patch('Progression.views.check_workout_started.apply_async')
    @patch('Progression.views.check_workout_completed.apply_async')
    def test_schedule_workout_past_time(self, mock_completed, mock_started):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        past_time = timezone.now() - timedelta(hours=1)  
        response = self.client.post('/WorkoutTracker/schedule/1/', {'start_time': past_time, 'duration': timedelta(minutes=30)}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_delete_nonexistent_schedule(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post("WorkoutTracker/schedule/remove/351/")
        self.assertEqual(response.status_code, 404) 

    def test_update_scheduler_bad_key(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)         
        response = self.client.post("WorkoutTracker/schedule/update/6451/", {"scheduled_workout": {"start_time": "2024-12-30 09:40:00", "duration": "35", "workout_id": "4"}}, format='json')
        self.assertEqual(response.status_code, 404)

    def test_update_scheduler_bad_data(self): #
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)         
        response = self.client.post("WorkoutTracker/schedule/update/6451/", {"scheduled_workout": {"start_time": "2024-12-30 09:40:00", "duration": "35", "workout_id": "4"}}, format='json')
        self.assertEqual(response.status_code, 404)

    def test_report_view_no_data(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token2)
        response = self.client.get("report/")
        self.assertEqual(response.status_code, 404)

    def test_list_view_bad_data(self): #
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get("/schedule/list/", {"Liast" : "Completed"}, format='json')
        self.assertEqual(response.status_code, 404)


    def test_list_view_no_data(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token2)
        response = self.client.get("/schedule/list/", {"List" : "Completed"}, format='json')
        self.assertEqual(response.status_code, 404)    

    def test_query_view_bad_url(self): #
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get("/WorkoutTracker/schedule/search/?workkrowout=1/")
        self.assertEqual(response.status_code, 400)  


    def test_query_view_bad_data(self): #
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get("/WorkoutTracker/schedule/search/?workout=100/")
        self.assertEqual(response.status_code, 404)

    def test_query_view_no_query(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get("/schedule/search/")
        self.assertEqual(response.status_code, 404)
                


#python manage.py test Progression 
