from __future__ import annotations

from rest_framework import serializers


class PromptSerializer(serializers.Serializer):
    prompt = serializers.CharField(max_length=1000) 