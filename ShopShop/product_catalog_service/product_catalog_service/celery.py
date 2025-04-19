from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'product_catalog_service.settings')

app = Celery('shopping_cart_service', broker='redis://redis:6379')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(['product_catalog_service'])

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')