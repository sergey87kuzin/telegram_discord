#pkill -9 celery
source venv/bin/activate
#celery multi start 5 -A telegram_to_discord -c 1 -B:1 -Q:1 telegram -Q:2 messages -Q:3 messages1 -Q:4 messages2 -Q:5 messages3
celery --app=telegram_to_discord beat -l warning --logfile=celery_beat.log &

celery -A telegram_to_discord flower --address=localhost --port=5555 --url_prefix=flower &