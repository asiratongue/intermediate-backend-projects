from django.urls import path
from . import views

urlpatterns = [
    path('view/<int:id>/', views.ViewMovies.as_view(), name='ViewMovie'),
    path('viewall/', views.ViewAllMovies.as_view(), name='ViewAllMovies'),
    path('reserve/<int:id>/', views.ReserveMovie.as_view(), name='ReserveMovie'),
    path('cancel/<int:id>/', views.CancelReservation.as_view(), name='cancel'),
    path('viewscreenings/', views.ViewScreenings.as_view(), name = 'ViewScreenings'),
    path('viewtickets/', views.ViewTickets.as_view(), name = 'ViewTickets'),
    path('viewavailable/<int:id>/', views.ViewSeatsAvailable.as_view(), name='AvailableSeats'),
    path('report/all/', views.ReportAll.as_view(), name = 'Report'),
    path('report/<int:id>/', views.ReportMovieScreening.as_view(), name = 'Reserve')

]
 