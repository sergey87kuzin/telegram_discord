from http import HTTPStatus

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views import generic
from rest_framework.response import Response
from rest_framework.views import APIView

from discord_messages.models import ConfirmMessage
from hashing import Hasher
from users.forms import UserAuthForm, UserRegistrationForm
from users.models import User


class LoginFormView(LoginView):
    form_class = UserAuthForm
    template_name = "auth/login.html"
    success_url = reverse_lazy("index")
    redirect_authenticated_user = True

    def get_success_url(self):
        url = self.get_redirect_url()
        return url or self.success_url


class UserRegistrationView(generic.UpdateView):
    template_name = "auth/registration.html"
    form_class = UserRegistrationForm
    success_url = reverse_lazy("index")

    def get_queryset(self):
        return User.objects.all()

    def get_context_data(self, **kwargs):
        user = User.objects.get(id=self.kwargs.get("pk"))
        kwargs["username"] = user.username
        context = super().get_context_data(**kwargs)
        return context

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs["request"] = self.request
        if self.request.GET:
            form_kwargs["username"] = self.request.GET.get("telegram")
        return form_kwargs


class AjaxUserRegistrationView(UserRegistrationView):
    template_name = "includes/auth.html"

    def get_success_url(self):
        return self.success_url

    def form_valid(self, form):
        super().form_valid(form)
        return JsonResponse(
            {
                "error": False,
                "success_messages": "Сообщение с кодом подтверждения отправлено Вам в бот telegram",
            }
        )

    def form_invalid(self, form):
        return JsonResponse({"error": True, "error_messages": form.errors})


class AjaxLoginFormView(LoginFormView):
    template_name = "auth/login_extended.html"

    def get_success_url(self):
        return self.success_url

    def form_invalid(self, form):

        return JsonResponse(
            {
                "error": True,
                "tpl": render_to_string(self.template_name, context=self.get_context_data(form=form)),
            }
        )

    def form_valid(self, form):
        data = form.clean()
        user = User.objects.filter(username__iexact=data.get("telegram")).first()
        if user:
            login(self.request, user, backend="django.contrib.auth.backends.ModelBackend")
            return JsonResponse({"error": False, "url": self.get_success_url()})

        self.form_invalid(form)


class AjaxLogin(APIView):

    def post(self, request, *args, **kwargs):
        user = User.objects.filter(
            username__iexact=request.data.get("telegram")
        ).first()
        password = request.data.get("password")
        result = user.check_password(password) or Hasher.verify_password(password, user.password)
        if result:
            login(self.request, user, backend="django.contrib.auth.backends.ModelBackend")
            return Response(status=HTTPStatus.OK, data={"url": reverse("index")})
        return Response(status=HTTPStatus.BAD_REQUEST)


@method_decorator(login_required, "dispatch")
class LogoutView(generic.View):
    def get(self, request, *args, **kwargs):
        logout(self.request)
        return HttpResponseRedirect(reverse_lazy("index"))


class RegistrationCompleteView(generic.TemplateView):
    template_name = "auth/registration_complete.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)
