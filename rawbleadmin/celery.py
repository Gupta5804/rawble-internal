from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rawbleadmin.settings')
app = Celery('rawbleadmin')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
os.environ['REDIS_URL'] = 'redis://user:5PI0wWA9cHB6t51drhNVHurHdg0UYSxQ@redis-15522.c90.us-east-1-3.ec2.cloud.redislabs.com:15522'
app.config_from_object('django.conf:settings',namespace='CELERY')
app.conf.update(BROKER_URL=os.environ['REDIS_URL'],
                CELERY_RESULT_BACKEND=os.environ['REDIS_URL'])

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))