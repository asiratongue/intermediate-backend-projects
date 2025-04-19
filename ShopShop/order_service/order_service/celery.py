from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'order_service.settings')

app = Celery('order_service', broker='redis://redis:6379')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(['order_service_app'])

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

    