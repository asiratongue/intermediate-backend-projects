from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from Workouts.models import Workout_Plan, Exercise_Session, Exercise, Muscle_Group
from django.contrib.auth import get_user_model
from datetime import datetime
#python manage.py test Workouts

class WorkoutTests(TestCase):

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

        login = self.client.post('/WorkoutTracker/login/', {'username': 'testuser', 'password': 'testpass'}, format='json')
        login2 = self.client.post('/WorkoutTracker/login/', {'username': 'userwithnodata', 'password': 'testpass'}, format='json')
        self.token = login.data['tokens']['access'] 
        self.token2 = login2.data['tokens']['access']

    def test_Invalid_Workout_Plan_Creation(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post('/WorkoutTracker/workout/create/', {"exercise_seshIIOon": 
                                                                        {"exercise_session_1": {"exercise": "Deadlift","sets": "12","repetitions": "12","weights": "25"},
                                                                         "exercise_session_5": {"exercise": "Bicep Curl","sets": "4","repetitions": "69","weights": "10"},},
                                                                         "workouwTTt_plan!": {"name": "Real hustlers Workout","comments": "this workout is for hustlers only",
                                                                         "1": "exercise_session_1","2": "exercise_session_5",}}, format='json')
        self.assertEqual(response.status_code, 400)
        
    def test_Invalid_Workout_Plan_Creation2(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post('/WorkoutTracker/workout/create/', {"exercise_session": 
                                                                        {"exercise_session_1": {"exerasfcise": "Deadlift","sets": "12","repetitions": "12","weights": "25"},
                                                                         "exercise_session_5": {"exercfgise": "Bicep Curl","sets": "4","repetitions": "69","weights": "10"},},
                                                                         "workout_plan": {"name": "Real hustlers Workout","comments": "this workout is for hustlers only",
                                                                         "1231": "exerc315ise_session_1","f2": "exercise_sasfession_5",}}, format='json')
        self.assertEqual(response.status_code, 400)

#python manage.py test Workouts
    def test_WrongExerciseKey(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get('/WorkoutTracker/exercises/24234/')
        self.assertEqual(response.status_code, 404)

    def test_NoJWTAccess(self):
        response = self.client.get('/WorkoutTracker/exercises/')
        self.assertEqual(response.status_code, 401)

    def test_badWorkoutKeys(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post('/WorkoutTracker/workout/create/', {"exercise_session":
                                                                        {"exercise_session_1": 100,
                                                                         "exercise_session_5": 200},
                                                                         "workout_plan": {"name": "Real hustlers Workout","comments": "this workout is for hustlers only",
                                                                         "1": "exercise_session_1","2": "exercise_session_5",}}, format='json')   
        self.assertEqual(response.status_code, 404)

    def test_RemoveWorkoutWrongKey(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post('/workout/remove/7786/')
        self.assertEqual(response.status_code, 404)

    def test_list_workout_plan_nodata(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token2)
        response = self.client.post('/workout/list/')
        self.assertEqual(response.status_code, 404)

    def test_update_workout_bad_data(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.patch('workout/update/', {"exercaaase_session": {"exercaaase": "Pull-Up", "seats": "4", "repetations": "15", "weights": "10"}}, format='json' )
        self.assertEqual(response.status_code, 404) 

    def test_update_workout_bad_keys(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.patch('workout/update/', {"workout_plan":{"name":"Ippos Workout","1":"1564"}}, format='json')
        self.assertEqual(response.status_code, 404)


#python manage.py test Workouts