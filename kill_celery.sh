kill -9 $(ps aux | grep celery | grep -v grep | awk '{print $2}' | tr '\n' ' ') > /dev/null 2>&1
celery multi stop 5 -A telegram_to_discord -c 1 -B:1 -Q:1 telegram -Q:2 messages -Q:3 messages1 -Q:4 messages2 -Q:5 messages3
