from django.core.exceptions import BadRequest
from django.http import HttpRequest, HttpResponse, JsonResponse

from .exceptions import PoisonException
from .messages import (
    CreateGameRequest,
    CreatePlayerRequest,
    JoinGameRequest,
    PollGameRequest,
    StartGameRequest
)
from .models import Game, Player
from . import game


def error_handler(f):
    def wrapper(*args):
        try:
            return f(*args)
        except PoisonException as e:
            return e.to_response()
    return wrapper


def index(request):
    # type: (HttpRequest) -> HttpResponse
    return HttpResponse("Web-app here")


@error_handler
def create_player(request):
    # type: (HttpRequest) -> JsonResponse

    req = CreatePlayerRequest(request.body)
    player = Player(name=req.name)
    player.save()

    return JsonResponse({'id': player.key})


@error_handler
def create_game(request):
    # type: (HttpRequest) -> JsonResponse

    req = CreateGameRequest(request.body)
    g = game.create_game(req.player_id)
    
    return JsonResponse(game.encode_game(g, req.player_id))


@error_handler
def join_game(request):
    # type: (HttpRequest) -> JsonResponse

    req = JoinGameRequest(request.body)
    g = game.join_game(req.game_id, req.player_id)
    return JsonResponse(game.encode_game(g, req.player_id))


@error_handler
def start_game(request):
    # type: (HttpRequest) -> JsonResponse

    req = StartGameRequest(request.body)
    g = game.start_game(req.game_id, req.player_id)
    return JsonResponse(game.encode_game(g, req.player_id))


@error_handler
def poll_game(request):
    # type: (HttpRequest) -> JsonResponse

    req = PollGameRequest(request.body)
    try:
        g = Game.objects.get(pk=req.game_id)
    except Exception:
        raise BadRequest(f'Bad game id: {req.game_id}')

    return JsonResponse(game.encode_game(g, req.player_id))


@error_handler
def perform_action(request):
    # type: (HttpRequest) -> JsonResponse
    return JsonResponse({})
