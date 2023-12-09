from rest_framework import serializers

from courses.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = (
            "text",
            "course"
        )

    def validate(self, attrs):
        return attrs
