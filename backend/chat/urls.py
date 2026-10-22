
from django.urls import path
from .views import health_check, chat_view

urlpatterns = [
    path("health/", health_check, name="health_check"),
    path("chat/", chat_view, name="chat"),
]
