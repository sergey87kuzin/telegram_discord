from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    "check_discord_answers": {
        "task": "discord_messages.tasks.get_discord_messages",
        "schedule": crontab(minute="*/1"),
        "options": {"queue": "messages"},
    },
}
