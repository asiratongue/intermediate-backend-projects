from django.db import connection
cursor = connection.cursor()
cursor.execute("DELETE FROM sqlite_sequence WHERE name=' ImageManagement_imagemodel';")

 
"ImageModel.objects.all().delete()"
