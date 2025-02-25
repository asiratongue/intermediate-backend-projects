from django.core.management.base import BaseCommand
from django.db import connection



class Command(BaseCommand):
    help = 'seeds the stdseatingplan with algebraic notation'

    def handle(self, *args, **kwargs):
        ChrList = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        NumList = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
        AlgebraList = []

        for Chr in ChrList:
            for Num in NumList:
                AlgChr = str(Chr) + str(Num)
                AlgebraList.append(AlgChr)

        try:
            with connection.cursor() as cursor:
                for algchr in AlgebraList:
                    cursor.execute(f"""
                                INSERT INTO "MovieReservations_stdseatingplan" (seat)
                                VALUES ('{algchr}');                         
                                """)
                self.stdout.write(self.style.SUCCESS("data seeded successfully!"))                  

        except Exception as e:            
            self.stdout.write(
                self.style.ERROR(f'Error: {str(e)}'))
            
