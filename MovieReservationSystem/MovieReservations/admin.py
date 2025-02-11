from django.contrib import admin
from Users.models import CustomUser
from MovieReservations.models import Transaction, Movie, MovieScreening, Genre, Revenue
from django.db import models
from django.forms import Textarea


     
class RevenueAdmin(admin.ModelAdmin): 
    
    def has_view_permission(self, request, obj=None):
        return request.user.is_staff or request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser
    
    formfield_overrides = {
    models.TextField: {'widget': Textarea(attrs={'rows': 10, 'cols': 80})},
}

admin.site.register(Transaction)
admin.site.register(CustomUser)
admin.site.register(Revenue, RevenueAdmin)
admin.site.register(Movie)
admin.site.register(MovieScreening)
admin.site.register(Genre)
