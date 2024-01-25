from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from solo.admin import SingletonModelAdmin

from stable_messages.models import StableMessage, StableAccount, StableSettings


class FreeFilter(SimpleListFilter):
    title = 'Бесплатные'
    parameter_name = 'user__remain_paid_messages'

    def lookups(self, request, model_admin):
        # define the filter options
        return (
            (0, 'Бесплатные'),
        )

    def queryset(self, request, queryset):
        if self.value() == "0":
            return queryset.filter(user__remain_paid_messages=0)


@admin.register(StableMessage)
class StableMessageAdmin(admin.ModelAdmin):
    search_fields = ("initial_text", "eng_text", "user__username", "stable_request_id")
    list_filter = ("user", FreeFilter)
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
