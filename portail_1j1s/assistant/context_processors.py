from .conf import assistant_enabled


def assistant_settings(request):
    return {"assistant_ia_enabled": assistant_enabled()}
