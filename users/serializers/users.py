
from django.contrib.auth import password_validation, update_session_auth_hash
from django.utils import timezone
from rest_framework import serializers

from users.models import User
from django.utils.translation import gettext_lazy as _


class UserProfileSerializer(serializers.ModelSerializer):
    email = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "is_staff",
            "is_active",
            "email",
        )


class ChangePasswordSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для смены пароля
    """

    old_password = serializers.CharField(required=False, write_only=True)
    new_password = serializers.CharField(required=True, min_length=8, write_only=True)
    new_password_confirm = serializers.CharField(required=True, min_length=8, write_only=True)

    class Meta:
        model = User
        fields = ("old_password", "new_password", "new_password_confirm")

    def validate_new_password(self, password):
        password_validation.validate_password(password, self.instance)
        return password

    def validate(self, data):
        super().validate(data)
        request = self.context.get("request")
        if data.get("new_password") != data.get("new_password_confirm"):
            raise serializers.ValidationError({"error": _("Пароли не совпадают")})
        if not request.user.is_first_password and not request.user.check_password(data.get("old_password")):
            raise serializers.ValidationError({"error": _("Неверный пароль")})
        return data

    def update(self, instance, validated_data):
        instance.set_password(validated_data.get("new_password"))
        instance.is_first_password = False
        instance.save(update_fields=["password", "is_first_password"])
        update_session_auth_hash(self.context.get("request"), instance)
        return instance


class CRMChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True, write_only=True, min_length=8)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())


class AccountRestorePassword(serializers.Serializer):
    """
    Восстановление пароля - шаг первый, отправка email с токеном
    """

    email = serializers.EmailField(required=True)

    def validate(self, data):
        super().validate(data)
        user = User.objects.filter(email__iexact=data.get("email")).first()
        if not user:
            raise serializers.ValidationError(_("Данный e-mail не зарегистрирован"))
        if not user.is_active:
            raise serializers.ValidationError(_("Данный аккаунт не активирован"))
        return data


class AccountChangePasswordFromRestore(serializers.Serializer):
    """
    Смена пароля после получения EMAIL с токеном
    """

    password = serializers.CharField(required=True, min_length=8)
    repeated_password = serializers.CharField(required=True, min_length=8)
    uid = serializers.CharField(required=True, max_length=None)
    activation_token = serializers.CharField(required=True, max_length=None)
    wrong_token_error = "Не валидный токен"

    def validate(self, data):
        password = data.get("password")
        repeated_password = data.get("repeated_password")
        super().validate(data)
        if password and repeated_password and password != repeated_password:
            raise serializers.ValidationError(_("Пароли не совпадают"))
        try:
            uid = data.get("uid")
            user = User.objects.filter(pk=uid, is_active=True).first()
            password_validation.validate_password(password, user)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError(self.wrong_token_error)
        if user:
            return data
        else:
            raise serializers.ValidationError(self.wrong_token_error)

    def change_password(self):
        uid = self.validated_data.get("uid")
        user = User.objects.filter(pk=uid).first()
        user.set_password(self.validated_data.get("password"))
        user.type_password = "default"
        user.save()
        return user
