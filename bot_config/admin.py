from django.contrib import admin
from solo.admin import SingletonModelAdmin

from bot_config.models import SiteSettings, Notice
from discord_messages.telegram_helper import bot
from users.models import User


@admin.register(SiteSettings)
class SiteSettingsAdmin(SingletonModelAdmin):
    pass


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    search_fields = ("text",)
    list_display = ("text",)
    actions = ["send_all"]

    def send_all(self, request, queryset):
        users = User.objects.all()
        for notice in queryset:
            for user in users:
                if user.chat_id:
                    try:
                        bot.send_message(
                            chat_id=user.chat_id,
                            text=notice.text
                        )
                    except Exception:
                        pass

    send_all.short_description = "Отправить всем"
