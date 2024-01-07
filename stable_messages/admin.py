from django.contrib import admin
from solo.admin import SingletonModelAdmin

from stable_messages.models import StableMessage, StableAccount, StableSettings


@admin.register(StableMessage)
class StableMessageAdmin(admin.ModelAdmin):
    search_fields = ("initial_text", "eng_text", "user__username", "stable_request_id")
    list_filter = ("user",)
    list_display = (
        "initial_text",
        "eng_text",
        "user",
        "stable_request_id",
        "single_image",
        "answer_sent",
        "created_at"
    )


@admin.register(StableAccount)
class StableAccountAdmin(admin.ModelAdmin):
    pass


@admin.register(StableSettings)
class StableSettingsAdmin(SingletonModelAdmin):
    pass
