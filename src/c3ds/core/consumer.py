import json
import logging

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

logger = logging.getLogger(__name__)


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
        text_data_json = json.loads(text_data)
        logger.info('Received message: %s', text_data)

        # self.send(text_data=json.dumps({"message": message}))

    def cmd(self, event):
        # Receive message from display group
        if not 'cmd' in event:
            raise ValueError('No command specified')
        cmd = event["cmd"]

        if isinstance(cmd, str):
            cmd = {'cmd': cmd}

        # Send message to WebSocket
        self.send(text_data=json.dumps(cmd))