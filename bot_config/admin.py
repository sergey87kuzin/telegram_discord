from django.contrib import admin
from solo.admin import SingletonModelAdmin

from bot_config.models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(SingletonModelAdmin):
    pass
