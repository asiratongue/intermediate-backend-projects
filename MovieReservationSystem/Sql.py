from django.db import connection
cursor = connection.cursor()
cursor.execute("DELETE FROM sqlite_sequence WHERE name=' MovieReservations_reservations';")
cursor.execute("DELETE FROM sqlite_sequence WHERE name=' MovieReservations_ticket';")
cursor.execute("DELETE FROM sqlite_sequence WHERE name=' MovieReservations_transaction';")
 
"ImageModel.objects.all().delete()"
