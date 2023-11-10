service nginx restart

# // Миграции и статика
cd /code/
python /code/manage.py migrate
python /code/manage.py collectstatic --no-input

celery --app=telegram_to_discord worker -l info --logfile=celery.log -Q telegram -n telegram &
celery --app=telegram_to_discord beat -l info --logfile=celery_beat.log &

celery -A telegram_to_discord flower --address=web --port=5555 --url_prefix=flower &

gunicorn telegram_to_discord.wsgi:application --bind 0.0.0.0:8000