from django.contrib import admin

from support.models import SupportMessage


@admin.register(SupportMessage)
class SupportMessageAdmin(admin.ModelAdmin):
    search_fields = ("message_text", "telegram_username")
    list_display = ("telegram_username", "message_text", "answered")
