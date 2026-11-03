import os


def assistant_enabled():
    """Indique si l'assistant est activé."""

    return os.environ.get(
        "ASSISTANT_IA_ENABLED", "false"
    ).lower() == "true"


def assistant_name():
    """Nom affiché dans l'interface."""

    return os.environ.get(
        "ASSISTANT_IA_NAME",
        "Assistant 1jeune1solution",
    )
