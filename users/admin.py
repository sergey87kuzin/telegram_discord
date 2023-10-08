from django.contrib import admin, auth
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import User


class UserAdmin(BaseUserAdmin):
    change_form_template = 'loginas/change_form.html'
    list_display = (
        "id", "username", "is_superuser", "is_active",
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
            "date_of_payment",
            "date_payment_expired",
            "is_active",
            "account"
        )}),
    )
    ordering = ["-id"]
    form = UserChangeForm
    search_fields = ("username", )


admin.site.register(User, UserAdmin)
admin.site.unregister(auth.models.Group)
