from django.core.management.base import BaseCommand
from django.db import connection
from MovieReservations.models import StdSeatingPlan



class Command(BaseCommand):
    help = 'seeds the stdseatingplan with seat types'

    def handle(self, *args, **kwargs):

        SeatClass = ['luxury class','midwit class','ghetto class']


        try:
            all_seats = StdSeatingPlan.objects.all().order_by('id')
            for seat in all_seats:
                seat.seat_type = SeatClass[0]
                
                if seat.id >= 31 and seat.id <= 60:
                    seat.seat_type = SeatClass[1]

                if seat.id >= 61:
                    seat.seat_type = SeatClass[2]

                seat.save()

            self.stdout.write(self.style.SUCCESS("data seeded successfully!"))                  

        except Exception as e:            
            self.stdout.write(
                self.style.ERROR(f'Error: {str(e)}'))