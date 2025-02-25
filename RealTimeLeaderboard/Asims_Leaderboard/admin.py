from django.contrib import admin
from Users.models import CustomUser
from Asims_Leaderboard.models import Game, UserGameProfile
# Register your models here.

class RevenueAdmin(admin.ModelAdmin): 
    
    def has_view_permission(self, request, obj=None):
        return request.user.is_staff or request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser
    

admin.site.register(Game)
admin.site.register(UserGameProfile)