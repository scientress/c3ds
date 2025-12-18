import json
import logging
from datetime import datetime, UTC
from time import time_ns

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.core.cache import cache

from c3ds.core.models import Display

logger = logging.getLogger(__name__)

class RemoteShellConsumer(WebsocketConsumer):
    def connect(self):
        user = self.scope['user']
        if not user.is_authenticated or not user.is_superuser:
            return

        self.slug = self.scope['url_route']['kwargs']['display_slug']
        self.group = f'shell_{self.slug}'

        async_to_sync(self.channel_layer.group_add)(
            self.group, self.channel_name
        )
        async_to_sync(self.channel_layer.group_add)(
            'shells', self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data = None, bytes_data = None):
        data: dict[str] = json.loads(text_data)
        logger.debug('Received message: %s', text_data)

        match data.get('cmd', None):
            case 'rsMSG':
                async_to_sync(self.channel_layer.group_send)(
                    f'display_{data.get('displaySlug')}',
                    {'type': 'cmd_data', 'data': data}
                )

    def cmd_data(self, event):
        if not 'data' in event:
            raise ValueError('No command/data specified')

        self.send(text_data=json.dumps(event["data"]))

class DisplayConsumer(WebsocketConsumer):
    def connect(self):
        self.display_slug = self.scope['url_route']['kwargs']['display_slug']
        self.display_group = f'display_{self.display_slug}'

        async_to_sync(self.channel_layer.group_add)(
            self.display_group, self.channel_name
        )
        async_to_sync(self.channel_layer.group_add)(
            'displays', self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data = None, bytes_data = None):
        data: dict[str] = json.loads(text_data)
        logger.debug('Received message: %s', text_data)

        match data.get('cmd', None):
            case 'ping':
                if not self.scope['user'].is_authenticated:
                    cache.set(Display.heartbeat_cache_key_for_slug(self.display_slug), datetime.now(tz=UTC), None)
                self.cmd({'cmd': 'pong'})

            case 'NTPRequest':
                self.cmd_data({'data': {
                    'cmd': 'NTPResponse',
                    'serverTime': time_ns() // 1000000,
                    'clientSendTimestamp': data['sendTimestamp'],
                }})

            case 'rsRES':
                async_to_sync(self.channel_layer.group_send)(
                    f'shell_{self.display_slug}',
                    {'type': 'cmd_data', 'data': data}
                )

    def cmd(self, event):
        # Receive message from display group
        if not 'cmd' in event:
            raise ValueError('No command specified')
        cmd = event["cmd"]

        if isinstance(cmd, str):
            cmd = {'cmd': cmd}

        logger.debug('Sending command: %s', cmd)
        # Send message to WebSocket
        self.send(text_data=json.dumps(cmd))

    def cmd_data(self, event):
        if not 'data' in event:
            raise ValueError('No command/data specified')

        self.send(text_data=json.dumps(event["data"]))
