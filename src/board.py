from typing import Optional, List
from player import Player
from game_status import GameStatus
from position import Position

BOARD_SIZE = 8

class Board:
    def __init__(self):#
        self._player1 = Player()
        self._player2 = Player()
        self._positions: List[List[Position]] = [
            [Position(row, col) for col in range(BOARD_SIZE)]
            for row in range(BOARD_SIZE)
        ] # pode ser usado com o self._positions[2][3] ex
        self._game_status: int = GameStatus.NO_MATCH.value
        self._winner: Optional[Player] = None
        self._selected_position: Optional[Position] = None
        self._received_move: Optional[dict] = None
        self.place_pieces_on_board()

    def place_pieces_on_board(self):
        num_piece = 0
        for k in range(0, 2):  # Linhas 0 e 1
            for i in range(0, 8):  # Colunas 0 a 7
                position = self._positions[k][i]
                self._player1.associate_piece_position(position, num_piece)
                num_piece += 1

        num_piece = 0
        for k in range(6, 8):  # Linhas 6 e 7
            for i in range(0, 8):  # Colunas 0 a 7
                position = self._positions[k][i]
                self._player2.associate_piece_position(position, num_piece)
                num_piece += 1

    def get_all_pieces(self):
        all_pieces = []
        all_pieces.append(self.player1.pieces)
        all_pieces.append(self.player2.pieces)
        return  all_pieces

    @property
    def player1(self) -> Player:
        return self._player1

    @player1.setter
    def player1(self, player1: Player) -> None:
        if not isinstance(player1, Player):
            raise TypeError("Player 1 must be a Player")
        self._player1 = player1

    @property
    def player2(self) -> Player:
        return self._player2
    
    @player2.setter
    def player2(self, player2: Player) -> None:
        if not isinstance(player2, Player):
            raise TypeError("Player 2 must be a Player")
        self._player2 = player2

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

    def get_piece(self, pos: Position):
        return self._positions[pos.row][pos.col].piece

    def remove_piece(self, pos: Position) -> None:
        self._positions[pos.row][pos.col].detach_piece()

    def move_piece(self, origin: Position, destination: Position) -> None:
        piece = self.get_piece(origin)
        if piece is None:
            raise ValueError("Sem peça na origem.")

        self.remove_piece(origin)
        self._positions[destination.row][destination.col].piece = piece
        self.promote_if_necessary(destination)
        self.check_game_over()

    def promote_if_necessary(self, pos: Position) -> None:
        piece = pos.piece
        if piece and not piece.is_king:
            if (piece.is_black and pos.row == 0) or (not piece.is_black and pos.row == BOARD_SIZE - 1):
                piece.is_king = True


    def is_valid_move(self, origin: Position, destination: Position) -> bool:
        piece = self.get_piece(origin)
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

    def check_game_over(self) -> None:
        alive1 = any(p.is_alive for p in self._player1.pieces)
        alive2 = any(p.is_alive for p in self._player2.pieces)

        if not alive1:
            self._winner = self._player2
            self._game_status = GameStatus.FINISHED.value
        elif not alive2:
            self._winner = self._player1
            self._game_status = GameStatus.FINISHED.value

"""    def initialize_board(self):
        #Posiciona as 16 peças iniciais de cada jogador no tabuleiro
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                pos = self._positions[row][col]
                if row < 2:
                    piece = Piece(is_black=True)
                    pos.piece = piece
                    self._player2.pieces.append(piece)
                elif row >= BOARD_SIZE - 2:
                    piece = Piece(is_black=False)
                    pos.piece = piece
                    self._player1.pieces.append(piece)
"""

# - Inicialização do tabuleiro e posicionamento das peças
# - Movimentação, promoção a dama e remoção de peças
# - Validação de jogadas conforme regras do jogo
# - Detecção do fim de jogo e definição do vencedor
# Interage diretamente com Player, Position, Piece e GameStatus.