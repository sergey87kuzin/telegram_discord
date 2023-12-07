import re

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import generic

from telegram_to_discord import settings
from users.models import User


class Profile(generic.DetailView):
    model = User
    template = "users/user_detail.html"

    def get_object(self, queryset=None):
        return self.request.user

    def post(self, request, *args, **kwargs):
        user = request.user
        user.first_name = request.POST.get("name")
        user.last_name = request.POST.get("surname")
        user.email = request.POST.get("email")
        user.save()
        return redirect(reverse_lazy("users:detail-profile"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        MOBILE_AGENT_RE = re.compile(r".*(iphone|mobile|androidtouch)", re.IGNORECASE)
        if MOBILE_AGENT_RE.match(self.request.META['HTTP_USER_AGENT']):
            context["is_mobile"] = True
        else:
            context["is_mobile"] = False
        return context


@method_decorator(login_required, "dispatch")
class UserChangePasswordView(generic.TemplateView):
    template_name = "users/change_password.html"


class UserRestorePasswordView(generic.TemplateView):
    template_name = "auth/restore_password.html"


class UserRestoreChangePasswordView(generic.TemplateView):
    template_name = "change-password-done.html"
