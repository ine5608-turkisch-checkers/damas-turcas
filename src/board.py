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
    def winner(self) -> Optional[Player]:
        return self._winner

    @winner.setter
    def winner(self, winner: Optional[Player]) -> None:
        if winner is not None and not isinstance(winner, Player):
            raise TypeError("Winner must be a Player or None")
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

        print("Definir reset game de acordo com o diagrama")



        return

    def detach_piece_at(self, pos: Position) -> None:
        """Desassocia a peça de uma dada posição"""

        self._positions[pos.row][pos.col].detach_piece()

    def move_piece(self, current_origin: Position, destination: Position) -> None:
        """Move peça de uma posição de origem à uma posição de destino.
        Promove se necessário e checa condição de término de jogo."""

        print("Entrou em move_piece")
        print(f"origin: {current_origin} e current_origin.row e col ({current_origin.row}, {current_origin.col})")
        print(f"destination: {destination} e destination.row e col ({destination.row}, {destination.col})")

        piece = self.piece_at(current_origin)
        if piece is None:
            raise ValueError("Sem peça na origem.")

        first_origin = self.first_selected_origin
        origin_to_send = {"row": first_origin.row, "col": first_origin.col}
        destination_to_send = {"row": destination.row, "col": destination.col}

        # Verifica se há captura e registra se necessário
        captured_coords = self.maybe_capture(piece, current_origin, destination)
        if captured_coords is not None:
            print(f"Achou uma peça para se capturar.")
            print(f"Lista de peças capturadas: {self.captured_pieces_on_this_turn}")

            # Move a peça fisicamente antes de verificar múltiplas capturas
            current_origin.detach_piece()
            destination.piece = piece
            piece.position = destination
            self.current_selected_origin = destination

            if self.verify_multiple_capture():
                print("verify_multiple_capture deu True. Player deve capturar outra peça")
                self.game_status = GameStatus.OCCURRING_LOCAL_MOVE.value
                return

        # Movimento local (sem captura ou fim da sequência de capturas)
        current_origin.detach_piece()
        destination.piece = piece
        piece.position = destination

        # Se não há mais capturas, monta move_to_send
        was_promoted = self._maybe_promote(destination)
        if self._evaluate_end_condition():
            self.game_status = GameStatus.FINISHED.value

        # Monta captured_pieces_data
        captured_pieces_data = []
        for coords in self.captured_pieces_on_this_turn:
            captured_pieces_data.append({
                "row": coords["row"],
                "col": coords["col"]
            })

        winner = self.winner
        game_status = self.game_status
        self.move_to_send = {
            "origin": origin_to_send,
            "destination": destination_to_send,
            "captured_pieces": captured_pieces_data,
            "promoted": was_promoted,
            "winner": winner,
            "game_status": game_status,
            "match_status": 'next',
        }

        self.game_status = GameStatus.WAITING_REMOTE_MOVE.value

    def _maybe_promote(self, pos: Position) -> bool:
        """Avalia se a peça deve ser promovida, e promove se necessário"""

        piece = pos.piece
        if not piece.is_king and pos.row == 0:
            piece.promote_piece()
            return True
        return False

    def maybe_capture(self, piece: Piece, origin: Position, destination: Position) -> Optional[Piece]:
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
                mid_position.piece = None
                captured_piece.position = None
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
                    return None  # já encontrou uma peça antes — não pode capturar duas
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
    
    def receive_move(self, a_move: dict) -> None:
        """Recebe a jogada do adversário e atualiza o tabuleiro."""

        print("Entrou no receive_move")
        print(f"a_move no receive move: {a_move}")

        # Armazena o movimento
        self._received_move = a_move
        
        print("----- [RECEIVE MOVE DEBUG] -----")
        origin_row = 7 - a_move["origin"]["row"]
        origin_col = 7 -a_move["origin"]["col"]
        dest_row = 7 - a_move["destination"]["row"]
        dest_col = 7 - a_move["destination"]["col"]

        origin_pos = self.positions[origin_row][origin_col]
        dest_pos = self.positions[dest_row][dest_col]

        origin_piece = origin_pos.piece
        dest_piece = dest_pos.piece

        all_pieces = self.get_all_pieces()
        owner_origin = 'player1' if origin_piece in all_pieces['player1'] else 'player2' if origin_piece in all_pieces['player2'] else 'None'
        owner_dest = 'player1' if dest_piece in all_pieces['player1'] else 'player2' if dest_piece in all_pieces['player2'] else 'None'

        print(f"Origem recebida: ({origin_row}, {origin_col}) -> Peça: {origin_piece} (Owner: {owner_origin})")
        print(f"Destino recebido: ({dest_row}, {dest_col}) -> Peça: {dest_piece} (Owner: {owner_dest})")

        print("--------------------------------")


        # Verifica vitória
        if a_move["winner"] is not None:
            self._winner = self.player1 if a_move["winner"] == self.player1.id else self.player2
            self._game_status = GameStatus.FINISHED.value
            return  # A interface vai cuidar da notificação e encerramento

        # Remove peças capturadas do adversário
        for captured in a_move["captured_pieces"]:
            row, col = 7- captured["row"], 7 - captured["col"]
            pos = self._positions[row][col]
            if pos.piece:
                pos.piece.toggle_is_captured()
                pos.piece.position = None  # ← remove o vínculo na própria peça
                pos.piece = None           # ← remove o vínculo na posição

        # Move a peça
        origin_data = a_move["origin"]
        print(f"origin_data: {origin_data}")
        dest_data = a_move["destination"]
        origin = self._positions[7 - origin_data["row"]][7 -origin_data["col"]]
        print(f"origin: {origin}")
        print(f"origin row e col: {origin.row} e {origin.col}")
        print(f"origem recebida no receive move {origin}")
        destination = self._positions[7 - dest_data["row"]][7 - dest_data["col"]]

        piece = origin.piece
        print(f"piece recebida no receive move {piece}")
        origin.detach_piece()
        destination.piece = piece
        print(f"piece 2 recebida no receive move {piece}")
        piece.position = destination
        if a_move.get("promoted"):
            piece.promote_piece()

        # 6. Atualiza status e muda o turno de ambos jogadores
        self._game_status = GameStatus.WAITING_LOCAL_MOVE.value
        self.switch_turn()
    
    def check_mandatory_capture_pieces(self) -> List[Piece]:
        """Retorna todas as peças do jogador local (player1) que podem capturar."""

        mandatory_pieces = []

        for piece in self.player1.pieces:
            if piece.is_captured or piece.position is None:
                continue

            if piece.is_king:
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
        enemy_pieces = self._player2.pieces if player == self._player1 else self._player1.pieces

        for d_row, d_col in directions:
            r, c = row + d_row, col + d_col
            found_enemy = False

            while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                current_pos = self._positions[r][c]

                if current_pos.is_occupied:
                    if current_pos.piece in player.pieces:
                        break  # Não pode capturar suas próprias peças
                    elif found_enemy:
                        break  # Já encontrou um inimigo antes — não pode capturar dois
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
