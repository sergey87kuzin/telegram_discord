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
        "task": "discord_messages.tasks.tasks.delete_old_messages",
        "schedule": crontab(minute="0", hour="0"),
        "options": {"queue": "telegram"},
    },
    "send_stable_to_telegram_1": {
        "task": "stable_messages.tasks.tasks.send_stable_messages_to_telegram_1",
        "schedule": timedelta(seconds=63),
        "options": {"queue": "telegram"},
    },
    "send_stable_to_telegram_2": {
        "task": "stable_messages.tasks.tasks.send_stable_messages_to_telegram_2",
        "schedule": timedelta(seconds=60),
        "options": {"queue": "messages"},
    },
    "send_stable_to_telegram_3": {
        "task": "stable_messages.tasks.tasks.send_stable_messages_to_telegram_3",
        "schedule": timedelta(seconds=61),
        "options": {"queue": "messages1"},
    },
    "send_stable_to_telegram_4": {
        "task": "stable_messages.tasks.tasks.send_stable_messages_to_telegram_4",
        "schedule": timedelta(seconds=62),
        "options": {"queue": "messages3"},
    },
    "check_not_sent_messages": {
        "task": "stable_messages.tasks.tasks.check_not_sent_messages",
        "schedule": timedelta(minutes=10),
        "options": {"queue": "telegram"},
    },
    "resend_messages": {
        "task": "stable_messages.tasks.tasks.resend_messages",
        "schedule": timedelta(minutes=65),
        "options": {"queue": "telegram1"},
    },
    "fetch_videos": {
        "task": "stable_messages.tasks.fireworks_api.fetch_video",
        "schedule": timedelta(minutes=5),
        "options": {"queue": "telegram2"},
    },
    "clear_space": {
        "task": "stable_messages.tasks.fireworks_api.clear_space",
        "schedule": crontab(minute="5", hour="23"),
        "options": {"queue": "telegram2"},
    }
    # "send_discord_answers": {
    #     "task": "discord_messages.tasks.send_messages_to_telegram",
    #     "schedule": timedelta(seconds=31),
    #     "options": {"queue": "telegram"},
    # },
}
