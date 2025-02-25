from django.db import models
from Users.models import CustomUser
from simple_history.models import HistoricalRecords
# Create your models here.


class Game(models.Model):
    name = models.CharField(max_length=50, null=True)
    description = models.CharField(max_length=500, null=True)

    def __str__(self):
        return self.name  

class UserGameProfile(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, default=1)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, default=1)
    wins = models.PositiveIntegerField(default=0)
    losses = models.PositiveIntegerField(default=0)
    history = HistoricalRecords(
        history_user_id_field=models.IntegerField(null=True)
    )



    class Meta:
        constraints = [models.UniqueConstraint(fields = ['user', 'game'], name='unique_game')]

    @property
    def winrate(self):
        percentage = (self.wins) / (self.wins + self.losses) * 100
        return str(percentage) + "%"

    def __str__(self):
        return f'{self.user.username} {self.game.name}' 


