kill -9 $(ps aux | grep celery | grep -v grep | awk '{print $2}' | tr '\n' ' ') > /dev/null 2>&1
sudo celery multi stop 2 -A telegram_to_discord -c 1 -B:2 -Q:1 messages -Q:2 telegram
