import uuid

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AssistantConversation",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "messages",
                    models.JSONField(default=list),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                    ),
                ),
                (
                    "expires_at",
                    models.DateTimeField(db_index=True),
                ),
            ],
            options={
                "verbose_name": "Conversation de l'assistant",
                "verbose_name_plural": "Conversations de l'assistant",
            },
        ),
    ]
