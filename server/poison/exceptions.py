from django.http import JsonResponse


class PoisonException(Exception):
    def __init__(self, code, message):
        # type: (int, str) -> None
        super().__init__(message)
        self.user_message = message
        self.code = code

    def to_response(self):
        return JsonResponse({
            'code': self.code,
            'message': self.user_message,
        }, status=418)


class GameAlreadStartedException(PoisonException):
    def __init__(self):
        super().__init__(1, 'Game already started')


class GameFullException(PoisonException):
    def __init__(self):
        super().__init__(2, 'Game is full')


class NotInGameException(PoisonException):
    def __init__(self):
        super().__init__(3, 'Not a part of this game')


class NotEnoughPlayersException(PoisonException):
    def __init__(self):
        super().__init__(4, 'Not enough players')


class NotHostException(PoisonException):
    def __init__(self):
        super().__init__(5, 'You are not the host')
