import requests
from django.contrib import admin, auth
from django.contrib.admin import SimpleListFilter
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from bot_config.models import SiteSettings
from discord_messages.telegram_helper import bot
from telegram_to_discord.settings import SITE_DOMAIN
from users.helper import add_generations
from users.models import User, Style, CustomSettings


class PaidFilter(SimpleListFilter):
    title = 'Оплатившие'
    parameter_name = 'remain_paid_messages'

    def lookups(self, request, model_admin):
        # define the filter options
        return (
            ('yes', 'Оплатившие'),
            ('no', 'Не оплатившие'),
        )

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(remain_paid_messages__gt=0)


class UserAdmin(BaseUserAdmin):
    change_form_template = 'change_form.html'
    list_display = (
        "id", "username", "is_active", "remain_paid_messages", "remain_messages", "remain_video_messages"
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2"),
            },
        ),
    )
    fieldsets = (
        ("Главная информация", {"fields": (
            "username",
            "chat_id",
            "partner_id",
            "date_of_payment",
            "date_payment_expired",
            "remain_messages",
            "remain_paid_messages",
            "remain_video_messages",
            "is_active",
            "is_test_user",
            "account",
            "stable_account",
            "preset",
            "style",
            "custom_settings"
        )}),
        ("Статус пользователя", {
            "fields": ("is_staff", "is_superuser")
        })
    )
    ordering = ["-id"]
    form = UserChangeForm
    search_fields = ("username", "chat_id")
    actions = ["send_message", "send_to_all"]
    list_filter = (PaidFilter,)

    def send_message(self, request, queryset):
        site_settings = SiteSettings.get_solo()
        for user in queryset:
            if user.chat_id:
                try:
                    message_text = site_settings.notice_message.replace("{next}", "\n\n")
                    bot.send_message(
                        chat_id=user.chat_id,
                        text=message_text,
                        parse_mode="HTML"
                    )
                except Exception:
                    pass

    def send_to_all(self, request, queryset):
        requests.post(f"{SITE_DOMAIN}/async/telegram/send_info_messages")

    send_message.short_description = "Отправить сообщение"
    send_to_all.short_description = "Отправить всем"

    def response_change(self, request, obj: User):
        if "add_20" in request.POST and obj.partner_id:
            add_generations(
                chat_id=obj.partner_id,
                generations_to_add=20
            )
        if "add_100" in request.POST and obj.partner_id:
            add_generations(
                chat_id=obj.partner_id,
                generations_to_add=100
            )
        if "set_password" in request.POST:
            obj.set_password("12345")
            obj.save()
        return super().response_change(request, obj)

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term and search_term.startswith("@"):
            short_search_term = search_term[1:]
            try:
                queryset |= self.model.objects.filter(username__icontains=short_search_term)
            except Exception:
                pass
        return queryset, use_distinct


@admin.register(Style)
class StyleAdmin(admin.ModelAdmin):
    pass


@admin.register(CustomSettings)
class CustomSettingsAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    actions = ["make_copy"]

    def make_copy(self, request, queryset):
        new_settings = queryset.first()
        new_settings.pk = None
        new_settings.save()

    make_copy.short_description = "Сделать копию"


admin.site.register(User, UserAdmin)
admin.site.unregister(auth.models.Group)
