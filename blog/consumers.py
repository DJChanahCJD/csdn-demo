import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from common.cache import CacheKey
from blog.models import Blog
import time


class MessageConsumer(AsyncWebsocketConsumer):
    """
    处理消息页面的WebSocket连接
    """
    async def connect(self):
        """
        建立WebSocket连接时的处理逻辑
        """

        # 获取当前用户ID
        self.user_id = self.scope["url_route"]["kwargs"]["user_id"]
        # 创建用户特定的组名
        self.room_group_name = f"message_{self.user_id}"
        
        # 将连接加入到组中
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        """
        断接WebSocket连接时的处理逻辑
        """
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )
    
    async def receive(self, text_data):
        """
        接收来自WebSocket客户端的消息
        """
        # 当前实现中，客户端不需要发送消息到服务器
        pass
    
    async def message_update(self, event):
        """
        处理来自频道层的消息更新事件
        """
        print("consumers: message_update", event)

        message = event["data"]
        # 发送消息到WebSocket客户端
        await self.send(text_data=json.dumps(message))
