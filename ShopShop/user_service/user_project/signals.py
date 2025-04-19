from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .tasks import publish_user_event
from django.contrib.auth import get_user_model

User = get_user_model()
# change for security reasons
@receiver(post_save, sender=User)
def user_created_or_updated(sender, instance, created, **kwargs):
    """
    Signal handler for when a user is created or updated.
    """
    event_type = 'user.created' if created else 'user.updated'
    user_data = {
        'id': str(instance.id),
        'username': instance.username,
        'password' : instance.password,
        'email': instance.email,
        'first_name': instance.first_name,
        'last_name': instance.last_name,
    }

    publish_user_event.delay(event_type, user_data)

@receiver(post_delete, sender=User)
def user_deleted(sender, instance, **kwargs):
    event_type = 'user.deleted'
    user_data = {
        'id': str(instance.id),
        'username': instance.username,
        'password' : instance.password,
        'email': instance.email,
        'first_name': instance.first_name,
        'last_name': instance.last_name,
    }

    publish_user_event.delay(event_type, user_data)