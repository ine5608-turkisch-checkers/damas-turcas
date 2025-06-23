from typing import Optional, List

from piece import Piece

MAX_NUMBER_OF_PIECES = 16

class Player():
    def __init__(self, id: int, name: str, is_black: bool, is_its_turn: bool, pieces: Optional[List[Piece]] = None):
        self._id: int = id
        self._name:str = name
        self._is_black:bool = is_black
        self._is_its_turn: bool = is_its_turn
        self._is_winner: bool = False
        if pieces is None:
            self._pieces = []
        else:
            if not all(isinstance(p, Piece) for p in pieces):
                raise TypeError("All Pieces must be instance of Piece.")
            self._pieces = pieces
        
        ## Criar os métodos
