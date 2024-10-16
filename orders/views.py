from datetime import datetime, timedelta
from http import HTTPStatus

import pytz
import requests
import telebot
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic import TemplateView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from bot_config.models import SiteSettings
from courses.models import Course, UserCourses, Prolongation
from orders.helper import create_prodamus_order_object
from orders.models import Order
from users.helper import add_generations

payment_bot = telebot.TeleBot(settings.PAYMENT_TELEGRAM_TOKEN)


class CreateOrderView(generic.View):

    def get(self, request, *args, **kwargs):
        site_settings = SiteSettings.get_solo()
        user = request.user
        if not user.is_authenticated:
            return redirect("index")
        term = request.GET.get("term")
        course = None
        prolongation = None
        if term == "month":
            cost = site_settings.month_tariff_cost
            days = 30
            message_count = site_settings.month_tariff_count
        elif term == "day":
            cost = site_settings.day_tariff_cost
            days = 30
            message_count = site_settings.day_tariff_count
        course_id = request.GET.get("course_id")
        if course_id:
            if course := Course.objects.get(id=course_id):
                cost = course.cost
                days = course.duration
                message_count = site_settings.month_tariff_count
        prolongation_id = request.GET.get("prolongation_id")
        if prolongation_id:
            if prolongation := Prolongation.objects.filter(id=prolongation_id).first():
                cost = prolongation.cost
                days = prolongation.duration
                message_count = site_settings.month_tariff_count
        if not term and not course_id and not prolongation:
            return redirect(reverse_lazy("index"))

        order = Order.objects.create(
            user=user,
            total_cost=cost,
            days=days,
            message_count=message_count
        )
        if course:
            order.course_id = course.id
            order.save()
        if prolongation:
            order.prolongation_id = prolongation_id
            order.save()
        order_string = create_prodamus_order_object(order)
        response = requests.get(
            url=settings.PAYMENT_URL + order_string,
            headers={
                "Content-type": "text/plain;charset=utf-8"
            },
        )
        order.payment_url = response.text
        order.save()
        return redirect(response.text)


class SuccessPage(TemplateView):
    template_name = "success.html"


class FailPage(TemplateView):
    template_name = "fail.html"


class NotificationView(GenericAPIView):

    def post(self, request, *args, **kwargs):
        if request.data.get("payment_status") != "success":
            return Response(status=HTTPStatus.OK, data={})
        order_id = request.data.get("order_num")
        try:
            int(order_id)
        except Exception:
            chat_ids = ["1792622682", "344637537"]
            for chat_id in chat_ids:
                payment_bot.send_message(chat_id, text="Новая оплата марафона")
            return Response(status=HTTPStatus.OK, data={})
        if order := Order.objects.filter(id=order_id).select_related("user").first():
            utc = pytz.UTC
            order.payment_status = "Paid"
            chat_ids = ["1792622682", "344637537"]
            for chat_id in chat_ids:
                payment_bot.send_message(chat_id, text=f"Новая оплата, {order.total_cost}")
            order.save()
            user = order.user
            if order.course_id:
                UserCourses.objects.create(
                    user_id=order.user_id,
                    course_id=order.course_id,
                    buying_date=datetime.now().replace(tzinfo=utc)
                )
                user.remain_paid_messages = order.message_count
                user.date_of_payment = datetime.now()
                user.date_payment_expired = datetime.now() + timedelta(days=90)
                user.save()
                return Response(status=HTTPStatus.OK, data={})
            if order.prolongation_id:
                prolongation = Prolongation.objects.filter(id=order.prolongation_id).first()
                course = UserCourses.objects.filter(
                    user_id=order.user_id,
                    course_id=prolongation.course_id,
                ).first()
                if not course:
                    return Response(status=HTTPStatus.OK, data={})
                user.remain_paid_messages = order.message_count
                user.date_of_payment = datetime.now()
                user.date_payment_expired = datetime.now() + timedelta(days=prolongation.duration)
                user.save()
                course.expires_at = datetime.now() + timedelta(days=prolongation.duration)
                course.save()
                return Response(status=HTTPStatus.OK, data={})
            if order.video_message_count:
                user.remain_video_messages += order.video_message_count
                if order.video_message_count < 10:
                    user.used_test_video_payment = True
                user.save()
                chat_ids = ["1792622682", "344637537"]
                for chat_id in chat_ids:
                    payment_bot.send_message(chat_id, text=f"Оплата видео")
                return Response(status=HTTPStatus.OK, data={})
            user.date_of_payment = datetime.now()
            user.date_payment_expired = datetime.now() + timedelta(days=order.days)
            user.remain_paid_messages = order.message_count
            user.save()
            if user.partner_id:
                add_generations(chat_id=user.partner_id, generations_to_add=int(order.message_count / 10))
        return Response(status=HTTPStatus.OK, data={})
