from django.db import connection
cursor = connection.cursor()
cursor.execute("DELETE FROM sqlite_sequence WHERE name='Progression_scheduler';")

#Progression_scheduler