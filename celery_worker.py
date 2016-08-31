#!usr/bin/env python
import os
from app import celery, create_app
'''
The only remaining task is to launch a Celery worker.
This process needs to have its own Flask application instance that can be used to create the
context necessary for the Flask background tasks to run. For this I used a separate starter script,
which I called celery_worker.py:

This little script creates a Flask application and pushes an application context,
which will remain set through the entire life of the process.
Celery also needs access to the celery instance, so I imported it from the app package.

you need cmd 'celery worker -A celery_worker.celery --loglevel=info' run it
'''
app = create_app(os.getenv('FLASK_CONFIG') or 'default')
app.app_context().push()
