from django.apps import AppConfig


class UrlshortenerappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'UrlShortenerAPP'


#this is configuration for your django apps, to be integrated with settings, BigAutoField means theres HELLA keys that can be stored