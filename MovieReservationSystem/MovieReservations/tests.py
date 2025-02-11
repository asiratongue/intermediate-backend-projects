from django.test import TestCase, TransactionTestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from pathlib import Path
from MovieReservations.models import Movie, MovieScreening, Ticket, Seats, Revenue, Transaction, StdSeatingPlan
from django.core.management import call_command
from django.utils import timezone
from datetime import timedelta
import time
import concurrent.futures
from django.db import transaction
from Users.models import CustomUser

class EmptyDatabaseTests(TestCase):
    def setUp(self):

        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username='testuser', password='testpass')
        login = self.client.post('/PrinceCharles/login/', {'username': 'testuser', 'password': 'testpass'}, format='json')
        self.token = login.data['tokens']['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

    def test_viewall_empty_db(self):
        response = self.client.post('PrinceCharles/viewall/')
        self.assertEqual(response.status_code, 404)

    def test_InvalidQueryMS(self):
       response = self.client.post('PrinceCharles/viewscreenings/?date=23234-343-362')
       print(response.content)
       self.assertEqual(response.status_code, 404) 


    def test_report_all_empty_db(self):
       response = self.client.post('PrinceCharles/report/all/')
       self.assertEqual(response.status_code, 404)         

#WORKING

class MovieReservationVieWEndpointTests(TestCase):

    def setUp(self):
        
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username='testuser', password='testpass')
        login = self.client.post('/PrinceCharles/login/', {'username': 'testuser', 'password': 'testpass'}, format='json')
        self.token = login.data['tokens']['access'] 

    def test_viewInvalidMovieScreening(self):
       self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
       response = self.client.post('PrinceCharles/view/231214134/')  
       self.assertEqual(response.status_code, 404)

    def test_InvalidMovieQueryMS(self):
       self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
       response = self.client.post('PrinceCharles/viewscreenings/?movie=Aet39jK;&/')
       print(response.content)
       self.assertEqual(response.status_code, 404)

    def test_InvalidDateQueryMS(self):
       self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
       response = self.client.post('PrinceCharles/viewscreenings/?date=23234-343-362/')
       print(response.content)
       self.assertEqual(response.status_code, 404)        

#WORKING

