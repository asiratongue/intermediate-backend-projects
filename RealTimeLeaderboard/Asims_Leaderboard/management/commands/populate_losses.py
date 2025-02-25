from django.core.management.base import BaseCommand
from Asims_Leaderboard.tasks import populate_losses

class Command(BaseCommand):
    help = 'Populates Redis sorted sets for losses with scores from PostgreSQL'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting Redis population...')
        populate_losses()
        self.stdout.write(self.style.SUCCESS('Successfully populated Redis'))