from typing import Optional, List, Dict
from player import Player
from game_status import GameStatus
from position import Position
from piece import Piece

BOARD_SIZE = 8

class Board:
    def __init__(self):
        """Inicializa o board. Instancia os players. Que por sua vez instancia as peças.
        Depois instancia as posições e associa as peças dos players as posições."""
        self._player1 = Player()
        self._player2 = Player()
        self._positions: List[List[Position]] = [
            [Position(row, col) for col in range(BOARD_SIZE)]
            for row in range(BOARD_SIZE)
        ]

        self._game_status: int = GameStatus.NO_MATCH.value
        self._winner: Optional[str] = None
        self._first_selected_origin: Optional[Position] = None # Local onde a peça escolhida estava no início da jogada
        self._current_selected_origin: Optional[Position] = None # Usado para múltiplas capturas, acompanha a peça
        self._captured_pieces_on_this_turn: List[Dict[str, int]] = [] # Peças capturadas nesse turno
        self._move_to_send: Optional[Dict] = None
        self._received_move: Optional[dict] = None
        self.place_pieces_on_board()
        self.is_local_player: bool = False

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
    def winner(self) -> Optional[str]:
        return self._winner

    @winner.setter
    def winner(self, winner: Optional[str]) -> None:
        if winner is not None and not isinstance(winner, str):
            raise TypeError("Winner must be a string or None")
        self._winner = winner

    @property
    def first_selected_origin(self) -> Optional[Position]:
        return self._first_selected_origin

    @first_selected_origin.setter
    def first_selected_origin(self, first_selected_origin: Optional[Position]) -> None:
        if first_selected_origin is not None and not isinstance(first_selected_origin, Position):
            raise TypeError("First selected origin must be a Position or None")
        self._first_selected_origin = first_selected_origin

    @property
    def current_selected_origin(self) -> Optional[Position]:
        return self._current_selected_origin

    @current_selected_origin.setter
    def current_selected_origin(self, current_selected_origin: Optional[Position]) -> None:
        if current_selected_origin is not None and not isinstance(current_selected_origin, Position):
            raise TypeError("Current selected origin must be a Position or None")
        self._current_selected_origin = current_selected_origin

    @property
    def captured_pieces_on_this_turn(self) -> List[Dict[str, int]]:
        return self._captured_pieces_on_this_turn
    
    def add_captured_piece_on_this_turn(self, row: int, col: int) -> None:
        self._captured_pieces_on_this_turn.append({"row": row, "col": col})
    
    def clear_captured_pieces_on_this_turn(self) -> None:
        self._captured_pieces_on_this_turn = []

    @property
    def move_to_send(self) -> Optional[Dict]:
        return self._move_to_send

    @move_to_send.setter
    def move_to_send(self, move: Optional[Dict]) -> None:
        if move is not None and not isinstance(move, dict):
            raise TypeError("move_to_send must be a dictionary or None")
        self._move_to_send = move

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

    def place_pieces_on_board(self):
        """Coloca peças já instanciadas nas posições iniciais.
        Lembrando que a origem está no canto superior esquerdo"""

        num_piece = 0
        for k in range(5, 7):  # Linhas 1 e 2
            for i in range(0, 8):  # Colunas 0 a 7
                position = self._positions[k][i]
                self._player1.associate_piece_position(position, num_piece)
                num_piece += 1

        num_piece = 0
        for k in range(1, 3):  # Linhas 6 e 7
            for i in range(0, 8):  # Colunas 0 a 7
                position = self._positions[k][i]
                self._player2.associate_piece_position(position, num_piece)
                num_piece += 1

    def reset_game(self):
        """Reseta tudo do jogo"""
        ...

        return

    def detach_piece_at(self, pos: Position) -> None:
        """Desassocia a peça de uma dada posição"""

        self._positions[pos.row][pos.col].detach_piece()

    def move_piece(self, current_origin: Position, destination: Position) -> None:
        piece = self.piece_at(current_origin)
        if piece is None:
            raise ValueError("Sem peça na origem.")

        # Guarda origens para envio
        first_origin = self.first_selected_origin
        origin_to_send = {"row": first_origin.row, "col": first_origin.col}
        destination_to_send = {"row": destination.row, "col": destination.col}

        # Move a peça primeiro
        current_origin.detach_piece()
        destination.piece = piece
        piece.position = destination

        # Verifica captura
        captured_coords = self.maybe_capture(piece, current_origin, destination)
        has_capture = captured_coords is not None

        # Se houve captura, verifica se pode capturar novamente
        if has_capture:
            self.current_selected_origin = destination
            if self.verify_multiple_capture():
                self.game_status = GameStatus.OCCURRING_LOCAL_MOVE.value
                return  # Aguarda próxima captura

        # Promoção e verificação de fim de jogo
        was_promoted = self._maybe_promote(destination)
        game_finished = self._evaluate_end_condition()
        if game_finished:
            self.move_to_send = {
                "winner": self.player1.name,
                "match_status": 'finished'
            }
            return

        # Prepara dados para envio
        captured_pieces_data = [{"row": c["row"], "col": c["col"]} 
                            for c in self.captured_pieces_on_this_turn]

        self.move_to_send = {
            "origin": origin_to_send,
            "destination": destination_to_send,
            "captured_pieces": captured_pieces_data,
            "promoted": was_promoted,
            "winner": self._winner.name if self._winner else None,
            "game_status": self.game_status,
            "match_status": 'next'
        }

        if not game_finished:
            self.game_status = GameStatus.WAITING_REMOTE_MOVE.value
        else:
            self.game_status = GameStatus.FINISHED.value

    def _maybe_promote(self, pos: Position) -> bool:
        """Avalia se a peça deve ser promovida, e promove se necessário"""

        piece = pos.piece
        if not piece.is_king and pos.row == 0:
            piece.promote_piece()
            return True
        return False

    def maybe_capture(self, piece: Piece, origin: Position, destination: Position) -> Optional[Piece]:
        """Determina se há uma captura para dada peça"""

        if piece.is_king:
            return self.capture_as_king(origin, destination)
        else:
            return self.capture_as_man(origin, destination)

    def capture_as_man(self, origin: Position, destination: Position) -> Optional[Piece]:
        """Determina se há uma captura como peão, e executa a remoção da peça capturada"""

        d_row = destination.row - origin.row
        d_col = destination.col - origin.col

        if abs(d_row) == 2 or abs(d_col) == 2:
            mid_row = origin.row + (d_row // 2)
            mid_col = origin.col + (d_col // 2)
            mid_position = self._positions[mid_row][mid_col]
            captured_piece = mid_position.piece

            if captured_piece:
                self.add_captured_piece_on_this_turn(mid_row, mid_col)
                captured_piece.toggle_is_captured()
                mid_position.detach_piece()  # Usar detach_piece em vez de atribuir None
                return captured_piece
        return None

    def capture_as_king(self, origin: Position, destination: Position) -> Optional[Piece]:
        """Determina se há uma captura como dama, e executa a remoção da peça capturada"""

        d_row = destination.row - origin.row
        d_col = destination.col - origin.col

        # Verifica se o movimento é em linha reta (horizontal ou vertical)
        if d_row != 0 and d_col != 0 and d_row != d_col and d_row != -d_col:
            return None

        step_row = (d_row // abs(d_row)) if d_row != 0 else 0
        step_col = (d_col // abs(d_col)) if d_col != 0 else 0

        r = origin.row + step_row
        c = origin.col + step_col
        captured_piece = None

        while (r != destination.row or c != destination.col):
            current_pos = self._positions[r][c]

            if current_pos.is_occupied:
                if captured_piece is not None:
                    return None  # já encontrou uma peça antes, não pode capturar duas
                if current_pos.piece in self.player1.pieces:
                    return None  # não pode capturar suas próprias peças
                captured_piece = current_pos.piece
                captured_row = r
                captured_col = c

            r += step_row
            c += step_col

        if captured_piece:
            self.add_captured_piece_on_this_turn(captured_row, captured_col)
            captured_piece.toggle_is_captured()
            self._positions[captured_row][captured_col].piece = None
            captured_piece.position = None
            return captured_piece

        return None

    def _evaluate_end_condition(self) -> bool:
        """Checa condições de vitória do jogo"""

        pieces1 = [p for p in self.player_pieces(self.player1) if not p.is_captured]
        pieces2 = [p for p in self.player_pieces(self.player2) if not p.is_captured]

        alive1 = len(pieces1) > 0
        alive2 = len(pieces2) > 0

        # Regra 1: player1 tem 1 dama, player2 tem 1 peão
        if not alive1:
            self._winner = self._player2
            self._game_status = GameStatus.FINISHED.value
            return True
        elif not alive2:
            self._winner = self._player1
            self._game_status = GameStatus.FINISHED.value
            return True

        # Regra 2: player1 tem 1 dama, player2 tem 1 peão
        if len(pieces1) == 1 and pieces1[0].is_king and len(pieces2) == 1 and not pieces2[0].is_king:
            self._winner = self._player1
            self._game_status = GameStatus.FINISHED.value
            return True

        # Regra 3: empate se ambos só têm 1 peão
        if len(pieces1) == 1 and len(pieces2) == 1 and not pieces1[0].is_king and not pieces2[0].is_king:
            self._winner = None
            self._game_status = GameStatus.FINISHED.value
            return True

        return False

    def start_match(self, players: str, local_player_id: str) -> bool:
        """Atualiza os atributos dos jogadores existentes com os dados da Dog API.
        Define quem começa e retorna True se for o jogador local, False caso contrário."""

        player1_name = players[0][0]
        player1_id = players[0][1]
        player1_order = players[0][2]
        player2_name = players[1][0]
        player2_id = players[1][1]
        self.player1.reset()
        self.player2.reset()
        self.player1.id = player1_id
        self.player1.name = player1_name
        self.player2.id = player2_id
        self.player2.name = player2_name
        if player1_order == "1":
            self.is_local_player = True
            self.player1.toggle_turn()
            self.game_status = GameStatus.WAITING_LOCAL_MOVE.value
        else:
            self.player2.toggle_turn()
            self.game_status = GameStatus.WAITING_REMOTE_MOVE.value
    
    def receive_move(self, a_move: dict) -> None:
        """Recebe a jogada do adversário e atualiza o tabuleiro."""

        # Armazena o movimento
        self._received_move = a_move

        if a_move["match_status"] == "finished":
            self.winner = a_move["winner"]
            self.game_status = GameStatus.FINISHED.value
            return

        # Verifica vitória
        if a_move["winner"] is not None:
            if a_move["winner"] == self.player1.name:
                self._winner = self.player1
            elif a_move["winner"] == self.player2.name:
                self._winner = self.player2
            self._game_status = GameStatus.FINISHED.value
            return  # A interface vai cuidar da notificação e encerramento

        # Remove peças capturadas do adversário
        for captured in a_move["captured_pieces"]:
            row, col = 7 - captured["row"], 7 - captured["col"]
            pos = self._positions[row][col]
            if pos.piece:
                pos.piece.toggle_is_captured()
                pos.detach_piece()  # Limpa a posição

        # Move a peça
        origin_data = a_move["origin"]
        dest_data = a_move["destination"]
        origin = self._positions[7 - origin_data["row"]][7 -origin_data["col"]]
        destination = self._positions[7 - dest_data["row"]][7 - dest_data["col"]]

        piece = origin.piece
        origin.detach_piece()
        destination.piece = piece
        piece.position = destination
        if a_move.get("promoted"):
            piece.promote_piece()

        # Atualiza status e muda o turno de ambos jogadores
        self._game_status = GameStatus.WAITING_LOCAL_MOVE.value
        self.switch_turn()
    
    def check_mandatory_capture_pieces(self) -> List[Piece]:
            """Retorna todas as peças do jogador local (player1) que podem capturar."""

            mandatory_pieces = []

            for piece in self.player1.pieces:
                if piece.is_captured or piece.position is None:
                    continue

                elif piece.is_king:
                    if self.verify_capture_as_king(piece):
                        mandatory_pieces.append(piece)
                else:
                    if self.verify_capture_as_man(piece):
                        mandatory_pieces.append(piece)

            return mandatory_pieces

    def message_game_status(self) -> str:
        """Retorna mensagem referente ao estado do jogo"""

        game_status = self.game_status

        match game_status:
            case 1:
                return f"Para iniciar uma nova partida, clique em 'Iniciar jogo' no canto esquerdo superior."
            case 2:
                winner = self.winner
                if winner is None:
                    return f"Partida terminada sem vencedores."
                else:
                    return f"Partida terminada. {winner if isinstance(winner, str) else winner.name} venceu a partida."
            case 3:
                return f"Sua vez. Escolha uma peça."
            case 4:
                return f"Agora escolha um destino para a sua peça."
            case 5:
                return f"Seu adversário está jogando."
            case 6:
                return f"Partida abandonada."
    def get_possible_moves(self, origin: Position) -> List[Position]:
        """Retorna as posições de destino possíveis para uma dada peça, priorizando capturas obrigatórias."""

        piece = origin.piece
        if not piece:
            return []

        if piece.is_king:
            if self.verify_capture_as_king(piece):
                return self.get_capture_moves_as_king(origin)
            else:
                return self.get_possible_moves_as_king(origin)
        else:
            if self.verify_capture_as_man(piece):
                return self.get_capture_moves_as_man(origin)
            else:
                return self.get_possible_moves_as_man(origin)

    def get_possible_moves_as_man(self, origin: Position) -> List[Position]:
        """Retorna as posições de destino possíveis para uma dado peão"""

        piece = origin.piece
        player = self._player1 if piece in self._player1.pieces else self._player2
        enemy_pieces = self._player2.pieces if player == self._player1 else self._player1.pieces

        moves = []
        directions = [(-1, 0), (0, -1), (0, 1)]  # frente, esquerda, direita

        for dr, dc in directions:
            r1 = origin.row + dr
            c1 = origin.col + dc

            if 0 <= r1 < BOARD_SIZE and 0 <= c1 < BOARD_SIZE:
                mid_pos = self._positions[r1][c1]

                if not mid_pos.is_occupied:
                    moves.append(mid_pos)
                elif mid_pos.piece in enemy_pieces:
                    r2 = r1 + dr
                    c2 = c1 + dc
                    if 0 <= r2 < BOARD_SIZE and 0 <= c2 < BOARD_SIZE:
                        landing_pos = self._positions[r2][c2]
                        if not landing_pos.is_occupied:
                            moves.append(landing_pos)

        return moves

    def get_capture_moves_as_man(self, origin: Position) -> List[Position]:
        """Retorna apenas as posições de captura possíveis para um peão."""

        piece = origin.piece
        if not piece:
            return []

        player = self._player1 if piece in self._player1.pieces else self._player2
        enemy_pieces = self._player2.pieces if player == self._player1 else self._player1.pieces

        moves = []
        directions = [(-1, 0), (0, -1), (0, 1)]  # frente, esquerda, direita

        for dr, dc in directions:
            r1, c1 = origin.row + dr, origin.col + dc
            r2, c2 = origin.row + 2*dr, origin.col + 2*dc

            if (
                0 <= r1 < BOARD_SIZE and 0 <= c1 < BOARD_SIZE and
                0 <= r2 < BOARD_SIZE and 0 <= c2 < BOARD_SIZE
            ):
                mid_pos = self._positions[r1][c1]
                dest_pos = self._positions[r2][c2]

                if (
                    mid_pos.is_occupied and
                    mid_pos.piece in enemy_pieces and
                    not dest_pos.is_occupied
                ):
                    moves.append(dest_pos)

        return moves

    def get_possible_moves_as_king(self, origin: Position) -> List[Position]:
        """Retorna as posições de destino possíveis para uma dada dama"""

        piece = origin.piece
        player = self._player1 if piece in self._player1.pieces else self._player2

        moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # cima, baixo, esquerda, direita

        for dr, dc in directions:
            r, c = origin.row + dr, origin.col + dc
            found_enemy = False

            while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                current_pos = self._positions[r][c]

                if current_pos.is_occupied:
                    if (current_pos.piece in player.pieces) or found_enemy:
                        break
                    else:
                        found_enemy = True
                else:
                    if found_enemy:
                        # Casa vazia após peça inimiga: captura
                        moves.append(current_pos)
                        break  # só pode capturar uma por vez
                    else:
                        # Movimento simples
                        moves.append(current_pos)

                r += dr
                c += dc

        return moves
    
    def get_capture_moves_as_king(self, origin: Position) -> List[Position]:
        """Retorna apenas as posições de captura possíveis para uma dama."""

        piece = origin.piece
        if not piece:
            return []

        player = self._player1 if piece in self._player1.pieces else self._player2

        moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # cima, baixo, esquerda, direita

        for dr, dc in directions:
            r, c = origin.row + dr, origin.col + dc
            found_enemy = False

            while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                current_pos = self._positions[r][c]

                if current_pos.is_occupied:
                    if (current_pos.piece in player.pieces) or found_enemy:
                        break
                    else:
                        found_enemy = True
                else:
                    if found_enemy:
                        # Encontrou inimigo e casa vazia depois: pode capturar
                        moves.append(current_pos)
                        break
                r += dr
                c += dc

        return moves

    def verify_multiple_capture(self) -> bool:
        """Verifica se a peça que acabou de capturar pode capturar novamente."""

        current = self.current_selected_origin
        if current is None or current.piece is None or current.piece.is_captured:
            return False

        piece = current.piece
        if piece.is_king:
            return self.verify_capture_as_king(piece)
        else:
            return self.verify_capture_as_man(piece)
    
    def verify_capture_as_man(self, piece: Piece) -> bool:
        pos = piece.position
        row, col = pos.row, pos.col
        directions = [(-1, 0), (0, -1), (0, 1)]  # Frente, esquerda, direita

        player = self._player1 if piece in self._player1.pieces else self._player2
        enemy_pieces = self._player2.pieces if player == self._player1 else self._player1.pieces

        for d_row, d_col in directions:
            mid_row = row + d_row
            mid_col = col + d_col
            dest_row = row + 2 * d_row
            dest_col = col + 2 * d_col

            if (
                0 <= mid_row < BOARD_SIZE and 0 <= mid_col < BOARD_SIZE and
                0 <= dest_row < BOARD_SIZE and 0 <= dest_col < BOARD_SIZE
            ):
                mid_pos = self._positions[mid_row][mid_col]
                dest_pos = self._positions[dest_row][dest_col]

                if (
                    mid_pos.is_occupied and
                    mid_pos.piece in enemy_pieces and
                    not dest_pos.is_occupied
                ):
                    return True

        return False

    def verify_capture_as_king(self, piece: Piece) -> bool:
        pos = piece.position
        row, col = pos.row, pos.col
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Cima, baixo, esquerda, direita

        player = self._player1 if piece in self._player1.pieces else self._player2

        for d_row, d_col in directions:
            r, c = row + d_row, col + d_col
            found_enemy = False

            while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                current_pos = self._positions[r][c]

                if current_pos.is_occupied:
                    if (current_pos.piece in player.pieces) or found_enemy:
                        break  # Não pode capturar suas próprias peças
                    else:
                        found_enemy = True
                else:
                    if found_enemy:
                        return True  # Encontrou inimigo e casa livre depois: pode capturar

                r += d_row
                c += d_col

        return False

    # Equivalente ao verificar peças que podem se mover, acho eu
    def get_moveable_pieces(self) -> List[Piece]:
        """Retorna todas as peças do jogador local (player1) que podem se mover."""

        moveable_pieces = []

        for piece in self.player1.pieces:
            if piece.is_captured or piece.position is None:
                continue

            origin = piece.position
            possible_moves = self.get_possible_moves(origin)

            if possible_moves:  # Se tiver qualquer destino possível
                moveable_pieces.append(piece)

        return moveable_pieces

    def switch_turn(self) -> None:
        self._player1.toggle_turn()
        self._player2.toggle_turn()
