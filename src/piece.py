from typing import Optional, List
from player import Player
from position import Position
from exceptions import PromotionError, UnlinkedPieceError, CaptureError

class Piece():
    def __init__(self, player: Player, position: Optional[Position] = None):
        """Inicializa a classe piece a partir do player. Inicialmente não é associado a uma posição"""

        self._player: Player = player
        self._position: Optional[Position] = position
        self._is_king: bool = False
        self._is_captured: bool = False

    @property
    def player(self) -> Player:
        return self._player

    # Provavelmente isto está errado
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
    
    def detach_position(self) -> None:
        """Desvincula peça da posição"""

        if self._position is not None:
            pos = self._position
            self._position = None
            pos._piece = None #Desvincula tanto no Piece, quanto no Position

    @property
    def is_king(self) -> bool:
        return self._is_king

    def promote_piece(self) -> None:
        """Promove a peça se ainda não foi promovida"""

        if self._is_king:
            raise PromotionError("Error: Piece is already a king.")
        else:
            self._is_king = True
    
    @property
    def is_captured(self) -> bool:
        return self._is_captured

    def toggle_is_captured(self) -> None:
        """Troca o estado de captura da peça se a peça não está capturada"""

        if self.is_captured is True:
            raise CaptureError("Error: Piece is already captured")
        else:
            self._is_captured = True

    @property
    def coordinates(self) -> List[int]:
        """Retorna coordenadas da posição em formato de lista"""
        if self._position is None:
            raise UnlinkedPieceError("Error: Piece is not linked to position.")
        return self._position.coordinates
