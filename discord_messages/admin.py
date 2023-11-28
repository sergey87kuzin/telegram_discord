from django.contrib import admin

from discord_messages.models import Message, ConfirmMessage, DiscordAccount, DiscordConnection


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    search_fields = ("text", "eng_text", "user_telegram")
    list_filter = ("user_telegram", "answer_type")
    list_display = (
        "text",
        "eng_text",
        "user_telegram",
        "telegram_id",
        "discord_message_id",
        "images",
        "buttons",
        "answer_type",
        "answer_sent",
        "seed",
        "job",
        "seed_send"
    )


@admin.register(ConfirmMessage)
class ConfirmMessageAdmin(admin.ModelAdmin):
    pass


@admin.register(DiscordAccount)
class DiscordAccountAdmin(admin.ModelAdmin):
    pass


@admin.register(DiscordConnection)
class DiscordConnectionAdmin(admin.ModelAdmin):
    pass
