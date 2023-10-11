release: python manage.py migrate
web: gunicorn ready_saas.wsgi
worker: python manage.py celery worker --loglevel=info
celery_beat: python manage.py celery beat --loglevel=info