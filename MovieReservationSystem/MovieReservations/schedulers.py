from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
from MovieReservations.models import Ticket, MovieScreening
from datetime import timedelta
import logging 

logger = logging.getLogger(__name__)

def schedule_expire_tickets(id):
    ticket = Ticket.objects.get(pk = id)
    expiry_time = ticket.movie_screening.showtime  + timedelta(seconds=5) 
    
    logger.info(f"Scheduling expiry for ticket {id} at {expiry_time}")

    def expire_tickets_and_screening(id):
        logger.info(f"Running expiry for ticket {id}")
        ticket = Ticket.objects.get(pk = id)
        logger.info(f"About to expire tickets for screening {ticket.movie_screening.id}")
        
        tickets_updated = Ticket.objects.filter(movie_screening=ticket.movie_screening, status='Valid').update(status='expired')
        screening_updated = MovieScreening.objects.filter(pk=ticket.movie_screening.id).update(valid=False)
        
        logger.info(f"Expired {tickets_updated} tickets and updated screening status")

    scheduler = BackgroundScheduler()
    scheduler.start()

    if expiry_time < timezone.now():
        scheduler.add_job(
            expire_tickets_and_screening,
            'date',
            run_date=timezone.now(),
            misfire_grace_time=None,
             args=[id],
            id=f'screening_{id}'
        )

    else:
        scheduler.add_job(
            expire_tickets_and_screening,
            'date', 
            run_date=expiry_time,
            misfire_grace_time=None,
            args=[id],
            id=f'screening_{id}'
        )
    


    if not scheduler.running:
        logger.info("Starting scheduler")
        scheduler.start()
    else:
        logger.info("Scheduler already running")
    

