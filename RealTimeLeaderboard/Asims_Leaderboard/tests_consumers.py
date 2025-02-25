from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from unittest.mock import patch
from django.db import transaction, connections
from .consumers import BrowserConsumer
from django_redis import get_redis_connection
from channels.testing import WebsocketCommunicator
from rest_framework.test import APIClient
from django.test import TransactionTestCase
import json
from asyncio.exceptions import TimeoutError
from unittest.mock import MagicMock, patch



class TestBrowserConsumer(TransactionTestCase):

    def setUp(self):
        for conn in connections.all():
            conn.close()

    async def asyncsetUp(self):

        @database_sync_to_async
        def setup_user_and_token():
            with transaction.atomic():
                client = APIClient()
                user = get_user_model().objects.create_user(username='testuser', password='testpass123') 
                login = client.post('/AsimsLeaderboard/login/', {'username': 'testuser', 'password': 'testpass123'}, format='json')
                token = login.data['tokens']['access']
                return user, token, client
        
        self.user, self.token, self.client = await setup_user_and_token()

        self.redis_conn = get_redis_connection("default")     

        @database_sync_to_async
        def delete_all_sorted_sets():
            for key in self.redis_conn.scan_iter("*"):
                if self.redis_conn.type(key) == b'zset':
                    self.redis_conn.delete(key)

        await delete_all_sorted_sets()
        self.channel_layer = get_channel_layer()

    async def test_connect(self):
        await self.asyncsetUp()
        communicator = WebsocketCommunicator(BrowserConsumer.as_asgi(), f"/ws/?token={self.token}")
        communicator.scope["user"] = self.user

        try:
            connected, _ = await communicator.connect()
            self.assertTrue(connected)

            response = await communicator.receive_json_from()
            self.assertEqual(response["type"], "leaderboard.update")
            self.assertIsInstance(response["data"], list)

        finally:
            await communicator.disconnect()

    async def asyncTearDown(self):
        await database_sync_to_async(self.delete_all_sorted_sets())


    @patch('Asims_Leaderboard.consumers.BrowserConsumer.get_user')
    @patch('Asims_Leaderboard.consumers.BrowserConsumer.setup_rankings')
    @patch('Asims_Leaderboard.consumers.BrowserConsumer.is_valid_message')
    @patch('Asims_Leaderboard.consumers.BrowserConsumer.retrieve_leaderboard')
    @patch('django_redis.get_redis_connection')
    async def test_BrowserInvalidMessages(self, mock_is_valid_message, mock_retrieve_leaderboard, mock_setup_rankings, mock_get_user, mock_redis_connection):
        await self.asyncsetUp()
        mock_is_valid_message.return_value = False
        mock_get_user.return_value = None
        mock_setup_rankings.return_value = None

        mock_redis = MagicMock()
        mock_redis.zrevrange.return_value = [(b"player1:1", 100),(b"player2:2", 50)]

        mock_redis_connection.return_value = mock_redis
        
        communicator = WebsocketCommunicator(BrowserConsumer.as_asgi(), f"/ws/?token={self.token}")

        try:
            connected, _ = await communicator.connect()
            self.assertTrue(connected)
            print("Connected successfully")

            initial_update = await communicator.receive_json_from()
            print("Initial response:", initial_update)
            self.assertIn("type", initial_update)
            self.assertEqual(initial_update["type"], "leaderboard.update")

            await communicator.send_to(text_data="hello")            
            response2 = await communicator.receive_json_from()
            print("Response to invalid text:", response2)
            self.assertIn("error", response2)
            self.assertEqual(response2["status"], 400)

        
            await communicator.send_json_to({"message" : "hello"})       
            response3 =  await communicator.receive_json_from()
            print("Got response3:", response3)

            self.assertIn("error", response3)
            self.assertEqual(response3["status"], 400)

        finally:
            await communicator.disconnect()
        

    async def asyncTearDown(self):
        for conn in connections.all():
            conn.close()

    async def test_BrowserNoJWT(self):

        await self.asyncsetUp()
        communicator = WebsocketCommunicator(BrowserConsumer.as_asgi(), f"/ws/?token=InvalidToken")

        try:
            connected, _ = await communicator.connect()
            self.assertFalse(connected)

        finally:
            await communicator.disconnect()

    async def test_RetrieveLeaderboards(self):

        await self.asyncsetUp()
        communicator = WebsocketCommunicator(BrowserConsumer.as_asgi(), f"/ws/?token={self.token}")

        try:
            connected, _ = await communicator.connect()
            response1 = await communicator.receive_json_from()
            

            await communicator.send_json_to({"message" : "wins"})
            response2 = await communicator.receive_json_from()
            await communicator.send_json_to({"message" : "winrate"})
            response3 = await communicator.receive_json_from()
            self.assertIn('Here is the global winrate scoreboard', list(response3.keys())[0])
            self.assertIn('Here is the global wins scoreboard', list(response2.keys())[0])

        finally:
            await communicator.disconnect()



#python manage.py test Asims_Leaderboard.tests.EndpointTests.test_submit_concurrently --keepdb
