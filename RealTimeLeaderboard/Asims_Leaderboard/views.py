from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status 
from django.contrib.auth.models import User
from .models import Game, UserGameProfile
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from django.db.models import Count, Max, Sum
from Users.models import CustomUser
from .utils import rank_calc, get_filtered_history, validate_dates, calculate_player_stats, create_leaderboards, generate_leaderboard_response
import redis
from django.utils import timezone
from datetime import datetime


r = redis.Redis(host="localhost", port = 6379, db=0)

class ViewGames(APIView):
    model = Game
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]


    def get(self, request):     
        all_games = Game.objects.all()

        if not all_games:
            return Response({"error" : "no games were found!"}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({"message" : "here are all games currently being played",
                            "games" : [["id", game.id, game.name, game.description] for game in all_games]}, status=status.HTTP_200_OK)



class SubmitGameScore(APIView):

    model = Game
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
            

    def post(self, request, id):

        def validate_scores(request):
            if not isinstance(request, int):
                return Response({"error" : "check your request data, only integers are allowed!"}, 
                                            status=status.HTTP_400_BAD_REQUEST)
            if request >= 100 or request <= 0:
                return Response({"error" : "check your request data, you can only submit up to 100 games at a time!"}, 
                                            status=status.HTTP_400_BAD_REQUEST)
            else:
                return
    
        try:
            profile = request.user
            game_to_update = Game.objects.get(pk = id)
            try:
                wins = request.data["score"]["wins"]
                losses = request.data["score"]["losses"]
            except KeyError as e:
                return Response({f"error {e}" : "you have mispelt your header! it must be named 'score'"}, status=status.HTTP_400_BAD_REQUEST)
            
            def game_score(request, user):
                game_profile, created = UserGameProfile.objects.get_or_create(game = game_to_update, user = user)
                x = validate_scores(request[1])

                if isinstance(x, Response):
                    return x
                
                if "wins" in request:                    
                    game_profile.wins += request[1] 

                if "losses" in request:
                    game_profile.losses += request[1]

                game_profile.save()
                return(game_profile)
                    
            for item in request.data["score"].items():
                game_profile_new = game_score(item, profile)

                if isinstance(game_profile_new, Response):
                    return game_profile_new

            sorted_set_title = f"{game_to_update.name}:{game_to_update.id}"
            sorted_set_member = f"{profile.username}:{profile.id}"

            r.zincrby(sorted_set_title+":total_wins", wins, sorted_set_member)
            r.zincrby(sorted_set_title+":total_losses", losses, sorted_set_member)
            
            return Response({f"message for {profile.username}": f"You have successfully updated your game score for {game_profile_new.game.name}! "
                                        f"New wins: {game_profile_new.wins}, new losses: {game_profile_new.losses}, "
                                        f"new win rate = {game_profile_new.winrate}%"}, status=status.HTTP_200_OK)

        except (Game.DoesNotExist, KeyError) as e:
            return Response ({"error" : f"{e}"}, status= status.HTTP_400_BAD_REQUEST)


class GlobalRanking(APIView):
    model = UserGameProfile
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]


    def get(self, request):
        try:
            asking_user = request.user
            all_users = CustomUser.objects.filter(is_superuser=False)

    

            win_dict = {}
            winrate_dict = {}

            for user in all_users:
                user_stats = UserGameProfile.objects.filter(user = user).aggregate(total_wins = Sum('wins', distinct=True), total_losses = Sum('losses', distinct=True))

                if user_stats['total_wins'] is None and user_stats['total_losses'] is None:
                   continue
                 
                user_stats["global_winrate"] = (user_stats["total_wins"]) / (user_stats["total_wins"] + user_stats["total_losses"]) * 100
                print(user_stats)

                win_dict[user.username] = user_stats["total_wins"]
                winrate_dict[user.username] = user_stats["global_winrate"]

            if asking_user.username not in win_dict:
                return Response({"error" : "you have no games logged, go play!"}, status=status.HTTP_400_BAD_REQUEST)
            
            ranks = rank_calc(win_dict, winrate_dict, asking_user)

            return Response({f"message for {asking_user.username}" : f"you have a total score of {ranks[2][asking_user.username]}, with a global winrate of {ranks[3][asking_user.username]}."
  f" this places you at number {ranks[0]} for global score, and at number {ranks[1]} for winrate, keep going !"}, status=status.HTTP_200_OK)
        
        except User.DoesNotExist:
            return Response({"error" : "could not find a user"}, status=status.HTTP_404_NOT_FOUND)


class SelectedGameRanking(APIView):
    model = UserGameProfile
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def get(self, request, id):

        try:
            asking_user = request.user
            game = Game.objects.get(pk = id)
            all_users = UserGameProfile.objects.filter(game = game)

            if not UserGameProfile.objects.filter(game = game, user = asking_user).exists():
                return Response ({"error" : f"you have no scored logged for {game.name} yet, go play!"}, status=status.HTTP_400_BAD_REQUEST)
            
            winrate_dict = {}
            win_dict = {}

            for user in all_users:
                win_dict[user.user.username] = user.wins
                winrate_dict[user.user.username] = user.winrate

            ranks = rank_calc(win_dict, winrate_dict, asking_user)

            return Response({f"message for {asking_user.username}" : f"""for the game of {game.name}, you have a total score of {ranks[2][asking_user.username]}, with a winrate of {ranks[3][asking_user.username]}
  this places you at number {ranks[0]} for global score, and at number {ranks[1]} for winrate, keep going !"""}, status=status.HTTP_200_OK)

        except Game.DoesNotExist:
            return Response ({"error" : "could not find any games matching id - check your id?"}, status=status.HTTP_404_NOT_FOUND)

class TopPlayersAllGames(APIView):
    model = UserGameProfile
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def get(self, request):
        date_from, date_to, error_response = validate_dates(request.GET.get('datefrom'), request.GET.get('dateto'))

        if error_response:
            return error_response
        try:
            all_game_profiles = UserGameProfile.objects.all()
        except UserGameProfile.DoesNotExist:
            return Response({"error": "No UserGameProfiles have been found"}, status=status.HTTP_404_NOT_FOUND)

        return generate_leaderboard_response(all_game_profiles, date_from, date_to, r)


class TopPlayersSelectedGame(APIView):
    model = UserGameProfile
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def get(self, request, id):
        date_from, date_to, error_response = validate_dates(request.GET.get('datefrom'),request.GET.get('dateto'))

        if error_response:
            return error_response

        try:
            game = Game.objects.get(pk=id)
            selected_game_profiles = UserGameProfile.objects.filter(game=game)
            return generate_leaderboard_response(selected_game_profiles, date_from, date_to, r,game.name)
        except Game.DoesNotExist:
            return Response({"error": "Game not found"}, status=status.HTTP_404_NOT_FOUND)
        
        

