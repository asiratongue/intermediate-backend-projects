import json
from channels.generic.websocket import AsyncWebsocketConsumer
from urllib.parse import parse_qs
from .models import Game
from asgiref.sync import sync_to_async, SyncToAsync
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken
from urllib.parse import parse_qs
from django.contrib.auth import get_user_model
from django_redis import get_redis_connection
from channels.db import database_sync_to_async


class BrowserConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.redis_conn = get_redis_connection('default')

    async def connect(self):
        try:
            query_string = parse_qs(self.scope['query_string'].decode())
            token = query_string.get('token', [None])[0]

            if not token:
                await self.send(json.dumps({"error": "you are not authenticated","status": 401}))
                await self.close()
                return 
            
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            self.user = await self.get_user(user_id)
            await self.setup_rankings()

            await self.channel_layer.group_add("GlobalLeaderboard", self.channel_name)
            await self.accept()
            await self.send_leaderboard_update()

        except Exception as e:
            print(f"WebSocket connection error: {str(e)}")
            await self.close()

    @database_sync_to_async
    def setup_rankings(self):
        redis_key_list_wins = []
        redis_key_list_losses = []

        # Get all games and build Redis key lists
        for game in Game.objects.all():
            game_key = f"{game.name}:{game.id}"
            redis_key_list_wins.append(game_key + ":total_wins")
            redis_key_list_losses.append(game_key + ":total_losses")

        # Create global rankings if there are games
        if redis_key_list_wins:
            # Combine all win counts
            self.redis_conn.zunionstore("global_win_rankings", redis_key_list_wins)
            # Combine all loss counts
            self.redis_conn.zunionstore("global_loss_rankings", redis_key_list_losses)

            # Calculate winrates for each player
            for member, wins in self.redis_conn.zscan_iter("global_win_rankings"):
                losses = self.redis_conn.zscore("global_loss_rankings", member) or 0
                winrate = wins / (wins + losses) * 100 if (wins + losses) > 0 else 0
                self.redis_conn.zadd("global_winrate_rankings", {member: winrate})


    async def get_user(self, user_id):
        from channels.db import database_sync_to_async
        
        @database_sync_to_async
        def get_user_by_id(uid):
            return get_user_model().objects.get(id=uid)
            
        return await get_user_by_id(user_id)        


    async def disconnect(self, code):
        await self.channel_layer.group_discard("GlobalLeaderboard", self.channel_name)

    async def send_leaderboard_update(self, event=None):
        leaderboard = self.redis_conn.zrevrange("global_win_rankings", 0, -1, withscores= True)     
        leaderboard_data = [{"rank" : rank, "username": str(user.decode().split(":")[0]), "score" : int(score)} for rank, (user, score) in enumerate(leaderboard, 1)]
        await self.send(text_data=json.dumps({"type" : "leaderboard.update", "timestamp" : str(timezone.now()), "data" : leaderboard_data}))

        
    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json["message"]

            if not self.is_valid_message(text_data):
                await self.send(json.dumps({"error" : "invalid message format", "status" : 400}))
                return
            
            await self.channel_layer.group_send("GlobalLeaderboard", {"type" : "retrieve.leaderboard", "message" : message})

        except json.JSONDecodeError:
            await self.send(json.dumps({"error": "Invalid JSON format","status": 400}))

        except Exception as e:
            await self.send(json.dumps({"error": "Internal server error","status": 500}))


    async def retrieve_leaderboard(self, event):
        message = event["message"]

        if message == "winrate":
            winrate_leaderboard = self.redis_conn.zrevrange("global_winrate_rankings", 0, -1, withscores=True)
            winrate_leaderboard_data = [{"rank" : rank, "username": str(user.decode().split(":")[0]), "winrate" : str(score)+"%"} for rank, (user, score) in enumerate(winrate_leaderboard, 1)]
            await self.send(text_data=json.dumps({f"Here is the global winrate scoreboard as of {timezone.now()}" : winrate_leaderboard_data}))
        
        elif message == "wins":
            wins_leaderboard = self.redis_conn.zrevrange("global_win_rankings", 0, -1, withscores=True)
            wins_leaderboard_data = [{"rank" : rank, "username": str(user.decode().split(":")[0]), "total wins" : int(score)} for rank, (user, score) in enumerate(wins_leaderboard, 1)]
            await self.send(text_data=json.dumps({f"Here is the global wins scoreboard as of {timezone.now()}" : wins_leaderboard_data}))

        else:
            await self.send(json.dumps({"error" : "invalid command, you must either write 'wins' or 'winrate'", "status" : 400}))

    def is_valid_message(self, message):
        try:
            if not message or (not isinstance(message, str) and not isinstance(message, dict)):
                return False            
            
            return True
        except Exception:
            return False
        
        #maybe make this more robust.