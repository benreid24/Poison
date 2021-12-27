from django.core.exceptions import BadRequest
from django.http import HttpRequest, HttpResponse, JsonResponse

from .messages import CreateGameRequest, CreatePlayerRequest, JoinGameRequest, PollGameRequest, StartGameRequest
from .models import Game, Player
from . import game


def index(request):
    # type: (HttpRequest) -> HttpResponse
    return HttpResponse("Web-app here")


def create_player(request):
    # type: (HttpRequest) -> JsonResponse

    req = CreatePlayerRequest(request.body)
    player = Player(name=req.name)
    player.save()

    return JsonResponse({'id': player.key})


def create_game(request):
    # type: (HttpRequest) -> JsonResponse

    req = CreateGameRequest(request.body)
    g = game.create_game(req.player_id)
    
    return JsonResponse(game.encode_game(g, req.player_id))


def join_game(request):
    # type: (HttpRequest) -> JsonResponse

    req = JoinGameRequest(request.body)
    g = game.join_game(req.game_id, req.player_id)
    return JsonResponse(game.encode_game(g, req.player_id))


def start_game(request):
    # type: (HttpRequest) -> JsonResponse

    req = StartGameRequest(request.body)
    g = game.start_game(req.game_id, req.player_id)
    return JsonResponse(game.encode_game(g, req.player_id))


def poll_game(request):
    # type: (HttpRequest) -> JsonResponse

    req = PollGameRequest(request.body)
    try:
        g = Game.objects.get(pk=req.game_id)
    except Exception:
        raise BadRequest(f'Bad game id: {req.game_id}')

    return JsonResponse(game.encode_game(g, req.player_id))


def perform_action(request):
    # type: (HttpRequest) -> JsonResponse
    return JsonResponse({})
