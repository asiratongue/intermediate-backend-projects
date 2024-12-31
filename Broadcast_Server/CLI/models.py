from django.db import models


class chat_history(models.Model):

    message = models.CharField(max_length=500)
    sender_id = models.CharField(max_length=250)
    group_name = models.CharField(max_length=250, default=1)
    timestamp = models.DateTimeField("Timestamp: ", auto_now_add=True)
