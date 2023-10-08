from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from cart.models.cart import Cart
from catalog.models import Product
from subscriptions.services.sms import send_sms
from users.helpers.user_helper import UserHelper
from users.models import User
from users.services import RetailLoyaltyService
from utils.models.sms_message import SmsMessage


class RegisterUserSerializer(serializers.Serializer):
    confirmation_code = serializers.IntegerField()
    phone = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()

    class Meta:
        fields = ("confirmation_code", "phone", "last_name", "first_name")

    def validate(self, attrs):

        user = self.context["view"].request.user  # type: User
        # if users.loyalty_id and users.registered_in_loyalty:
        #     raise serializers.ValidationError({"error": _("Вы уже зарегистрированы в программе лояльности")})
        user.phone = attrs['phone']
        user.first_name = attrs['first_name']
        user.last_name = attrs['last_name']
        user.save(update_fields=("first_name", "last_name", "phone"))
        errors = {}

        if not user.phone:
            errors["phone"] = _("Для регистрации в программе лояльности нужно указать номер телефона")

        if not user.first_name:
            errors["first_name"] = _("Для регистрации в программе лояльности нужно указать своё имя")

        if not user.last_name:
            errors["last_name"] = _("Для регистрации в программе лояльности нужно указать свою фамилию")

        if errors:
            raise serializers.ValidationError(errors)

        sms_errors = SmsMessage().check_sms_code(
            phone_number=user.phone, confirmation_code=attrs.get("confirmation_code")
        )
        if sms_errors:
            raise serializers.ValidationError(sms_errors)

        retail_data = RetailLoyaltyService().filter_accounts({"phoneNumber": attrs.get("phone")})
        self.result = UserHelper().handle_existing_loyalty(user.email, retail_data)
        if self.result.get("message") != 'success':
            raise serializers.ValidationError({"phone": self.result.get("message")})

        return attrs

    def create(self, validated_data):
        retail_service = RetailLoyaltyService()
        user = self.context["view"].request.user  # type: User

        if self.result.get("has_loyalty"):
            UserHelper().bind_loyalty(email=user.email, loyalty_id=self.result.get("loyalty_id"))
        user.refresh_from_db()
        if not self.result.get("has_loyalty") and not retail_service.register_user(user=user):
            raise serializers.ValidationError(
                {"users": _("Произошла ошибка при регистрации в системе лояльности. Пожалуйста, попробуйте позже")}
            )
        retail_data = retail_service.get_user(user=user)
        self.user_data = {
            "active": retail_data.get("active", False),
            "bonuses": retail_data.get("amount", False),
            "ordersSum": retail_data.get("ordersSum", False),
            "nextLevelSum": retail_data.get("nextLevelSum", False),
            "level": retail_data.get("level", False),
            "status": retail_data.get("status", False),
        }
        return self.user_data

    @property
    def data(self):
        return self.user_data


class SmsConfirmSerializer(serializers.ModelSerializer):
    """
    Отправка смс-подтверждения пользователю
    """

    phone_number = serializers.RegexField(
        regex=r"^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,9}$", required=True
    )

    class Meta:
        model = SmsMessage
        fields = ("phone_number",)

    def validate(self, attrs):
        last_message = SmsMessage.objects.filter(phone_number=attrs.get("phone_number")).last()
        if last_message:
            # throttling by 60 seconds
            if (timezone.localtime() - timezone.localtime(last_message.created_at)).total_seconds() < 60:
                raise serializers.ValidationError(
                    {"confirmation_code": "Слишком много отправок кодов. Попробуйте через несколько минут"}
                )
        return attrs

    def create(self, validated_data):

        instance = SmsMessage.objects.create(phone_number=validated_data.get("phone_number"))
        text = send_sms(
            phone=instance.phone_number,
            tpl_name="sms/sms_confirmation.html",
            text=dict(code=instance.code),
        )
        instance.save(update_fields=("is_sent",))
        return instance


class UserLoyaltyInfoSerialzier(serializers.Serializer):
    class Meta:
        fields = []

    def validate(self, attrs):
        user = self.context["view"].request.user  # type: User
        if not user.loyalty_id and not user.registered_in_loyalty:
            raise serializers.ValidationError({"doesnt_registered": _("Вы не зарегистрированы в программе лояльности")})

        return attrs

    def create(self, validated_data):
        retail_service = RetailLoyaltyService()
        retail_data = retail_service.get_user(user=self.context["view"].request.user)
        if not retail_data.get("found", False):
            raise serializers.ValidationError({"doesnt_registered": _("Вы не зарегистрированы в программе лояльности")})
        self.user_data = {
            "active": retail_data.get("active", False),
            "bonuses": retail_data.get("amount", False),
            "ordersSum": retail_data.get("ordersSum", False),
            "nextLevelSum": retail_data.get("nextLevelSum", False),
            "level": retail_data.get("level", False),
            "status": retail_data.get("status", False),
        }
        return self.user_data

    @property
    def data(self):
        return self.user_data


class CartDiscountSerialzier(serializers.Serializer):
    class Meta:
        fields = []

    def validate(self, attrs):
        user = self.context["view"].request.user  # type: User
        if not user.loyalty_id and not user.registered_in_loyalty:
            raise serializers.ValidationError({"doesnt_registered": _("Вы не зарегистрированы в программе лояльности")})

        return attrs

    def create(self, validated_data):
        retail_service = RetailLoyaltyService()
        cart = Cart.get_cart_from_request(self.context["request"])  # type: Cart
        self.user_data = retail_service.calculate_products_discount(
            products=cart.products_json,
            user=self.context["view"].request.user
        )
        return self.user_data

    @property
    def data(self):
        return self.user_data


class BonusesHistorySerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=["waiting_activation", "burn_soon"], required=True)
    page = serializers.IntegerField(min_value=1, required=True)

    class Meta:
        fields = ["status"]

    def validate(self, attrs):
        user = self.context["view"].request.user  # type: User
        if not user.loyalty_id and not user.registered_in_loyalty:
            raise serializers.ValidationError({"doesnt_registered": _("Вы не зарегистрированы в программе лояльности")})
        attrs["users"] = user

        return attrs

    def create(self, validated_data):
        retail_service = RetailLoyaltyService()
        self.user_data = retail_service.get_bonuses_history(
            user=validated_data["users"],
            status=validated_data["status"],
            page=validated_data["page"],
        )
        return self.user_data

    @property
    def data(self):
        return self.user_data


class LoyaltyProductDiscountsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = []

    def validate(self, attrs):
        user = self.context["view"].request.user  # type: User
        if not user.loyalty_id and not user.registered_in_loyalty:
            raise serializers.ValidationError({"doesnt_registered": _("Вы не зарегистрированы в программе лояльности")})
        attrs["users"] = user

        return attrs

    @property
    def data(self):
        self.validate({})
        retail_service = RetailLoyaltyService()
        self.product_discount_data = retail_service.calculate_products_discount(
            products=self.instance,
            user=self.context["view"].request.user
        )
        return self.product_discount_data
