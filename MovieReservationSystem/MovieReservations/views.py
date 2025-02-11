from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from MovieReservations.models import Movie, MovieScreening, Transaction, Ticket, Revenue, StdSeatingPlan, Seats
from Users.models import CustomUser
from rest_framework import status, permissions
from django.db.models import F, Sum, Count
from django.core.exceptions import ObjectDoesNotExist
from datetime import date
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone
from django.db.models import Sum

class IsAdminToken(permissions.BasePermission):

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)

class ViewAllMovies(APIView):

    permission_classes = [IsAuthenticated]
    model = Movie
    throttle_classes = [UserRateThrottle]

    def get(self, request): 
         try:
            AllMovies = Movie.objects.all()
            return Response({"message" : "here are all movies currently available at PCC!", "Movies" : 
                             f"""{[["ID:", movie.id, "Description:", movie.description, "Poster:", movie.poster.url, "genre:", 
                                  [genre.name for genre in movie.genre.all()], "title:", movie.title]for movie in AllMovies ]}""" })
         
         except Movie.DoesNotExist:
             return Response({"Error": "there are no movies currently available"}, status=status.HTTP_404_NOT_FOUND)
       
class ViewMovies(APIView):

    permission_classes = [IsAuthenticated]
    model = Movie
    throttle_classes = [UserRateThrottle]

    def get(self, request, id):
        try:
            genrelist = []
            SelectedMovie = Movie.objects.get(pk = id)
            for genre in SelectedMovie.genre.all():
                genrelist.append(genre.name)

            return Response({"Title" : f"{SelectedMovie.title}",
                             "Description" : f"{SelectedMovie.description}", 
                            "Poster" : f"{SelectedMovie.poster.url}",
                            "Genre" : f"{genrelist}"}, status=status.HTTP_200_OK)
        
        except Movie.DoesNotExist:
              return Response({"Error": "there are no movies currently available"}, status=status.HTTP_400_BAD_REQUEST)           


class ViewScreenings(APIView):

    permission_classes = [IsAuthenticated]
    model = Movie
    throttle_classes = [UserRateThrottle]

    def get(self, request):
        try:
            date_q = request.GET.get('date', 0)
            movie_q = request.GET.get('movie', 0)
            query_result = MovieScreening.objects.all()
            seats = len(StdSeatingPlan.objects.all())

            if date_q != 0:
                query_result = query_result.filter(showtime__gte=date_q)
            
            if isinstance(movie_q, str):
                query_result = query_result.filter(movie__title__icontains=movie_q)

            return Response ({"message" : f"here are your search results",
                            "Screenings" : f"{[["ID:" + screening.id + "showtime:" + screening.formatted_showtime, "Seats left:" + screening.seats_left, 
                            "movie name:", screening.movie.title]for screening in query_result ]}" }, status=status.HTTP_200_OK)
          
        except MovieScreening.DoesNotExist:
            return Response ({"error" : "could not find any movie screening objects"}, status=status.HTTP_404_NOT_FOUND)


class ViewSeatsAvailable(APIView):

    permission_classes = [IsAuthenticated]
    model = StdSeatingPlan
    throttle_classes = [UserRateThrottle] 

    def get(self, request, id):

        try:

            All_seats = StdSeatingPlan.objects.all()
            MovieScreeningObj = MovieScreening.objects.get(pk = id)
            booked_seats = Seats.objects.filter(available = False, movie_screening = id)

            all_seat_values = All_seats.values_list('id', flat=True)
            all_booked_seat_values = booked_seats.values_list('seat_loc_id', flat=True)

            availableseat_ids = all_seat_values.difference(all_booked_seat_values)
            availableseats = StdSeatingPlan.objects.filter(id__in = availableseat_ids).order_by('id')

            
            return Response({"message" : f"all the seats available for {MovieScreeningObj.movie.title}", "seats" :
                              f"{[["location:", seats.seat,"type:", seats.seat_type] for seats in availableseats]}"}, status=status.HTTP_200_OK)
        
        except MovieScreening.DoesNotExist:
            return Response({"error" : "a movie screening cant be found with that id!"}, status=status.HTTP_400_BAD_REQUEST)
        



