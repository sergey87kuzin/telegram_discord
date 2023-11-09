#pkill -9 celery

celery --app=telegram_to_discord worker -l info --logfile=celery.log -Q telegram -n telegram &
celery --app=telegram_to_discord beat -l info --logfile=celery_beat.log &

celery -A telegram_to_discord flower --address=localhost --port=5555 --url_prefix=flower &