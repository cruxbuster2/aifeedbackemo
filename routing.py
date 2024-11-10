from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path

application = ProtocolTypeRouter({
    # Empty for now. Add WebSocket protocol later if needed
})