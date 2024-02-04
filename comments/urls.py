from django.urls import path

from comments.views import CommentMessageAPIView

app_name = "comments"

urlpatterns = [
    path("telegram-callback/", CommentMessageAPIView.as_view(), name="comments_callback"),
]
