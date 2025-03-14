from django.core.management.base import BaseCommand
from Asims_Leaderboard.tasks import populate_redis_scores

class Command(BaseCommand):
    help = 'Populates Redis sorted sets with scores from PostgreSQL'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting Redis population...')
        populate_redis_scores()
        self.stdout.write(self.style.SUCCESS('Successfully populated Redis'))

