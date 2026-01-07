from django.urls import path

from . import ws_consumers

websocket_urlpatterns = [
    # To be used for KDS and live order/table updates
    path("ws/orders/", ws_consumers.OrderStreamConsumer.as_asgi()),
]
