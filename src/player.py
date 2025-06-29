from typing import Optional, List

from piece import Piece

MAX_NUMBER_OF_PIECES = 16

class Player:
    def __init__(self):
        self._id = 0
        self._name = ""
        self._is_black = False
        self._is_its_turn = False
        self._is_winner = False
        self._pieces = [Piece() for i in range(16)] #create_piece()

    def associate_piece_position(self, position, num_piece):
        piece = self._pieces[num_piece]
        piece.associate_position(position)

    @property
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, value: int) -> None:
        self._id = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def is_black(self) -> bool:
        return self._is_black

    @is_black.setter
    def is_black(self, value: bool) -> None:
        self._is_black = value

    @property
    def is_its_turn(self) -> bool:
        return self._is_its_turn
    
    @is_its_turn.setter
    def is_its_turn(self, value: bool) -> None:
        self._is_its_turn = value

    def toggle_turn(self) -> None:
        self._is_its_turn = not self._is_its_turn

    @property
    def is_winner(self) -> bool:
        return self._is_winner

    @is_winner.setter
    def is_winner(self, value: bool) -> None:
        self._is_winner = value

    @property
    def pieces(self) -> List[Piece]:
        return self._pieces

    @pieces.setter
    def pieces(self, new_pieces: List[Piece]) -> None:
        if len(new_pieces) != MAX_NUMBER_OF_PIECES:
            raise ValueError(f"Player must start with exactly {MAX_NUMBER_OF_PIECES} pieces.")
        if not all(isinstance(p, Piece) for p in new_pieces):
            raise TypeError("All pieces must be instances of Piece.")
        self._pieces = new_pieces