class ReserveEndpointTests(TransactionTestCase):

    def setUp(self):
        call_command('loaddata', 'test_fixtures.json', verbosity=0)

        self.client1 = APIClient()
        self.client2 = APIClient()

        with transaction.atomic():

            self.user = get_user_model().objects.create_user(username='testuser', password='testpass')
            self.user2 = get_user_model().objects.create_user(username = 'testuser2', password='testpass2')

        login = self.client.post('/PrinceCharles/login/', {'username': 'testuser', 'password': 'testpass'}, format='json')
        login2 = self.client.post('/PrinceCharles/login/', {'username': 'testuser2', 'password': 'testpass2'}, format='json')

        self.token = login.data['tokens']['access']
        self.token2 = login2.data['tokens']['access']

        self.moviee = Movie.objects.all().first()     

    def test_UnauthenticatedUser(self):
        response = self.client1.post('/PrinceCharles/reserve/10/', {"seats": ["C1", "F3", "I4"]}, format='json')
        self.assertEqual(response.status_code, 401) 

    def test_NoSeatParam(self):
        self.client1.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client1.post('/PrinceCharles/reserve/')
        self.assertEqual(response.status_code, 404)

    def test_EmptySeats(self):
        self.client1.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client1.post('/PrinceCharles/reserve/10/', {"seats": []})
        self.assertEqual(response.status_code, 400)

    def test_InvalidSeat(self):
        self.client1.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client1.post('/PrinceCharles/reserve/10/', {"seats": ["C342", "FX3", "Zdg4"]}, format='json')
        self.assertEqual(response.status_code, 400) 

    def test_ExpiredScreenings(self): 
        self.client1.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')     
        response = self.client1.post('/PrinceCharles/reserve/13/', {"seats": ["C1", "F3", "I4"]}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_VeryCloseToExpiredScreening(self):
        self.client1.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        showtime = timezone.now() + timedelta(seconds=1)
        MovieScreening.objects.create(showtime = showtime, movie = self.moviee, seats_left = 100)
        latest_screening = MovieScreening.objects.latest('id')

        for i in range (10):
            time.sleep(1)
            print(f"counting down {10 - i}")

        response = self.client1.post(f'/PrinceCharles/reserve/{latest_screening.id}/', {"seats": ["C1", "F3", "I4"]}, format='json')
        print(response.content)
        self.assertEqual(response.status_code, 400) 

    def test_bookingAlreadyBooked(self):
        self.client1.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client1.post('/PrinceCharles/reserve/6/', {"seats": ["C1", "F3", "I4"]}, format='json')
        time.sleep(3)
        self.client2.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token2}')
        response2 = self.client1.post('/PrinceCharles/reserve/6/', {"seats": ["C1", "F3", "I4"]}, format='json')

        self.assertEqual(response2.status_code, 400)

    def test_ConcurrentRaceBookings(self):

        def make_booking(client, token):

            client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
            response = client.post('/PrinceCharles/reserve/5/', {"seats": ["B2"]}, format='json')
            return response
        
        import threading
        
        responses = []
        
        def thread_task(client, token):
            response = make_booking(client, token)
            responses.append(response)

        t1 = threading.Thread(target=thread_task, args=(self.client1, self.token))
        t2 = threading.Thread(target=thread_task, args=(self.client2, self.token2))

        t1.start()
        t2.start()
        t1.join()
        t2.join()

        success_count = sum(1 for r in responses if r.status_code == 200)
        self.assertEqual(success_count, 1)


    def test_ConcurrentBookings(self):

        def make_booking(client, token, seat):

            client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
            response = client.post('/PrinceCharles/reserve/5/', {"seats": [seat]}, format='json')
            return response

        import threading

        responses = []

        def thread_task(client, token, seat):
            response = make_booking(client, token, seat)
            responses.append(response)

        t1 = threading.Thread(target=thread_task, args=(self.client1, self.token, "B6"))
        t2 = threading.Thread(target=thread_task, args=(self.client2, self.token2, "B7"))

        t1.start()
        t2.start()
        t1.join()
        t2.join()

        self.assertEqual(responses[0].status_code, 200)
        self.assertEqual(responses[0].status_code, 200)


    def test_DataIntegrity(self):
        self.client1.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        price_check = []
        response = self.client1.post('/PrinceCharles/reserve/10/', {"seats": ["C1", "F3", "I4"]}, format='json')
        Txn = Transaction.objects.latest('transaction_date')
        Tickets = Ticket.objects.filter(Txnid = Txn)
        x = False

        for tix in Tickets:
            price_check.append(tix.price)

        if len(price_check) == len(set(price_check)):
            x = True

        Rev = Revenue.objects.latest('month')
        amount = int(Rev.amount)

        self.assertEqual(Txn.status, "Approved")
        self.assertEqual(x, True)
        self.assertGreater(amount, 0)


    def test_seatConsistency(self):
        self.client1.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client1.post('/PrinceCharles/reserve/10/', {"seats": ["C1"]}, format='json')
        self.client2.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token2}')
        response2 = self.client2.post('/PrinceCharles/reserve/10/', {"seats": ["C1"]}, format='json')
        MS = MovieScreening.objects.get(pk = 10)
        SeatsLeft = MS.seats_left 

        self.assertEqual(response2.status_code, 400)
        self.assertEqual(SeatsLeft, 99)

    def test_NonExistentMovieScrnings(self):
        self.client1.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client1.post('/PrinceCharles/reserve/777/', {"seats": ["C1"]}, format='json')

        self.assertEqual(response, 400)

    def test_schedulingFunction(self):
        self.client1.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        from . import schedulers
        seating_plan_obj = StdSeatingPlan.objects.get(pk = 12)
        Expired_tickets = Ticket.objects.create(movie_screening = MovieScreening.objects.get(pk=13), user = self.user, 
                                                seat = Seats.objects.create(seat_loc = seating_plan_obj, movie_screening = MovieScreening.objects.get(pk=13), available = False ))
        
        schedulers.schedule_expire_tickets(Expired_tickets.id)
        time.sleep(5)
        expired_ticket = Ticket.objects.get(pk = Expired_tickets.id)

        self.assertEqual(expired_ticket.status, 'expired')

