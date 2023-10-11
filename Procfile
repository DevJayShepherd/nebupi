release: python manage.py migrate
web: gunicorn config.wsgi
worker: python -m celery -A config worker -l info
celery_beat: python -m celery -A config beat -l info