class ReserveMovie(APIView):

    permission_classes = [IsAuthenticated]
    model = Movie
    throttle_classes = [UserRateThrottle]

    def post(self, request, id): 
       try:
        user = request.user
        screen2get = MovieScreening.objects.get(pk=id)
        txn = Transaction.objects.create(status = "Approved", user = user)
        year, month = txn.transaction_date.year, txn.transaction_date.month
        revenue_date = date(year, month, 1)

        if "seats" not in request.data:
            txn.delete()
            return Response({"error" : "you must include the list 'seats' within your request!"}, status=status.HTTP_400_BAD_REQUEST)
        
        if screen2get.showtime <= timezone.now():
            screen2get.valid = False
            screen2get.save()
            txn.delete()
            return Response({"error" : f"this movie screening for {screen2get.movie.title} is finished!"}, status=status.HTTP_400_BAD_REQUEST)

        else:                    
            seats = request.data["seats"]       
            ticket_prices = []

            SeatLocation = []

            for seatx in seats:
                seat = StdSeatingPlan.objects.filter(seat= seatx).first()

                if not seat:
                    txn.delete()
                    return Response({"error": f"Invalid seat: {seatx}"}, status=status.HTTP_400_BAD_REQUEST)
                SeatLocation.append(seat)
            
            for i, seat_seat in enumerate(SeatLocation):
                
                seat_to_check = Seats.objects.filter(movie_screening = screen2get, seat_loc = seat_seat)
                if not seat_to_check.exists():
                    continue
                if seat_to_check[0].available == False:
                    txn.delete()
                    return Response({"message" : f"the space {seat_seat.seat} has already been booked!"}, status=status.HTTP_400_BAD_REQUEST) 
            
            booking_errors = []
            successful_bookings = []

            for i, seat in enumerate(seats):
                try:
                    with transaction.atomic():

                
                        SeatObj, created = Seats.objects.select_for_update().get_or_create(seat_loc = SeatLocation[i], movie_screening = screen2get, defaults={"available": True})


                        if SeatObj.available == False:
                            raise ValueError(f"Seat {SeatLocation[i]} already booked")
                        
                        SeatObj.available = False
                        SeatObj.save()

                        price = SeatLocation[i].price()
                        ticket_prices.append(float(price))
                        ticket = Ticket.objects.create(user = user, movie_screening=screen2get, seat = SeatObj, Txnid=txn, price = price)
                        successful_bookings.append((SeatObj, ticket))

                        from . import schedulers
                        print("scheduling task")
                        schedulers.schedule_expire_tickets(ticket.id)  #check the order . . . 

                except Exception as e:
                    booking_errors.append(f"Seat {SeatLocation[i]}: {str(e)}")
                    continue

            if booking_errors:
                with transaction.atomic():
                    for seat_obj, ticket in successful_bookings:
                        ticket.delete()
                        seat_obj.available = True
                        seat_obj.save()

                return Response({"errors": booking_errors}, status=status.HTTP_400_BAD_REQUEST)




            amount = sum(ticket_prices)
            txn.amount = amount
            txn.save()
            screen2get.seats_left -= len(seats)
            screen2get.save()
                                          

        revenue = Transaction.objects.filter(transaction_date__year=year, transaction_date__month=month).aggregate(total=Sum('amount'))['total']
        Revenue.objects.update_or_create(month = revenue_date, defaults={"amount": f"{revenue}"})

        return Response({"message" : f"you have successfully bought {len(seats)} tickets", 
                         "info" : f"""the screening for {screen2get.movie.title} is on the {screen2get.showtime}, you have spent {txn.amount}!, your movie screening id is {screen2get.id},
your ticket ids are {[tix.id for tix in Ticket.objects.filter(user = user, movie_screening = screen2get, Txnid = txn )]} """},
                           status=status.HTTP_200_OK)  

       except MovieScreening.DoesNotExist:
           return Response({"error" : "could not find any screenings . . ."}, status=status.HTTP_404_NOT_FOUND)



class ViewTickets(APIView):
    permission_classes = [IsAuthenticated]
    model = CustomUser
    throttle_classes = [UserRateThrottle]

    def get(self, request):
        user = request.user

        return Response({f"ticket info for {user.username}" : f"{[["Title", ticket.formatted_movie_screening,
                                              "Cost", ticket.formatted_cost, 
                                              "Transaction id:", ticket.Txnid.id,
                                              "Seat:", ticket.formatted_seat_info] 
                                              for ticket in Ticket.objects.filter(user=user)]}"}, 
                        status=status.HTTP_200_OK)
       
        
