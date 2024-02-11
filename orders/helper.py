import urllib

import requests
from django.conf import settings

from bot_config.models import SiteSettings
from orders.models import Order
from users.models import User


def create_prodamus_order_object(order):
    order_string = f"?order_id={order.id}&products[0][price]={order.total_cost}" \
                   "&products[0][quantity]=1&products[0][name]=Обучающие материалы&do=link"
    return order_string


def create_order_from_menu(tariff, username):
    site_settings = SiteSettings.get_solo()
    TARIFF_COSTS = {
        "day": {
            "cost": site_settings.day_tariff_cost,
            "days": 30,
            "message_count": site_settings.day_tariff_count
        },
        "month": {
            "cost": site_settings.month_tariff_cost,
            "days": 30,
            "message_count": site_settings.month_tariff_count
        }
    }
    order_data = TARIFF_COSTS.get(tariff)
    if not order_data:
        return ""
    user = User.objects.filter(username=username).first()
    if not user:
        return ""
    order = Order.objects.create(
        user=user,
        total_cost=order_data.get("cost"),
        days=order_data.get("days"),
        message_count=order_data.get("message_count")
    )
    order_string = create_prodamus_order_object(order)
    response = requests.get(
        url=settings.PAYMENT_URL + order_string,
        headers={
            "Content-type": "text/plain;charset=utf-8"
        },
    )
    order.payment_url = response.text
    order.save()
    return response.text
