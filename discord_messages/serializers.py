from rest_framework import serializers

from discord_messages.discord_helper import send_message_to_discord


class MessageSerializer(serializers.Serializer):
    message_text = serializers.CharField()

    def validate(self, attrs):
        return attrs

    def send_message(self):
        return send_message_to_discord(self.validated_data.get("message_text"))
