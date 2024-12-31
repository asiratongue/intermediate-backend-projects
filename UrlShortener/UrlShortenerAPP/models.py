from django.db import models
import random
import string

class URL(models.Model):

    url = models.CharField(max_length=100)
    shortCode = models.CharField(max_length=50)
    createdat = models.DateField("User Created At", auto_now_add=True)
    updatedat = models.DateField("User Last Updated At", auto_now=True)
    accesscount = models.IntegerField(blank=True, default=0)

    def __str__(self):
        return self.url

    @classmethod
    def create_url(cls, url):
        # Generate a random short code for the URL
        short_code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        return cls.objects.create(url=url, shortCode=short_code)


# this is like sqlalchemy where your database models are defined and also where you can add class methods also.