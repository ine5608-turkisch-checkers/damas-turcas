from typing import Optional, List, Dict
from player import Player
from game_status import GameStatus
from position import Position
from piece import Piece

BOARD_SIZE = 8

class Board():
    def __init__(self):
        """Inicializa o board. Instancia os players. Que por sua vez instancia as peças.
        Depois instancia as posições e associa as peças dos players as posições."""

        self._player1: Player = Player() # Precisamos definir os argumentos
        self._player2: Player = Player() # Precisamos definir os argumentos
        self._positions: List[List[Position]] = [
            [Position(row, col) for col in range(BOARD_SIZE)]
            for row in range(BOARD_SIZE)
        ] # pode ser usado com o self._positions[2][3] ex

        self._game_status: int = GameStatus.NO_MATCH.value
        self._winner: Optional[Player] = None
        self._selected_position: Optional[Position] = None
        self._received_move: Optional[dict] = None
        self.place_pieces_on_board()

    @property
    def player1(self) -> Player:
        return self._player1

    @property
    def player2(self) -> Player:
        return self._player2
    
    @property
    def positions(self) -> List[List[Position]]:
        return self._positions

    @property
    def game_status(self) -> int:
        return self._game_status

    @game_status.setter
    def game_status(self, status: int) -> None:
        if status in [s.value for s in GameStatus]:
            self._game_status = status
        else:
            raise ValueError(f"Invalid game status: {status}")

    @property
    def winner(self) -> Optional[Player]:
        return self._winner

    @winner.setter
    def winner(self, winner: Optional[Player]) -> None:
        if winner is not None and not isinstance(winner, Player):
            raise TypeError("Winner must be a Player or None")
        self._winner = winner

    @property
    def selected_position(self) -> Optional[Position]:
        return self._selected_position

    @selected_position.setter
    def selected_position(self, selected_position: Optional[Position]) -> None:
        if selected_position is not None and not isinstance(selected_position, Position):
            raise TypeError("Selected position must be a Position or None")
        self._selected_position = selected_position

    @property
    def received_move(self) -> Optional[dict]:
        return self._received_move

    @received_move.setter
    def received_move(self, received_move: Optional[dict]) -> None:
        if received_move is not None and not isinstance(received_move, dict):
            raise TypeError("Received move must be a dictionary or None")
        self._received_move = received_move

    def player_pieces(self, player: Player) -> List[Piece]:
        """Retorna uma lista de peças de um dado jogador"""

        if player == self.player1:
            return self.player1.pieces
        elif player == self.player2:
            return self.player2.pieces
        else:
            raise TypeError("player is not Player 1 or Player 2")

    def get_all_pieces(self) -> Dict[str, List[Piece]]:
        """Retorna um dicionário com todas as peças
        
        - 'player1': lista de peças do jogador 1
        - 'player2': lista de peças do jogador 2"""

        return {
            'player1': self.player_pieces(self.player1),
            'player2': self.player_pieces(self.player2),
        }
    
    def piece_at(self, pos: Position) -> Optional[Piece]:
        """Retorna peça associada à uma dada posição"""
        
        return self._positions[pos.row][pos.col].piece

    def place_pieces_on_board(self) -> None:
        """Posiciona as 16 peças iniciais de cada jogador no tabuleiro."""

        # Player 1 – linhas 5 e 6 (de baixo para cima)
        pieces_p1 = self.player_pieces(self.player1)
        for row in [5, 6]:
            for col in range(BOARD_SIZE):
                if not pieces_p1:
                    break
                piece = pieces_p1.pop(0)
                position = self._positions[row][col]
                self._player1.associate_piece_position(piece, position)

        # Player 2 – linhas 1 e 2 (de cima para baixo)
        pieces_p2 = self.player_pieces(self.player2)
        for row in [1, 2]:
            for col in range(BOARD_SIZE):
                if not pieces_p2:
                    break
                piece = pieces_p2.pop(0)
                position = self._positions[row][col]
                self._player2.associate_piece_position(piece, position)

    def detach_piece_at(self, pos: Position) -> None:
        """Desassocia a peça de uma dada posição"""

        self._positions[pos.row][pos.col].detach_piece()

    def move_piece(self, origin: Position, destination: Position) -> None:
        """Move peça de uma posição de origem à uma posição de destino.
        Promove se necessário e checa condição de término de jogo"""

        piece = self.piece_at(origin)
        if piece is None:
            raise ValueError("Sem peça na origem.")

        origin.detach_piece()
        destination.piece = piece 
        self._maybe_promote(destination)
        self._evaluate_end_condition()

    # Felipe: Não acho que esse método esteja correto.
    # A verificação não deveria ser local apenas?
    def _maybe_promote(self, pos: Position) -> None:

        piece = pos.piece
        if piece and not piece.is_king:
            if (piece.is_black and pos.row == 0) or (not piece.is_black and pos.row == BOARD_SIZE - 1):
                piece.is_king = True


    # Felipe: Não acho que esse método esteja correto.
    # A verificação do movimento é sempre de si mesmo e cada jogador tem a impressão
    # que está jogando do "sul" do tabuleiro
    def is_valid_move(self, origin: Position, destination: Position) -> bool:
        piece = self.piece_at(origin)
        if piece is None or destination.is_occupied:
            return False

        row_diff = destination.row - origin.row
        col_diff = destination.col - origin.col

        if abs(row_diff) != 1 or abs(col_diff) != 1:
            return False

        if not piece.is_king:
            if piece.is_black and row_diff != -1:
                return False
            if not piece.is_black and row_diff != 1:
                return False

        return True

    def get_possible_moves(self, pos: Position) -> List[Position]:
        moves = []
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dr, dc in directions:
            r, c = pos.row + dr, pos.col + dc
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                dest = self._positions[r][c]
                if not dest.is_occupied and self.is_valid_move(pos, dest):
                    moves.append(dest)
        return moves

    # Felipe: Check winning condition apenas abrange vitória por inexistência de peças
    # não capturadas por parte de um dos jogadores
    def _evaluate_end_condition(self) -> None:
        """Checa condições de vitória do jogo"""

        alive1 = any(not p.is_captured for p in self.player_pieces(self.player1))
        alive2 = any(not p.is_captured for p in self.player_pieces(self.player2))

        if not alive1:
            self._winner = self._player2
            self._game_status = GameStatus.FINISHED.value
        elif not alive2:
            self._winner = self._player1
            self._game_status = GameStatus.FINISHED.value

