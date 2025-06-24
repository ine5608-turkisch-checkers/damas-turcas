from typing import Optional, List
from player import Player
from position import Position
from exceptions import PromotionError, PieceNotLinkedToPositionError

class Piece():
    def __init__(self, player: Optional[Player] = None, position: Optional[Position] = None):
        self._player: Optional[Player] = player
        self._position: Optional[Position] = position
        self._is_king: bool = False 
        self._captured: bool = False

    @property
    def player(self) -> Player:
        return self._player

    @player.setter
    def player(self, player: Optional[Player]) -> None:
        if player is not None and not isinstance(player, Player):
            raise TypeError(f"Player should be instance of Player. Instead, player is: {type(player)}")
        self._player = player

    @property
    def position(self) -> Optional[Position]:
        return self._position

    @position.setter
    def position(self, position: Optional[Position]) -> None:
        if position is not None and not isinstance(position, Position):
            raise TypeError(f"Position should be instance of Position. Instead, position is: {type(position)}")
        self._position = position

    @property
    def is_king(self) -> bool:
        return self._is_king
    
    def detach_piece(self) -> None:
        ...

    def promote_piece(self) -> None:
        if self._is_king:
            raise PromotionError("Error: Piece is already a king.")
        else:
            self._is_king = True

    def get_coordinate(self) -> List[int]:
        """Retorna coordenadas da posição em formato de lista"""
        if self._position is None:
            raise PieceNotLinkedToPositionError("Error: Piece is not linked to position.")
        return self._position.get_coordinate
