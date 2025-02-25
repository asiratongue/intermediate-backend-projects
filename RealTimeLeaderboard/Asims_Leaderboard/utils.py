from django.utils import timezone
from datetime import datetime
from rest_framework.response import Response
from rest_framework import status
from django_redis import get_redis_connection


def get_filtered_history(profile, date_from, date_to):

    return profile.history.filter(
        history_date__gte=date_from,
        history_date__lte=date_to,
        wins__gte=1,
        losses__gte=1
    )


def rank_calc(win_dictx, winrate_dictx, user):

    sorted_win_dict = dict(sorted(win_dictx.items(), key=lambda x: x[1], reverse=True))
    sorted_winrate_dict = dict(sorted(winrate_dictx.items(), key=lambda x: x[1], reverse=True))

    score_rank = list(sorted_win_dict.keys()).index(user.username) + 1
    winrate_rank = list(sorted_winrate_dict.keys()).index(user.username) + 1

    return [score_rank, winrate_rank, sorted_win_dict, sorted_winrate_dict]



def validate_dates(date_from, date_to):
    try:
        date_from = timezone.make_aware(datetime.strptime(date_from, '%Y-%m-%d'))
        date_to = timezone.make_aware(datetime.strptime(date_to, '%Y-%m-%d'))
        max_date = timezone.make_aware(datetime.strptime('2100-01-01', '%Y-%m-%d'))
        min_date = timezone.make_aware(datetime.strptime('1900-01-01', '%Y-%m-%d'))
        
        if date_from == 0 or date_to == 0:
            return None, None, Response(
                {"error": "you must send a query! (format: ?datefrom=yyyy-mm-dd?dateto=yyyy-mm-dd)"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if (date_from >= max_date or date_from <= min_date) or (date_to >= max_date or date_from <= min_date):
                        return None, None, Response(
                {"error": "Date must be between 1900 and 2100"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        return date_from, date_to, None
    except Exception as e:
        return None, None, Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

def calculate_player_stats(historical_records):
    """Calculate wins, losses and winrate for players."""
    wins_dict = {}
    losses_dict = {}
    winrate_dict = {}

    for record in historical_records:
        username = record.user.username
        wins_dict.setdefault(username, 0)
        wins_dict[username] += int(record.wins)
        losses_dict.setdefault(username, 0)
        losses_dict[username] += int(record.losses)

    for wins, losses in zip(wins_dict.items(), losses_dict.items()):
        name = wins[0]
        percentage = (wins[1] / (wins[1] + losses[1])) * 100
        winrate_dict[name] = percentage

    return wins_dict, losses_dict, winrate_dict


def create_leaderboards(redis_client, date_from, date_to, game_name=""):
    """Create and format leaderboards from Redis sorted sets."""
    prefix = f"{date_to}-{date_from}"
    game_prefix = f"_{game_name}" if game_name else ""
    
    wins_key = f"{prefix}{game_prefix}_wins_leaderboard"
    winrate_key = f"{prefix}{game_prefix}_winrate_leaderboard"
    
    wins_leaderboard = [
        f"{rank}) {name.decode()} - {int(score)} wins" for rank, (name, score) in enumerate(redis_client.zrevrange(wins_key, 0, -1, withscores=True), 1)]
    
    winrate_leaderboard = [
        f"{rank}) {name.decode()} - {score:.1f}% winrate" 
        for rank, (name, score) in enumerate(
            redis_client.zrevrange(winrate_key, 0, -1, withscores=True), 1
        )
    ]
    
    return wins_leaderboard, winrate_leaderboard



def generate_leaderboard_response(profiles, date_from, date_to, redis_client, game_name=""):
    """Main function to generate leaderboard data and response."""
    try:
        # Get historical records for all profiles
        all_dates = []
        for profile in profiles:
            history = get_filtered_history(profile, date_from, date_to)
            if history.exists():
                all_dates.extend(history)

        # Calculate player statistics
        wins_dict, losses_dict, winrate_dict = calculate_player_stats(all_dates)

        # Store in Redis
        prefix = f"{date_to}-{date_from}"
        game_prefix = f"_{game_name}" if game_name else ""
        
        redis_client.zadd(f"{prefix}{game_prefix}_wins_leaderboard", wins_dict)
        redis_client.zadd(f"{prefix}{game_prefix}_winrate_leaderboard", winrate_dict)

        # Generate formatted leaderboards
        wins_leaderboard, winrate_leaderboard = create_leaderboards(
            redis_client, date_from, date_to, game_name
        )

        message = f"here are the top ranked players between {date_from} and {date_to}"
        if game_name:
            message += f" for {game_name}"

        return Response({
            "message": message,
            "Top players by wins": wins_leaderboard,
            "Top players by winrate": winrate_leaderboard
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

def duplicate_redis_data_for_testing(source_db = 0, test_db=15):

    source_redis = get_redis_connection('default')

    source_redis.execute_command('SELECT', test_db)

    source_redis.flushdb()

    source_redis.execute_command('SELECT', source_db)


    for key in source_redis.scan_iter():
        key_type = source_redis.type(key)

        if key_type == b'zset':

            members_scores = source_redis.zrange(key, 0, -1, withscores = True)
            if members_scores:
                source_redis.execute_command('SELECT', test_db)
                source_redis.zadd(key, dict(members_scores))
                source_redis.execute_command('SELECT', source_db)
