import os
from django.conf import settings
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'user_service.settings')

app = Celery('sync_tasks', broker='redis://redis:6379')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(['user_project'])

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')