# WORKING!


class CancelTicketEndpointTests(TransactionTestCase):

    def setUp(self):
        call_command('loaddata', 'test_fixtures.json', verbosity=0)
        self.client = APIClient()
        self.client2 = APIClient()
        self.client_admin = APIClient()

        with transaction.atomic():
            self.user = get_user_model().objects.create_user(username='testuser', password='testpass')
            self.user2 = get_user_model().objects.create_user(username = 'testuser2', password='testpass2')
            self.admin_user = CustomUser.objects.create_superuser(username='admin',email='admin@example.com', password='adminpass123')

        login = self.client.post('/PrinceCharles/login/', {'username': 'testuser', 'password': 'testpass'}, format='json')
        login2 = self.client2.post('/PrinceCharles/login/', {'username': 'testuser2', 'password': 'testpass2'}, format='json')
        admin_login = self.client_admin.post('/PrinceCharles/login/', {'username': 'admin', 'password': 'adminpass123'}, format='json')

        self.token = login.data['tokens']['access']
        self.token2 = login2.data['tokens']['access']
        self.token_admin = admin_login.data['tokens']['access']

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.client2.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token2}')
        self.client_admin.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_admin}')

        seating_plan_obj = StdSeatingPlan.objects.get(pk = 12)
        Ticket.objects.create(movie_screening = MovieScreening.objects.get(pk=13), user = self.user, 
                                                seat = Seats.objects.create(seat_loc = seating_plan_obj, movie_screening = MovieScreening.objects.get(pk=13), available = False ))

    def test_cancel_expired_ticket(self):
        response = self.client.patch('/PrinceCharles/cancel/13/', {"cancel": ["B2"]}, format='json')
        print(response.content)
        self.assertEqual(response.status_code, 400)

    def test_cancel_invalid_seats(self):
        response = self.client.patch('/PrinceCharles/cancel/9/', {"cancel": ["BF22312"]}, format='json')
        print(response.content)
        self.assertEqual(response.status_code, 400)

    def test_cancel_unowned_tickets(self):
        response = self.client.patch('/PrinceCharles/cancel/5/', {"cancel": ["B2"]}, format='json')
        print(response.content)
        self.assertEqual(response.status_code, 400)     

    def test_cancel_misspelt_header(self):
        self.client.post('/PrinceCharles/reserve/5/', {"seats": ["B2"]}, format='json')
        response = self.client.patch('/PrinceCharles/cancel/5/', {"canshelel": ["B2"]}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_cancel_malformed_data(self):
        self.client.post('/PrinceCharles/reserve/5/', {"seats": ["B2"]}, format='json')
        response = self.client.patch('/PrinceCharles/cancel/5/', {"cancel": ["2;23'=-3!B2"]}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_empty_header(self):
        response = self.client.patch('/PrinceCharles/cancel/5/')
        self.assertEqual(response.status_code, 400)            
    
    def test_no_tickets(self):
        response = self.client.patch('/PrinceCharles/cancel/5/', {"cancel": []}, format='json')
        print(response.content)
        self.assertEqual(response.status_code, 400)

    def test_ticket_deletion(self):
        self.client.post('/PrinceCharles/reserve/5/', {"seats": ["B2"]}, format='json')
        movie_screening_obj = MovieScreening.objects.get(pk = 5)
        response = self.client.patch('/PrinceCharles/cancel/5/', {"cancel": ["B2"]}, format='json')        
        ticket = Ticket.objects.latest('id')
        seat = Seats.objects.latest('available')
        x = False

        if ticket.movie_screening == 5:
            x = True

        self.assertEqual(x, False)
        self.assertEqual(seat.available, True)

    def test_report_invalid_screening(self):

        x = CustomUser.objects.filter(is_superuser = True)
        for y in x:
            print(y.username)
            print(y.is_superuser)

        response = self.client_admin.get('/PrinceCharles/report/5342/') 
        self.assertEqual(response.status_code, 400)



#WORKING

