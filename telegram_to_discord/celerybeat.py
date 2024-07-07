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
    # "delete_messages": {
    #     "task": "discord_messages.tasks.tasks.delete_old_messages",
    #     "schedule": crontab(minute="0", hour="0"),
    #     "options": {"queue": "telegram"},
    # },
    "check_not_sent_messages": {
        "task": "stable_messages.tasks.tasks.check_not_sent_messages",
        "schedule": crontab(hour="*/1", minute="0"),
        "options": {"queue": "telegram"},
    },
    # "resend_messages": {
    #     "task": "stable_messages.tasks.tasks.resend_messages",
    #     "schedule": timedelta(minutes=65),
    #     "options": {"queue": "telegram1"},
    # },
    # "fetch_videos": {
    #     "task": "stable_messages.tasks.fireworks_api.fetch_video",
    #     "schedule": timedelta(minutes=5),
    #     "options": {"queue": "telegram2"},
    # },
    "send_messages_to_stable": {
        "task": "stable_messages.tasks.to_stable.send_first_messages_to_stable_workflow",
        "schedule": crontab(minute="*/1"),
        "options": {"queue": "messages"},
    },
    "send_vary_upscale_messages_to_stable": {
        "task": "stable_messages.tasks.to_stable.send_upscale_vary_messages_to_stable_workflow",
        "schedule": crontab(minute="*/1"),
        "options": {"queue": "stable"},
    },
    "send_messages_to_telegram": {
        "task": "stable_messages.tasks.tasks.send_stable_messages_to_telegram_workflow",
        "schedule": crontab(minute="*/1"),
        "options": {"queue": "messages"},
    },
    "send_video_messages_to_stable": {
        "task": "stable_messages.tasks.video_messages.send_video_messages_to_stable",
        "schedule": crontab(minute="*/1"),
        "options": {"queue": "stable"},
    },
    # "fetch_stable_video_messages": {
    #     "task": "stable_messages.tasks.video_messages.fetch_stable_video_messages",
    #     "schedule": crontab(minute="*/1"),
    #     "options": {"queue": "telegram"},
    # },
    "clear_space": {
        "task": "stable_messages.tasks.fireworks_api.clear_space",
        "schedule": crontab(minute="6", hour="23"),
        "options": {"queue": "messages"},
    }
    # "send_discord_answers": {
    #     "task": "discord_messages.tasks.send_messages_to_telegram",
    #     "schedule": timedelta(seconds=31),
    #     "options": {"queue": "telegram"},
    # },
}
