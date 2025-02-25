from django.urls import path
from . import views

app_name = 'RealTimeLeaderboard'

urlpatterns = [
    path('viewgames/', views.ViewGames.as_view(), name='ViewGames'),
    path('submit/<int:id>/', views.SubmitGameScore.as_view(), name='Submit'),
    path('view/global/score/', views.GlobalRanking.as_view(), name='ViewGlobalScore'),
    path('view/game/<int:id>/score/', views.SelectedGameRanking.as_view(), name='ViewSelectedGameRanking'),
    path('view/report/all/', views.TopPlayersAllGames.as_view(), name='ViewGlobalLeaderboard'), #time period queries!
    path('view/report/<int:id>/', views.TopPlayersSelectedGame.as_view(), name='ViewSelectedLeaderboard'), #time period queries!
    
]
