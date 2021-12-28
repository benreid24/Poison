import json

from django.core.exceptions import BadRequest

from .models import GameAction


def exception_catcher(f):
    def wrapper(*args):
        try:
            f(*args)
        except KeyError as e:
            raise BadRequest(f'Missing required field: {e}')
        except json.decoder.JSONDecodeError:
            raise BadRequest('Malformed json')
    return wrapper


class CreatePlayerRequest:
    @exception_catcher
    def __init__(self, blob):
        #type: (str) -> None
        parsed = json.loads(blob)
        if isinstance(parsed['name'], str):
            self.name = parsed['name']
        else:
            raise BadRequest('name must be a string')


class CreateGameRequest:
    @exception_catcher
    def __init__(self, blob):
        #type: (str) -> None
        parsed = json.loads(blob)
        self.player_id = parsed['player_id']


class JoinGameRequest:
    @exception_catcher
    def __init__(self, blob):
        #type: (str) -> None
        parsed = json.loads(blob)
        self.player_id = parsed['player_id']
        self.game_id = parsed['game_id']

    
class StartGameRequest:
    @exception_catcher
    def __init__(self, blob):
        #type: (str) -> None
        parsed = json.loads(blob)
        self.player_id = parsed['player_id']
        self.game_id = parsed['game_id']


class PollGameRequest:
    @exception_catcher
    def __init__(self, blob):
        #type: (str) -> None
        parsed = json.loads(blob)
        self.player_id = parsed['player_id']
        self.game_id = parsed['game_id']


class PerformActionRequest:
    @exception_catcher
    def __init__(self, blob):
        #type: (str) -> None
        parsed = json.loads(blob)
        self.player_id = parsed['player_id']
        self.game_id = parsed['game_id']
        kind = parsed['type'] # type: int
        if kind not in GameAction.Type:
            raise BadRequest(f'Invalid action type: {kind}')
        self.kind = GameAction.Type(kind)
        self.params = parsed['params']
