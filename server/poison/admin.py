from django.contrib import admin

from .models import Player, GamePlayer, GameAction, Game

admin.site.register(Player)
admin.site.register(GamePlayer)
admin.site.register(GameAction)
admin.site.register(Game)