class CancelReservation(APIView):
    permission_classes = [IsAuthenticated]
    model = CustomUser
    throttle_classes = [UserRateThrottle]

    def patch(self, request, id):
        user = request.user
        try:
            requested_seats = request.data["cancel"]
            if not requested_seats:
                return Response ({"error" : "you have not specified any seats to cancel!"}, status=status.HTTP_400_BAD_REQUEST)

        except KeyError as e:
            return Response({f"error {e}" : "you have mispelt your header! it must be named 'cancel'"}, status=status.HTTP_400_BAD_REQUEST)
        


        try:
            MovieScreeningObject = MovieScreening.objects.get(pk = id)
            if MovieScreeningObject.showtime <= timezone.now():
                return Response ({"error" : "tickets you cancel must not be expired"}, status=status.HTTP_400_BAD_REQUEST)
            
            Tickets = Ticket.objects.filter(movie_screening = MovieScreeningObject, user = user) 
            print(Tickets)
            first_ticket, Ticket_count = Tickets.first(), Tickets.count()             
            ticket_list = []
            price_dict = {}

            def Make_lists(seat_seat):

                seat_plan_obj = StdSeatingPlan.objects.get(seat = seat_seat)
                seat_obj = Seats.objects.get(movie_screening = MovieScreeningObject, seat_loc = seat_plan_obj.id)
                ticket_x = Ticket.objects.get(seat = seat_obj.id, movie_screening = MovieScreeningObject)
                ticket_list.append(ticket_x)
                seat_obj.available = True
                seat_obj.save()
                price_dict[ticket_x.id] = (ticket_x.Txnid, ticket_x.price)

            if "cancel" not in request.data:
                return Response({"error" : "you must specify which tickets you want to cancel!"}, status=status.HTTP_400_BAD_REQUEST)
            
            if "cancel" in request.data:

                user_owned_seats = [ticket.seat.seat_loc.seat for ticket in Tickets]
                unauthorized_seats = [seat for seat in requested_seats if seat not in user_owned_seats]

                if unauthorized_seats:
                    return Response({"error" : f"you don't own the following tickets: {', '.join(unauthorized_seats)}"}, status=status.HTTP_400_BAD_REQUEST)
                
        except ObjectDoesNotExist as e:
            return Response({f"error": f"{e}"}, status=status.HTTP_404_NOT_FOUND)
     
        try:
            for seat_position in [request.data["cancel"]]:

                for seat in seat_position:
                    Make_lists(seat)

                print(price_dict)
            for ticket_id, price_txn_tuple in price_dict.items():
                print(price_txn_tuple)
                txn = Transaction.objects.get(pk = price_txn_tuple[0].id)
                txn.amount = float(txn.amount) - float(price_txn_tuple[1])

                if txn.amount == 0:                      
                    txn.status = 'Refunded'


                if txn.amount != 0:
                    txn.status = 'Partially_Refunded'  

                txn.save()                            

            for tix in ticket_list:           
                tix.delete()
        
            year, month = first_ticket.Txnid.transaction_date.year, first_ticket.Txnid.transaction_date.month
            revenue_date = date(year, month, 1)
                                        
            TicketQuantity = Ticket.count_tickets(self=self, user=user, movie_screening = MovieScreeningObject)
            revenue = Transaction.objects.filter(transaction_date__year=year, transaction_date__month=month).aggregate(total=Sum('amount'))['total']
            Revenue.objects.update_or_create(month = revenue_date, defaults={"amount": f"{revenue}"})
            MovieScreeningObject.seats_left += len(request.data["cancel"])
            MovieScreeningObject.save()

            return Response({"message" : f"you have cancelled {len(request.data["cancel"])} tickets, you now have {TicketQuantity} tickets left! " }, status=status.HTTP_200_OK)
        
        except ObjectDoesNotExist as e:
            return Response({f"error {e}" : "no tickets were found!"}, status=status.HTTP_404_NOT_FOUND)            

  
class ReportAll(APIView):
    permission_classes = [IsAdminToken]
    model = Ticket
    throttle_classes = [UserRateThrottle]

    def get(self, request):
        try:
            all_revenue = Revenue.objects.all()
            all_tickets = Ticket.objects.all()
            all_moviescreenings = MovieScreening.objects.all()
            tickets_left = MovieScreening.objects.aggregate(total=Sum("seats_left"))['total']
            movie_counts = Ticket.objects.values('movie_screening').annotate(count=Count('movie_screening')) ##READ AGAIN, DO YOU UNDERSTAND?  
            # YOU END UP WITH A TUPLE LIKE ("movie screening" : "9", "count" : "3")

            return Response({"message": "here is a report of your PCC cinema mr boss",
                             "revenue" : f"{[["for the month of: " + revobj.formatted_month, "total revenue: " + revobj.formatted_revenue] for revobj in all_revenue]}",
                             "tickets" : f"""you have sold {all_tickets.count()} tickets in total, {[[tix.user.username, tix.seat.seat_loc.seat, tix.movie_screening.movie.title] for tix in all_tickets]} 
                             there are currently {tickets_left} tickets left """,
                             "screenings" : f"""{[[str(item['count']) + " from movie screening " + str(item['movie_screening'])] for item in movie_counts]} 
                             there are {all_moviescreenings.filter(valid = True).count()} movie screenings currently active """})
        
        except ObjectDoesNotExist as e:
            return Response({"error" : f"{e}"}, status=status.HTTP_404_NOT_FOUND)
        

class ReportMovieScreening(APIView):
    permission_classes = [IsAdminToken]
    model = Ticket
    throttle_classes = [UserRateThrottle] 

    def get(self, request, id):
        try:
            MovieScreeningObj = MovieScreening.objects.get(pk = id)
            all_tix = Ticket.objects.filter(movie_screening = MovieScreeningObj)

            return Response({"message" : f"here is the information for {MovieScreeningObj.movie.title}, of id {MovieScreeningObj.id}", 
                             "tickets" : f"{[[tix.user.username, tix.seat.seat_loc.seat, tix.price, tix.status] for tix in all_tix]}"}, status=status.HTTP_200_OK)

        except MovieScreening.DoesNotExist:
            return Response({"error" : "couldnt find any movie screenings with given id"}, status=status.HTTP_400_BAD_REQUEST)


#python manage.py test MovieReservations.tests.CancelTicketEndpointTests.test_no_tickets --keepdb


#python manage.py test MovieReservations.tests.ReserveEndpointTests.test_VeryCloseToExpiredScreening --keepdb

#python manage.py test MovieReservations.tests.CancelTicketEndpointTests --keepdb