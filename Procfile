release: python manage.py migrate
web: gunicorn config.wsgi
worker: python manage.py celery worker --loglevel=info
celery_beat: python manage.py celery beat --loglevel=info