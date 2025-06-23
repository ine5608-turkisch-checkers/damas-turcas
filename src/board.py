from typing import Optional, List

from player import Player
from game_status import GameStatus
from position import Position

BOARD_SIZE = 8

class Board():
    def __init__(self, player1: Player, player2: Player):
        self._positions: List[List[Position]] = [
            [Position(row,col) for col in range(BOARD_SIZE)]
            for row in range(BOARD_SIZE)
        ]
        self._player1: Player = player1
        self._player2: Player = player2
        self._game_status: int = GameStatus.NO_MATCH.value
        self._winner: Optional[Player] = None

        self._selected_position: Optional[Position] = None
        self._received_move: Optional[dict] = None

    @property
    def player1(self) -> Player:
        return self._player1

    @player1.setter
    def player1(self, player1: Player) -> None:
        if not isinstance(player1, Player):
            raise TypeError("Player 1 must be a Player")
        self._player1 = player1

    @property
    def player2(self) -> Player:
        return self._player2
    
    @player2.setter
    def player2(self, player2: Player) -> None:
        if not isinstance(player2, Player):
            raise TypeError("Player 2 must be a Player")
        self._player2 = player2

    @property
    def game_status(self) -> int:
        return self._game_status

    @game_status.setter
    def game_status(self, status: int) -> None:
        if status in [s.value for s in GameStatus]:
            self._game_status = status
        else:
            raise ValueError(f"Invalid game status: {status}")

    @property
    def winner(self) -> Optional[Player]:
        return self._winner

    @winner.setter
    def winner(self, winner: Optional[Player]) -> None:
        if winner is not None and not isinstance(winner, Player):
            raise TypeError("Winner must be a Player or None")
        self._winner = winner

    @property
    def selected_position(self) -> Optional[Position]:
        return self._selected_position

    @selected_position.setter
    def selected_position(self, selected_position: Optional[Position]) -> None:
        if selected_position is not None and not isinstance(selected_position, Position):
            raise TypeError("Selected position must be a Position or None")
        self._selected_position = selected_position

    @property
    def received_move(self) -> Optional[dict]:
        return self._received_move

    @received_move.setter
    def received_move(self, received_move: Optional[dict]) -> None:
        if received_move is not None and not isinstance(received_move, dict):
            raise TypeError("Received move must be a dictionary or None")
        self._received_move = received_move
