from django.test import TestCase, TransactionTestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from .utils import duplicate_redis_data_for_testing
from django_redis import get_redis_connection
from django.core.management import call_command


#python manage.py test Asims_Leaderboard.tests.EmptyDatabaseTests.test_view_global_report_emptydb
#python manage.py test Asims_Leaderboard.tests.EndpointTests

class EmptyDatabaseTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        duplicate_redis_data_for_testing()


    def setUp(self):
        
        super().setUp()
        self.redis_conn = get_redis_connection('default')
        self.client = APIClient()

        self.user = get_user_model().objects.create_user(username='testuser', password='testpass')
        login = self.client.post('/AsimsLeaderboard/login/', {'username': 'testuser', 'password': 'testpass'}, format='json')

        self.token = login.data['tokens']['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
      
    def test_view_games_emptydb(self):
        response = self.client.get('/AsimsLeaderboard/viewgames/')
        self.assertEqual(response.status_code, 404)

    def test_view_global_score_emptydb(self):
        response = self.client.get('/AsimsLeaderboard/view/global/score/')
        self.assertEqual(response.status_code, 404)

    def test_view_global_report_emptydb(self):
       response = self.client.get('/AsimsLeaderboard/report/all/?datefrom=2025-02-01&dateto=2025-02-25') 
       self.assertEqual(response.status_code, 404)
      

class EndpointTests(TransactionTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        duplicate_redis_data_for_testing()


    def setUp(self):
        
        call_command('loaddata', 'Game.json', 'users.json', 'UserGameProfile.json', verbosity=0)
        super().setUp()
        self.redis_conn = get_redis_connection('default')

        self.client = APIClient()
        self.client2 = APIClient()

        self.user = get_user_model().objects.create_user(username='testuser', password='testpass')
        self.user2 = get_user_model().objects.create_user(username='testuser2', password='testpass')

        login = self.client.post('/AsimsLeaderboard/login/', {'username': 'testuser', 'password': 'testpass'}, format='json')
        login2 = self.client2.post('/AsimsLeaderboard/login/', {'username': 'testuser2', 'password': 'testpass'}, format='json')

        self.token = login.data['tokens']['access']
        self.token2 = login2.data['tokens']['access']

        
    def test_viewgames_invalid_jwt(self):
        response = self.client.get('/AsimsLeaderboard/viewgames/')
        self.assertEqual(response.status_code, 401)

    def test_submit_nonexistent_game(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post('/AsimsLeaderboard/submit/23124315/', {"score": {"wins" : 13, "losses" : 5}}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_submit_incorrect_data(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

        response = self.client.post('/AsimsLeaderboard/submit/5/', {"scworeyauhs": {"wins" : 13, "losses" : 5}}, format='json')
        response2 = self.client.post('/AsimsLeaderboard/submit/5/', {"score": {"wsdas" : 13, "losgs" : 5}}, format='json')
        response3 = self.client.post('/AsimsLeaderboard/submit/5/', {"score": {"wins" : "098jf0", "losses" : "fifty"}}, format='json')
        response4 = self.client.post('/AsimsLeaderboard/submit/5/', {"score": {"wins" : 12113, "losses" : 3151}}, format='json')
        response5 = self.client.post('/AsimsLeaderboard/submit/5/', {"score": {"wins" : -23, "losses" : -1}}, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response2.status_code, 400)
        self.assertEqual(response3.status_code, 400)
        self.assertEqual(response4.status_code, 400)
        self.assertEqual(response5.status_code, 400)

    def test_basic_submit(self):
        # Test user 1
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response1 = self.client.post('/AsimsLeaderboard/submit/5/', {"score": {"wins": 15, "losses": 5}}, format='json')
        print(f"User 1 response: {response1.status_code}, {response1.content}")
        
        # Test user 2
        self.client2.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token2}')
        response2 = self.client2.post('/AsimsLeaderboard/submit/5/', {"score": {"wins": 15, "losses": 5}}, format='json')
        print(f"User 2 response: {response2.status_code}, {response2.content}")
        
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)

    def test_submit_with_futures(self):
        import concurrent.futures
        
        def submit_score(token):
            client = APIClient()
            client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
            return client.post('/AsimsLeaderboard/submit/5/', 
                            {"score": {"wins": 15, "losses": 5}}, 
                            format='json')
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future1 = executor.submit(submit_score, self.token)
            future2 = executor.submit(submit_score, self.token2)
            
            response1 = future1.result()
            response2 = future2.result()
        
        print(f"Response 1: {response1.status_code}, {response1.content}")
        print(f"Response 2: {response2.status_code}, {response2.content}")
        
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)

    def test_global_score_no_games(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get('/AsimsLeaderboard/view/global/score/')
        print(response.content)
        self.assertEqual(response.status_code, 400)

    def test_global_score_good_request(self):
        login = self.client.post('/AsimsLeaderboard/login/', {'username': 'Killua', 'password': 'securepassword'}, format='json')
        self.token_killua = login.data['tokens']['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token_killua)
        print(login.data)
        response = self.client.get('/AsimsLeaderboard/view/global/score/')
        print(response.content)
        self.assertEqual(response.status_code, 200) 


    def test_selectedrank_nonexistent(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get('/AsimsLeaderboard/view/game/75/score/')
        print(response.content)       
        self.assertEqual(response.status_code, 404)

    def test_selectedrank_no_scores(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get('/AsimsLeaderboard/view/game/3/score/')
        print(response.content)
        self.assertEqual(response.status_code, 400)        

    def test_selectedrank_malformed_url(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get('/AsimsLeaderboard/view/gayme/3/swcowdsre/')
        print(response.content)
        self.assertEqual(response.status_code, 404)

    def test_reportall_invalid_dates(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get('/AsimsLeaderboard/view/report/all/?datefrom=20225-0231-041&dateto=20245--061-250')

        response_string = self.client.get('/AsimsLeaderboard/view/report/all/?datefrom=twennytwennyfive-01-31&dateto=hello-ok-hahaha')

        self.assertEqual(response.status_code, 400)  
        self.assertEqual(response_string.status_code, 400)

    def test_reportall_bad_dates(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get('/AsimsLeaderboard/view/report/all/?datefrom=2899-02-12&dateto=2999-06-25')
        response2 = self.client.get('/AsimsLeaderboard/view/report/all/?datefrom=1776-02-12&dateto=1865-06-25')

        print(response.content, response2.content)

        self.assertEqual(response.status_code, 400)  
        self.assertEqual(response2.status_code, 400)

    def test_reportall_no_query(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get('/AsimsLeaderboard/view/report/all/')
        self.assertEqual(response.status_code, 400)

    def test_reportall_misspelt_query(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get('/AsimsLeaderboard/view/report/all/?datefroym=2025-02-12&dtataeeto=2025-06-25')
        self.assertEqual(response.status_code, 400)


    def test_reportgame_nonexistent(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get('/AsimsLeaderboard/view/report/29/?datefrom=2025-02-12&dateto=2025-06-25')
        print(response.content)       
        self.assertEqual(response.status_code, 404)

    def test_reportgame_noscores(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get('/AsimsLeaderboard/view/report/4/?datefrom=2025-03-12&dateto=2025-06-25')
        print(response.content)       
        self.assertEqual(response.status_code, 400)       

        




#python manage.py test Asims_Leaderboard.tests.EndpointTests.test_submit_with_futures --keepdb