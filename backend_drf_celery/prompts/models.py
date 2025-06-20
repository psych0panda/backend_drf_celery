from __future__ import annotations

import uuid

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Prompt(models.Model):
    """System/template prompt that can be reused by backend.

    Version field хранит *активную* версию. Исторические тексты лежат в
    :class:`PromptVersion`.
    """

    class PromptType(models.TextChoices):
        SYSTEM = "system", "system"
        TEMPLATE = "template", "template"
        TOOL = "tool", "tool"
        USER = "user", "user"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=32, choices=PromptType.choices)
    name = models.CharField(max_length=255)
    text = models.TextField()
    parameters = models.JSONField(default=dict, blank=True)
    version = models.PositiveIntegerField(default=1, help_text="Current active version number")
    tags = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["type", "name"]),
            models.Index(fields=["tags"], name="prompt_tags_gin"),
        ]

    def __str__(self) -> str:  # noqa: D401
        return f"{self.name} (v{self.version})"


class PromptVersion(models.Model):
    """Immutable snapshot of a prompt text with specific version."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE, related_name="versions")
    version = models.PositiveIntegerField()
    text = models.TextField()
    parameters = models.JSONField(default=dict, blank=True)
    author = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("prompt", "version")
        ordering = ["-created_at"]

    def __str__(self) -> str:  # noqa: D401
        return f"{self.prompt.name} v{self.version}"


class UserPrompt(models.Model):
    """Raw input text from end users (for analytics / replay)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="prompts")
    text = models.TextField()
    lang = models.CharField(max_length=8, default="en")
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["lang"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:  # noqa: D401
        return f"Prompt by {self.user} at {self.created_at:%Y-%m-%d %H:%M}" 