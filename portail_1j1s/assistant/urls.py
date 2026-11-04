from django.urls import path

from .views import assistant_chat, assistant_history

urlpatterns = [
    path("chat/", assistant_chat, name="chat"),
    path("history/", assistant_history, name="history"),
]
