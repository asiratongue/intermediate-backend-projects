from celery import shared_task
from WorkoutTracker.celery import app
from django.utils import timezone
from .models import Scheduler
import logging, traceback

logger = logging.getLogger(__name__)

@shared_task(name='Progression.tasks.check_workout_started')
def check_workout_started(schedule_id):
    logger.info(f"Starting workout check for schedule_id: {schedule_id}")
    try:
        schedule = Scheduler.objects.get(id=schedule_id)
        logger.info(f"Found schedule object: {schedule}")
        schedule.status = "STARTED"
        schedule.save()
        logger.info(f"Successfully updated status to STARTED for schedule_id: {schedule_id}")
        return f"Successfully started workout {schedule_id}"
    except Exception as e:
        logger.error(f"Error in check_workout_started: {str(e)}")
        raise
    

@shared_task
def check_workout_completed(schedule_id):
    logger.info(f"Completing workout check for schedule_id: {schedule_id}")
    try:
        schedule = Scheduler.objects.get(id=schedule_id)
        logger.info(f"Found schedule object: {schedule}")
        schedule.status = "COMPLETED"
        schedule.save()
        logger.info(f"Successfully updated status to COMPLETED for schedule_id: {schedule_id}")
        return f"Successfully completed workout {schedule_id}"
    except Exception as e:
        logger.error(f"Error in check_workout_completed: {str(e)}")
        raise

