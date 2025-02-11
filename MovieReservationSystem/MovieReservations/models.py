from django.db import models
from datetime import datetime
from django.core.exceptions import ValidationError
from .storage import MediaStorage
from django.core.validators import MaxValueValidator
import pytz , uuid
from django.db.models import Sum, F, Count
from simple_history.models import HistoricalRecords


def future_date_validator(value):
    naive_datetime = datetime.now()
    timezone = pytz.timezone('UTC')
    aware_datetime = timezone.localize(naive_datetime)

    if value < aware_datetime:
        raise ValidationError("Date must be in the future")

class Genre(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Movie(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=500, null=True)
    poster = models.ImageField(upload_to="Posters/", storage=MediaStorage())
    genre = models.ManyToManyField(Genre)
    date_released = models.IntegerField(null=True)

    def __str__(self):
        return self.title
    
class StdSeatingPlan(models.Model):
    SeatClass = [('luxury class', 'Luxury Class'),
            ('midwit class', 'Midwit Class'),
            ('ghetto class', 'Ghetto Class'),
            ]
    seat = models.CharField(max_length=50, null=True)
    seat_type = models.CharField(choices=SeatClass, max_length=50, default = 'midwit class', null=True)

    @property
    def capacity(self):
       allseats = self.objects.all()
       return len(allseats)

    def price(self):
        prices = {
            'luxury class' : '25.99',
            'midwit class' : '19.99',
            'ghetto class' : '14.99',
        }
        return prices.get(self.seat_type, '0.00') 
    
        
    def status_description(self):
        descriptions = {
            'luxury class' : 'comes with a foot jaccuzi, bottomless beer, and your very own personal masseuse!',
            'midwit class' : 'comes with a plastic reclining chair, a scores of ammy, and an electronic seat massager',
            'ghetto class' : 'comes with a plastic knife and fork, 3 wings and chips, and a vivastreet ting'
        }
        return descriptions.get(self.seat_type, 'unknown')


class MovieScreening(models.Model):
    id = models.AutoField(primary_key=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    showtime = models.DateTimeField(validators=[future_date_validator])   
    seats_left = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)])
    valid = models.BooleanField(default=True)

    @property
    def formatted_showtime(self):
         return self.showtime.strftime("%B %d, %Y at %I:%M %p")
    
    def __str__(self): 
        return self.movie.title
    
class Seats(models.Model):
    seat_loc = models.ForeignKey(StdSeatingPlan, null=True, on_delete=models.CASCADE)
    available = models.BooleanField(default=True)
    movie_screening = models.ForeignKey(MovieScreening, null=True, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['seat_loc', 'movie_screening']
        
from Users.models import CustomUser
class Transaction(models.Model):
        
    STATUS = [
        ('approved', 'Approved'),
        ('declined', 'Declined'),
        ('refunded', 'Refunded'),
        ('partial_refund','Partial Refund')
    ]
        
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, default=1)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    transaction_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(choices=STATUS, default='Refunded', max_length=20)
    history = HistoricalRecords()


class Ticket(models.Model):

    STATUS = [
        ('valid', 'Valid'),
        ('declined', 'Declined'),
        ('expired', 'Expired')
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, default=1)
    seat = models.ForeignKey(Seats, null=True, on_delete=models.CASCADE)
    unique_code = models.UUIDField(default=uuid.uuid4, editable=False)
    movie_screening = models.ForeignKey(MovieScreening, on_delete=models.CASCADE)
    price = models.CharField(null=True, max_length = 90)
    status = models.CharField(choices=STATUS, default='Valid', max_length=30)
    Txnid = models.ForeignKey(Transaction, on_delete=models.CASCADE, null=True) 

    @property
    def formatted_movie_screening(self):
        return self.movie_screening.movie.title

    @property
    def formatted_cost(self):
        return f"{float(self.price):.2f}"
    
    @property
    def formatted_seat_info(self):
        return self.seat.seat_loc.seat
    
    def create_tickets(self, user, cost, quantity, movie_screening, txn):
        tickets = [Ticket(cost=cost, movie_screening=movie_screening, user=user, Txnid = txn) for _ in range(quantity)]  #add seats aswell
        return Ticket.objects.bulk_create(tickets)
    
    def count_tickets(self, user, movie_screening):
        query = Ticket.objects.filter(user = user, movie_screening = movie_screening, status = 'Valid')
        return len(query)
    

    

    

class Revenue(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.DateField(null=True)

    def __str__(self):
        return self.title

    @property
    def formatted_revenue(self):
        return f"{float(self.amount):.2f}"


    @property
    def formatted_month(self):
        day, month, year = self.month.day, self.month.month, self.month.year
        return f"{day}/{month}/{year}"