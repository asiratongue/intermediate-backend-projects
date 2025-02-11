from django.apps import AppConfig
from datetime import timezone


class MoviereservationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "MovieReservations"


def ready(self):
    
    from . import schedulers
    from MovieReservations.models import MovieScreening
    future_screenings = MovieScreening.objects.filter(
        showtime__gt=timezone.now()
    )
    for screening in future_screenings:
        schedulers.schedule_ticket_expiry(screening.id)