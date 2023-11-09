from datetime import timedelta

from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    "check_discord_answers": {
        "task": "discord_messages.tasks.get_discord_messages",
        "schedule": timedelta(seconds=29),
        "options": {"queue": "telegram"},
    },
    "send_discord_answers": {
        "task": "discord_messages.tasks.send_messages_to_telegram",
        "schedule": timedelta(seconds=31),
        "options": {"queue": "telegram"},
    },
}
