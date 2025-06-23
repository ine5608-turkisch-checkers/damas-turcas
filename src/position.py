from typing import Optional
from piece import Piece

class Position():
    def __init__(self, row, col):
        self._row: int = row
        self._col: int = col
        self._occupied: bool = False
        self._piece: Optional[Piece] = None

    @property
    def row(self) -> int:
        return self._row
    
    @row.setter
    def row(self, row: int):
        if not isinstance(row, int):
            raise TypeError(f"Row should be instance of int. Instead, row is: {type(row)}")
        self._row = row

    @property
    def col(self) -> int:
        return self._col
    
    @col.setter
    def col(self, col: int):
        if not isinstance(col, int):
            raise TypeError(f"Column should be instance of int. Instead, column is: {type(col)}")
        self._col = col

    @property
    def occupied(self) -> bool:
        return self._occupied
    
    # Esse método não faz muito sentido. É possível deixar desocupado e ainda sim ter uma peça associada.
    # Melhor seria só ter um método "is_occupied que verifica se self.piece é None ou nao"
    def toggle_occupied(self):
            self._occupied =  not self._occupied

    @property
    def piece(self) -> Piece:
        return self._piece
    
    @piece.setter
    def piece(self, piece: Optional[Piece]) -> None:
        if piece is not None and not isinstance(piece, Piece):
            raise TypeError(f"piece should be instance of Piece. Instead, piece is: {type(piece)}")
        self._occupied = True
        self._piece = piece
