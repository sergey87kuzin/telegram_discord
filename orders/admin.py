from django.contrib import admin

from orders.models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    search_fields = ("user__username", "created_at")
    list_display = (
        "id",
        "user",
        "total_cost",
        "created_at",
        "payment_status",
        "payment_date",
    )
