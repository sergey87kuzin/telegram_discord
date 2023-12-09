#pkill -9 celery

sudo celery multi start 2 -A telegram_to_discord -c 1 -B:2 -Q:1 messages -Q:2 telegram
celery --app=telegram_to_discord beat -l warning --logfile=celery_beat.log &

celery -A telegram_to_discord flower --address=localhost --port=5555 --url_prefix=flower &