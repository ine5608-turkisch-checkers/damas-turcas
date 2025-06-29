from typing import Optional, List
from exceptions import PromotionError, PieceNotLinkedToPositionError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from position import Position

class Piece:
    def __init__(self):
        self._position = None
        self._is_king: bool = False 
        self._captured: bool = False

    def associate_position(self, position):
        self._position = position
        retorno = position.associate_piece(self)
        return retorno

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, position):
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
