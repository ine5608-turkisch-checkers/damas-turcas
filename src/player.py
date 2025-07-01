from typing import List
from piece import Piece

class Player:
    def __init__(self):
        self._id: int = 0
        self._name:str = ""
        self._is_black:bool = False
        self._is_its_turn: bool = False
        self._is_winner: bool = False
        self._pieces: List[Piece] = [Piece() for _ in range(16)] #Diagrama de sequência Initialize: Player instancia as suas peças sem posição

    def reset(self):
        self.id = 0
        self.name = ""
        self._is_winner = False

    @property
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, id: int) -> None:
        self._id = id

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name

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

    def associate_piece_position(self, position, num_piece):
        piece = self._pieces[num_piece]
        piece.associate_position(position)


