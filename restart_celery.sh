#pkill -9 celery

celery --app=telegram_to_discord worker -l warning --logfile=celery.log --max-tasks-per-child=1 --concurrency=1 --without-heartbeat -Q telegram -n telegram &
celery --app=telegram_to_discord worker -l warning --logfile=celery.log --concurrency=1 --without-heartbeat -Q messages -n messages &
celery --app=telegram_to_discord beat -l warning --logfile=celery_beat.log &

celery -A telegram_to_discord flower --address=localhost --port=5555 --url_prefix=flower &