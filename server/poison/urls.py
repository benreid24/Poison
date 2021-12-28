from django.urls import path

from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('create_player', views.create_player, name='create_player'),
    path('create_game', views.create_game, name='create_game'),
    path('join_game', views.join_game, name='join_game'),
    path('start_game', views.start_game, name='start_game'),
    path('poll_game', views.poll_game, name='poll_game'),
    path('perform_action', views.perform_action, name='perform_action'),
]
