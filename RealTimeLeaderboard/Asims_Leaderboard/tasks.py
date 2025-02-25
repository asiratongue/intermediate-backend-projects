from django.contrib.auth import get_user_model
import redis
from .models import UserGameProfile, Game

redis_client = redis.Redis(host= 'localhost', port=6379, db=0)

def populate_redis_scores():

    try:
        games = Game.objects.all()
        total_scores = 0

        for game in games:
            user_game_profile = UserGameProfile.objects.select_related('user').filter(game=game)
            game_key = f"{game.name}:{game.id}"

            for profile in user_game_profile:
                member = f"{profile.user.username}:{profile.user.id}"
                winrate = (profile.wins) / (profile.wins + profile.losses) * 100

                redis_client.zadd(game_key + ":winrate", {member: winrate})
                redis_client.zadd(game_key + ":total_wins",{member : profile.wins} )

            total_scores += user_game_profile.count()
            print(f"Populated {user_game_profile.count()} scores for game {game.id}")

        print(f"Successfully populated {total_scores} across {games.count()} games")
    except Exception as e:
        print(f"error populating scores: {str(e)}")


def populate_losses():

    try:
        games = Game.objects.all()
        total_scores = 0

        for game in games:
            user_game_profile = UserGameProfile.objects.select_related('user').filter(game=game)
            game_key = f"{game.name}:{game.id}"

            for profile in user_game_profile:
                member = f"{profile.user.username}:{profile.user.id}"
                
                redis_client.zadd(game_key + ":total_losses",{member : profile.losses} )

            total_scores += user_game_profile.count()
            print(f"Populated {user_game_profile.count()} scores for game {game.id}")  

    except Exception as e:
        print(f"error populating scores: {str(e)}")


