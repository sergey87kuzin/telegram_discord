from django.contrib import admin

from comments.models import CommentMessage


@admin.register(CommentMessage)
class CommentMessageAdmin(admin.ModelAdmin):
    search_fields = ("message_text", "telegram_username")
    list_display = ("telegram_username", "message_text", "answered")
