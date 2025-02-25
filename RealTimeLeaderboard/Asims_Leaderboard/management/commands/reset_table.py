from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Resets a specified table and its sequence'

    def add_arguments(self, parser):
        parser.add_argument(
            'table_name',
            type=str,
            help='Name of the table to reset'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force reset without confirmation',
        )

    def handle(self, *args, **kwargs):
        table_name = kwargs['table_name']
        
        if not kwargs['force']:
            confirm = input(f'This will delete all data in {table_name}. Are you sure? [y/N]: ')
            
            if confirm.lower() != 'y':
                self.stdout.write(self.style.WARNING('Operation cancelled'))
                return
            
        if table_name == "MovieReservations_transaction":
            try:
                with connection.cursor() as cursor:
                    cursor.execute('TRUNCATE TABLE "MovieReservations_transaction", "MovieReservations_ticket" RESTART IDENTITY CASCADE;')

                self.stdout.write(
                    self.style.SUCCESS(f'Successfully reset {table_name} table and sequence'))
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error: {str(e)}'))                

        else:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(f'TRUNCATE TABLE "{table_name}" RESTART IDENTITY;')
                    
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully reset {table_name} table and sequence')
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error: {str(e)}'))