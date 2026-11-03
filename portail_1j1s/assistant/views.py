import json
import uuid

from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_POST

from .services.albert import AlbertAPIError, AlbertClient
from .services.markdown import render_assistant_markdown

from .models import AssistantConversation

CONVERSATION_ID_SESSION_KEY = "assistant_1j1s_conversation_id"

CONVERSATION_LIFETIME_SECONDS = 30 * 60
CONVERSATION_MAX_MESSAGES = 20

def get_conversation_history(request):
    """Récupère l'historique de la conversation anonyme non expirée."""

    # Supprimer les anciennes données stockées dans la session Django.
    request.session.pop("assistant_1j1s_conversation", None)
    request.session.pop("assistant_1j1s_conversation_expiry", None)

    conversation_id = request.session.get(CONVERSATION_ID_SESSION_KEY)

    if not conversation_id:
        return []

    try:
        conversation_uuid = uuid.UUID(str(conversation_id))
    except (ValueError, TypeError, AttributeError):
        request.session.pop(CONVERSATION_ID_SESSION_KEY, None)
        return []

    conversation = AssistantConversation.objects.filter(
        id=conversation_uuid
    ).first()

    if conversation is None:
        request.session.pop(CONVERSATION_ID_SESSION_KEY, None)
        return []

    if timezone.now() >= conversation.expires_at:
        conversation.delete()
        request.session.pop(CONVERSATION_ID_SESSION_KEY, None)
        return []

    if not isinstance(conversation.messages, list):
        return []

    return [
        entry
        for entry in conversation.messages[-CONVERSATION_MAX_MESSAGES:]
        if (
            isinstance(entry, dict)
            and entry.get("role") in ("user", "assistant")
            and isinstance(entry.get("content"), str)
        )
    ]

def save_conversation_history(request, history):
    """Enregistre la conversation dans la table dédiée."""

    expires_at = timezone.now() + timezone.timedelta(
        seconds=CONVERSATION_LIFETIME_SECONDS
    )

    conversation_id = request.session.get(CONVERSATION_ID_SESSION_KEY)

    try:
        conversation_uuid = uuid.UUID(str(conversation_id))
    except (ValueError, TypeError, AttributeError):
        conversation_uuid = None

    conversation = None

    if conversation_uuid:
        conversation = AssistantConversation.objects.filter(
            id=conversation_uuid,
            expires_at__gt=timezone.now(),
        ).first()

    if conversation is None:
        conversation = AssistantConversation.objects.create(
            messages=history[-CONVERSATION_MAX_MESSAGES:],
            expires_at=expires_at,
        )

        request.session[CONVERSATION_ID_SESSION_KEY] = str(
            conversation.id
        )

    else:
        conversation.messages = history[-CONVERSATION_MAX_MESSAGES:]
        conversation.expires_at = expires_at
        conversation.save(
            update_fields=["messages", "expires_at"]
        )

@never_cache
@require_GET
def assistant_history(request):
    """Retourne l'historique non expiré de la conversation anonyme."""

    history = get_conversation_history(request)

    return JsonResponse(
        {
            "messages": [
                {
                    "role": entry["role"],
                    "content": entry["content"],
                    "content_html": (
                        render_assistant_markdown(entry["content"])
                        if entry["role"] == "assistant"
                        else None
                    ),
                }
                for entry in history
            ],
        }
    )

@never_cache
@require_POST
def assistant_chat(request):
    """Reçoit une question et retourne la réponse d'Albert API."""

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {"error": "Le message envoyé est invalide."},
            status=400,
        )

    if not isinstance(data, dict):
        return JsonResponse(
            {"error": "Le message envoyé est invalide."},
            status=400,
        )

    message = data.get("message")

    if not isinstance(message, str) or not message.strip():
        return JsonResponse(
            {"error": "Merci de saisir une question."},
            status=400,
        )

    message = message.strip()

    if len(message) > 2000:
        return JsonResponse(
            {"error": "La question ne doit pas dépasser 2 000 caractères."},
            status=400,
        )

    messages = [
        {
            "role": "system",
            "content": (
                "Tu es l'assistant du portail public 1jeune1solution. "
                "Tu aides les jeunes à comprendre les démarches liées "
                "à l'orientation, à la formation, à l'emploi et aux aides. "
                "Réponds en français, clairement et sans inventer "
                "d'informations. Si tu ne sais pas, indique-le. "
                "Privilégie des réponses concises, avec des titres courts "
                "et des listes à puces lorsque cela facilite la lecture. "
                "N'utilise pas de tableaux Markdown : l'assistant est "
                "principalement consulté dans un panneau étroit sur mobile."
            ),
        },
    ]

    # Récupérer les échanges précédents non expirés.
    history = get_conversation_history(request)

    # Transmettre à Albert l'historique puis la nouvelle question.
    messages.extend(history)
    messages.append(
        {
            "role": "user",
            "content": message,
        }
    )

    try:
        answer = AlbertClient().chat(messages)
    except AlbertAPIError:
        return JsonResponse(
            {
                "error": (
                    "L'assistant est momentanément indisponible. "
                    "Merci de réessayer."
                )
            },
            status=503,
        )

    # Enregistrer uniquement les échanges ayant reçu une réponse.
    history.append(
        {
            "role": "user",
            "content": message,
        }
    )

    history.append(
        {
            "role": "assistant",
            "content": answer[:10000],
        }
    )

    save_conversation_history(request, history)

    return JsonResponse(
        {
            "answer": answer,
            "answer_html": render_assistant_markdown(answer),
        }
    )
