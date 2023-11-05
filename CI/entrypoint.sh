service nginx restart

# // Миграции и статика
cd /code/
python /code/manage.py migrate
python /code/manage.py collectstatic --no-input

celery --app=telegram_to_discord worker -l info --logfile=/celery.log -Q default -n default &
celery --app=telegram_to_discord beat -l info --logfile=/celery_beat.log &

celery --broker=redis://redis:6379 -A telegram_to_discord flower --address=web --port=5555 --url_prefix=flower &

gunicorn telegram_to_discord.wsgi:application --bind 0.0.0.0:8000