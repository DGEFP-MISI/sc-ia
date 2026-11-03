from django.core.management.base import BaseCommand
from django.utils import timezone

from portail_1j1s.assistant.models import AssistantConversation


class Command(BaseCommand):
    help = "Supprime les conversations expirées de l'assistant 1jeune1solution."

    def handle(self, *args, **options):
        deleted_count, _ = AssistantConversation.objects.filter(
            expires_at__lte=timezone.now()
        ).delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"{deleted_count} conversation(s) expirée(s) supprimée(s)."
            )
        )
