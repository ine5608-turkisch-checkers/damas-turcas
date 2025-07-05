from typing import Optional, List
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from piece import Piece


class Position:
    def __init__(self, row: int, col: int) -> None:
        if not isinstance(row, int) or not isinstance(col, int):
                raise TypeError(f"Row and column must be integer. Instead, row is {type(row)} and column is {type(col)}")
        self._row: int = row
        self._col: int = col
        self._piece: Optional[Piece] = None

    @property
    def row(self) -> int:
        return self._row
    
    @row.setter
    def row(self, row: int) -> None:
        if not isinstance(row, int):
            raise TypeError(f"Row should be instance of integer. Instead, row is: {type(row)}")
        self._row = row

    @property
    def col(self) -> int:
        return self._col
    
    @col.setter
    def col(self, col: int) -> None:
        if not isinstance(col, int):
            raise TypeError(f"Column should be instance of integer. Instead, column is: {type(col)}")
        self._col = col

    @property
    def coordinates(self) -> List[int]:
        """Retorna coordenadas da posição em formato de lista"""

        return [self.row, self.col]

    @property
    def piece(self):
        return self._piece

    @piece.setter
    def piece(self, piece):
        self._piece = piece

    @property
    def is_occupied(self) -> bool:
        """Verifica se a posição está ocupada"""

        return self._piece is not None

    @property
    def is_king(self) -> bool:
        """Verifica se peça associada é dama"""

        return self.piece.is_king if self.is_occupied else False

    def detach_piece(self) -> None:
        """Desvincula posição da peça"""

        if self._piece is not None:
            self._piece.detach_position()

    def associate_piece(self, piece):
        self._piece = piece
        return True