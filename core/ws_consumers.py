import json

from channels.generic.websocket import AsyncJsonWebsocketConsumer


class OrderStreamConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):  # type: ignore[override]
        await self.channel_layer.group_add("orders", self.channel_name)
        await self.accept()

    async def disconnect(self, code):  # type: ignore[override]
        await self.channel_layer.group_discard("orders", self.channel_name)

    async def receive_json(self, content, **kwargs):  # type: ignore[override]
        # For now, just echo payload; later this will be used by staff/KDS
        await self.send_json({"type": "echo", "payload": content})

    async def order_updated(self, event):
        # Called when an order update is sent to the "orders" group
        await self.send_json(event["data"])
