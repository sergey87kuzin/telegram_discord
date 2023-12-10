from django import forms
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError

from discord_messages.models import ConfirmMessage
from discord_messages.telegram_helper import send_confirm_code
from users.models import User


def send_activation_message(user: User) -> None:
    """
    Отправляем сообщение в telegram для подтверждения
    """
    pass


class UserAuthForm(AuthenticationForm):
    """
    Форма авторизации менеджера в системе
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {
                "placeholder": "Ваш ник telegram",
                "class": "black_input"
            }
        )
        self.fields["password"].widget.attrs.update(
            {
                "placeholder": "Пароль",
                "class": "black_input"
            }
        )

    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        user = User.objects.filter(username__iexact=username).first()
        if not user.is_active:
            send_confirm_code(user)
            raise ValidationError("Осталось только активировать аккаунт, мы отправили вам сообщение!")
        if username and password:
            self.user_cache = authenticate(self.request, username=username, password=password)
            if not self.user_cache:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class UserRegistrationForm(forms.ModelForm):
    confirmation_code = forms.CharField(label="Код подтверждения из telegram", required=True)
    password1 = forms.CharField(label="Пароль", required=True)
    password2 = forms.CharField(label="Подтвердите пароль", required=True)

    class Meta:
        model = User
        fields = (
            "username",
            "password1",
            "password2",
            "confirmation_code",
        )

    def __init__(self, request, *args, **kwargs):
        username = kwargs.pop("username", "")
        super().__init__(*args, **kwargs)
        self.request = request
        self.fields["username"].widget.attrs.update(
            {
                "placeholder": "Ваш ник telegram",
                "class": "black_input",
                "id": "telegram-nickname"
            }
        )
        self.fields["username"].initial = kwargs.get("instance").username
        self.fields["password1"].widget.attrs.update(
            {
                "placeholder": "Пароль",
                "class": "black_input"
            }
        )
        self.fields["password2"].widget.attrs.update(
            {
                "placeholder": "Подтверждение пароля",
                "class": "black_input"
            }
        )
        self.fields["confirmation_code"].widget.attrs.update(
            {
                "placeholder": "Код подтверждения telegram",
                "class": "black_input"
            }
        )

    def clean(self):
        cleaned_data = self.cleaned_data
        if cleaned_data.get("password1") != cleaned_data.get("password2"):
            raise ValidationError("Пароли не совпадают")
        if self.instance.is_active:
            raise ValidationError("Пользователь с таким ником telegram уже существует")
        if not self.instance:
            raise ValidationError("Пользователя с таким ником telegram не существует. "
                                  "Пожалуйста, начните диалог с ботом.")
        if message := ConfirmMessage.objects.filter(
            telegram_nick=self.instance.username,
            code=cleaned_data.get("confirmation_code"),
            used=False,
            new_message_sent=False
        ).first():
            message.used = True
            message.save()
        else:
            raise ValidationError("Неверный код подтверждения")
        return cleaned_data

    def save(self, commit=True):
        user = User.objects.filter(username=self.cleaned_data["username"]).first()
        user.set_password(self.cleaned_data["password1"])
        user.is_active = True
        user.save()
        login(self.request, user, backend="django.contrib.auth.backends.ModelBackend")
        return user


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = "__all__"


class UserCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            "username",
            "password1",
            "is_active",
            "is_staff",
            "is_superuser",
        )
