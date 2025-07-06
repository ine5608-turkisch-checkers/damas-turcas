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
        ] # pode ser usado com o self._positions[2][3] ex

        self._game_status: int = GameStatus.NO_MATCH.value
        self._winner: Optional[Player] = None
        self._selected_origin: Optional[Position] = None #Seria bom chamar de selected_origin, usado para o make e send move
        self._captured_pieces_on_this_turn = []
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
    def winner(self) -> Optional[Player]:
        return self._winner

    @winner.setter
    def winner(self, winner: Optional[Player]) -> None:
        if winner is not None and not isinstance(winner, Player):
            raise TypeError("Winner must be a Player or None")
        self._winner = winner

    @property
    def selected_origin(self) -> Optional[Position]:
        return self._selected_origin

    @selected_origin.setter
    def selected_origin(self, selected_origin: Optional[Position]) -> None:
        if selected_origin is not None and not isinstance(selected_origin, Position):
            raise TypeError("Selected position must be a Position or None")
        self._selected_origin = selected_origin

    @property
    def captured_pieces_on_this_turn(self) -> List[Piece]:
        return self._captured_pieces_on_this_turn
    
    def add_captured_piece_on_this_turn(self, piece: Piece) -> None:
        self._captured_pieces_on_this_turn.append(piece)
    
    def clear_captured_pieces_on_this_turn(self) -> None:
        self._captured_pieces_on_this_turn.clear()

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

    def detach_piece_at(self, pos: Position) -> None:
        """Desassocia a peça de uma dada posição"""

        self._positions[pos.row][pos.col].detach_piece()

    def move_piece(self, origin: Position, destination: Position) -> None:
        """Move peça de uma posição de origem à uma posição de destino.
        Promove se necessário e checa condição de término de jogo"""

        print("Entrou em move_piece")
        print(f"origin: {origin} e origin.row e col ({origin.row}, {origin.col})")
        print(f"destination: {origin} e destination.row e col ({destination.row}, {destination.col})")

        piece = self.piece_at(origin)
        if piece is None:
            raise ValueError("Sem peça na origem.")

        origin_to_send = {"row": origin.row, "col": origin.col}
        destination_to_send = {"row": destination.row,"col": destination.col}

        origin.detach_piece()
        destination.piece = piece
        piece.position = destination

        captured_piece = self.maybe_capture(origin, destination)
        if captured_piece is not None:
            self.add_captured_piece_on_this_turn(captured_piece)
            if self.verify_multiple_capture():
                return

        self._maybe_promote(destination)
        if self._evaluate_end_condition():
            self.game_status = GameStatus.FINISHED.value

        captured_pieces_data = []
        for piece in self.captured_pieces_on_this_turn:
            if piece.position:
                captured_pieces_data.append({
                    "row": piece.position.row,
                    "col": piece.position.col
                })

        winner = self.winner
        game_status = self.game_status # mandamos para o send_move do dog, mas nem usaremos

        self.move_to_send = {
            "origin": origin_to_send,
            "destination": destination_to_send,
            "captured_pieces": captured_pieces_data,
            "winner": winner,
            "game_status": game_status,
            "match_status": 'next', # 'next', 'progress' ou 'finished'
        }

        self.game_status = GameStatus.WAITING_REMOTE_MOVE.value # Waiting remote move

    def _maybe_promote(self, pos: Position) -> None:
        """Avalia se a peça deve ser promovida, e promove se necessário"""

        print("Entrou no maybe promote")

        piece = pos.piece
        if not piece.is_king: #Se a peça não for dama
            if pos.row == 0:
                piece.is_king = True
    
    def maybe_capture(self, origin: Position, destination: Position) -> Optional[Piece]:
        """Se a jogada foi uma captura (movimento de 2 casas), remove a peça inimiga intermediária e retorna ela."""

        d_row = destination.row - origin.row
        d_col = destination.col - origin.col

        # Só é captura (já avaliado no self.get_possible_moves) se houve salto
        if abs(d_row) == 2 or abs(d_col) == 2:
            mid_row = origin.row + (d_row // 2)
            mid_col = origin.col + (d_col // 2)

            mid_position = self._positions[mid_row][mid_col]
            captured_piece = mid_position.piece

            if captured_piece:
                captured_piece.toggle_is_captured()
                mid_position.piece = None
                captured_piece.position = None
                return captured_piece

        return None

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

    def start_match(self, players: str, local_player_id: str) -> bool:
        """
        Atualiza os atributos dos jogadores existentes com os dados da Dog API.
        Define quem começa e retorna True se for o jogador local, False caso contrário.
        """
        print("Entrou no board.start match")

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

        ## Para desenvolvimento ###########
        if self.is_local_player:
            print("Este é o jogador 1")
        else:
            print("Este é o jogador 2")
        print(f"player1_id: {self.player1.id}")
        print(f"player2_id: {self.player2.id}")

        ###################################
    
    def receive_move(self, a_move):
        '''Recebe a jogada do dogActor'''

        print("Entrou no receive_move")
        print(f"a_move: {a_move}")

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
                    return f"Partida terminada. {winner.name} venceu a partida."
            case 3:
                return f"Sua vez. Escolha uma peça."
            case 4:
                return f"Agora escolha um destino para a sua peça."
            case 5:
                return f"Seu adversário está jogando."
            case 6:
                return f"Partida abandonada."
    def get_possible_moves(self, origin: Position) -> List[Position]:
        """Retorna as posições de destino possíveis para uma dada peça, considerando capturas e tipo (peão ou dama)."""
        print("Entrou no board.get_possible_moves")

        piece = origin.piece
        if not piece:
            return []

        if piece.is_king:
            return self.get_possible_moves_as_king(origin)
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
    
    def get_possible_moves_as_king(self, origin: Position) -> List[Position]:
        """Retorna as posições de destino possíveis para uma dada dama"""

        piece = origin.piece
        player = self._player1 if piece in self._player1.pieces else self._player2
        enemy_pieces = self._player2.pieces if player == self._player1 else self._player1.pieces

        moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # cima, baixo, esquerda, direita

        for dr, dc in directions:
            r, c = origin.row + dr, origin.col + dc
            found_enemy = False

            while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                current_pos = self._positions[r][c]

                if current_pos.is_occupied:
                    if current_pos.piece in player.pieces:
                        break  # bloqueado por peça própria
                    elif found_enemy:
                        break  # não pode capturar duas seguidas
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
    
    def verify_multiple_capture(self) -> bool:
        """Verifica se alguma peça do jogador local deve realizar uma captura."""

        for piece in self.player1.pieces:  # Só o jogador local
            if piece.is_captured or piece.position is None:
                continue

            if piece.is_king:
                if self.verify_capture_as_king(piece):
                    return True
            else:
                if self.verify_capture_as_man(piece):
                    return True

        return False
    
    def verify_capture_as_man(self, piece: Piece) -> bool:
        pos = piece.position
        row, col = pos.row, pos.col
        directions = [(-1, 0), (0, -1), (0, 1)]  # Frente, esquerda, direita para o jogador 1

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
                    mid_pos.piece in self.player2.pieces and
                    not dest_pos.is_occupied
                ):
                    return True

        return False

    def verify_capture_as_king(self, piece: Piece) -> bool:
        pos = piece.position
        row, col = pos.row, pos.col
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Cima, baixo, esquerda, direita

        for d_row, d_col in directions:
            r, c = row + d_row, col + d_col
            found_enemy = False

            while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE: #Um loop dentro das posições do board
                current_pos = self._positions[r][c]

                if current_pos.is_occupied:
                    if current_pos.piece in self.player1.pieces:
                        break  # Não pode capturar suas próprias peças
                    elif found_enemy:
                        break  # Já havia um inimigo, não pode ter dois
                    else:
                        found_enemy = True
                else:
                    if found_enemy:
                        return True  # Encontrou inimigo e casa livre depois: pode capturar

                r += d_row
                c += d_col

        return False

    def switch_turn(self) -> None:
        self._player1.toggle_turn()
        self._player2.toggle_turn()
