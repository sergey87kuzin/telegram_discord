from datetime import datetime, timedelta
from http import HTTPStatus

import pytz
import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic import TemplateView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from bot_config.models import SiteSettings
from orders.helper import create_prodamus_order_object
from orders.models import Order
from users.models import User


class CreateOrderView(generic.View):

    def get(self, request, *args, **kwargs):
        site_settings = SiteSettings.get_solo()
        # user = request.user
        user = User.objects.first()
        term = request.GET.get("term")
        if term == "month":
            cost = site_settings.month_tariff_cost
            days = 30
        elif term == "day":
            cost = site_settings.day_tariff_cost
            days = 1
        else:
            return redirect(reverse_lazy("index"))
        order = Order.objects.create(
            user=user,
            total_cost=cost,
            days=days,
        )
        order_string = create_prodamus_order_object(order)
        response = requests.get(
            url=settings.PAYMENT_URL + order_string,
            headers={
                "Content-type": "text/plain;charset=utf-8"
            },
        )
        order.payment_url = response.text
        return redirect(response.text)


class SuccessPage(TemplateView):
    template_name = "success.html"


class FailPage(TemplateView):
    template_name = "fail.html"


class NotificationView(GenericAPIView):

    def post(self, request, *args, **kwargs):
        order_id = request.data.get("order_num")
        if order := Order.objects.filter(id=order_id).select_related("user").first():
            utc = pytz.UTC
            order.payment_status = "Paid"
            order.save()
            user = order.user
            if user.date_payment_expired and user.date_payment_expired >= datetime.now().replace(tzinfo=utc):
                user.date_payment_expired += timedelta(days=order.days)
            else:
                user.date_of_payment = datetime.now()
                user.date_payment_expired = datetime.now() + timedelta(days=order.days)
            user.save()
        return Response(status=HTTPStatus.OK, data={})
