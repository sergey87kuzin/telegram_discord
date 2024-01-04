from datetime import timedelta

from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    # "check_discord_answers": {
    #     "task": "discord_messages.tasks.get_discord_messages",
    #     "schedule": timedelta(seconds=60),
    #     "options": {"queue": "telegram"},
    # },
    # "send_no_answer": {
    #     "task": "discord_messages.tasks.send_message_no_answer",
    #     "schedule": timedelta(minutes=30),
    #     "options": {"queue": "telegram"},
    # },
    "delete_messages": {
        "task": "discord_messages.tasks.delete_old_messages",
        "schedule": crontab(minute="0", hour="0"),
        "options": {"queue": "telegram"},
    },
    "send_stable_to_telegram": {
        "task": "stable_messages.tasks.send_stable_messages_to_telegram",
        "schedule": timedelta(seconds=63),
        "options": {"queue": "telegram"},
    },
    "check_not_sent_messages": {
        "task": "stable_messages.tasks.check_not_sent_messages",
        "schedule": timedelta(minutes=10),
        "options": {"queue": "telegram"},
    }
    # "send_discord_answers": {
    #     "task": "discord_messages.tasks.send_messages_to_telegram",
    #     "schedule": timedelta(seconds=31),
    #     "options": {"queue": "telegram"},
    # },
}
