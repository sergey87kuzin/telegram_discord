from django.shortcuts import redirect
from django.urls import reverse_lazy
from rest_framework import generics, permissions

from users.models import User
from users.serializers import ChangePasswordSerializer, UserProfileSerializer


class UserProfileApiView(generics.RetrieveAPIView, generics.UpdateAPIView, generics.GenericAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ["get", "post"]

    def get_object(self):
        return self.request.user


class UserProfileUpdateAPIView(generics.GenericAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def post(self, request, *args, **kwargs):
        return redirect(reverse_lazy("index"))


class ChangePasswordView(generics.UpdateAPIView):
    """
    Смена пароля
    """

    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ["put"]
    queryset = User.objects.all()

    def get_object(self):
        return self.request.user
