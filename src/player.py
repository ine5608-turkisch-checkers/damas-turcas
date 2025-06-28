from typing import Optional, List

from piece import Piece

MAX_NUMBER_OF_PIECES = 16

class Player():
    def __init__(self, id: int, name: str, is_black: bool, is_its_turn: bool) -> None:
        self._id: int = id
        self._name:str = name
        self._is_black:bool = is_black
        self._is_its_turn: bool = is_its_turn
        self._is_winner: bool = False
        self._pieces: List[Piece] = [Piece(self) for _ in range(MAX_NUMBER_OF_PIECES)] #Diagrama de sequência Initialize: Player instancia as suas peças sem posição 

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
