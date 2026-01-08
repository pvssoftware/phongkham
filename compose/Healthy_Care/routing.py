from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from django.conf.urls import url
from doctors.consumers import ListPatientsConsumer, ListPatientsFinishedConsumer


application = ProtocolTypeRouter({
    'websocket':AuthMiddlewareStack(
        URLRouter(
            [
                url(r"^list-patients-finished/$",ListPatientsFinishedConsumer),
                url(r"^list-patients/$",ListPatientsConsumer),
            ]
        )
    )
})