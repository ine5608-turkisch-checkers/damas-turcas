from typing import Optional, List
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from position import Position
from exceptions import PromotionError, UnlinkedPieceError, CaptureError

class Piece:
    def __init__(self):
        """Inicializa a classe piece a partir do player. Inicialmente não é associado a uma posição"""
        self._position = None
        self._is_king: bool = False
        self._is_captured: bool = False

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, position):
        if position is not None and not isinstance(position, Position):
            raise TypeError("Position must be a Position instance")
        
        # Desvincula da posição anterior
        if self._position is not None and self._position.piece is self:
            self._position._piece = None

        self._position = position

        if position is not None and position.piece is not self:
            position.piece = self
    
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

    def associate_position(self, position):
        self._position = position
        retorno = position.associate_piece(self)
        return retorno