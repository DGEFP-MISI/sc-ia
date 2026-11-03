import uuid

from django.db import models
from django.utils import timezone


class AssistantConversation(models.Model):
    """Historique temporaire d'une conversation anonyme."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    messages = models.JSONField(default=list)

    created_at = models.DateTimeField(
        default=timezone.now,
    )

    expires_at = models.DateTimeField(
        db_index=True,
    )

    class Meta:
        verbose_name = "Conversation de l'assistant"
        verbose_name_plural = "Conversations de l'assistant"
