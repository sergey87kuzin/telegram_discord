from django.contrib import admin

from discord_messages.models import Message, ConfirmMessage, DiscordAccount, DiscordConnection


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    pass


@admin.register(ConfirmMessage)
class ConfirmMessageAdmin(admin.ModelAdmin):
    pass


@admin.register(DiscordAccount)
class DiscordAccountAdmin(admin.ModelAdmin):
    pass


@admin.register(DiscordConnection)
class DiscordConnectionAdmin(admin.ModelAdmin):
    pass
