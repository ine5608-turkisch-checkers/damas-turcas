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
        captured_piece:Piece = None # Deletar isso
        #captured_piece = self.maybe_capture(piece, destination)
        self._maybe_promote(destination)
        self._evaluate_end_condition()

        if captured_piece is not None:
            captured_piece_to_send = {"row": captured_piece.row,"col": captured_piece.col}
        else:
            captured_piece_to_send = None

        winner = self.winner
        game_status = self.game_status # mandamos para o send_move do dog, mas nem usaremos

        self.move_to_send = {
            "origin": origin_to_send,
            "destination": destination_to_send,
            "captured_pieces": captured_piece_to_send,
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
    
    def maybe_capture(self, destination: Position) -> Optional[Position]:
        '''Avalia captura de peça e captura se necessário e retorna posição
        da peça capturada'''
        
        if destination.piece is not None:
            if destination.piece is any(self.get_all_pieces()['player2']):
                captured_piece = destination.piece
                destination.piece.toggle_is_captured()
                destination.piece = None
                captured_piece.position = None
                return captured_piece
        else:
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
        """Retorna as posições de destino possíveis para uma dada peça"""
        print("Entrou no board.possible_moves")

        piece = origin.piece
        if not piece:
            return []

        player = self._player1 if piece in self._player1.pieces else self._player2
        direction = -1 if player == self._player1 else 1  # Sempre vai ser true, não?

        moves = []

        # Para frente como peça normal
        r, c = origin.row + direction, origin.col
        if 0 <= r < BOARD_SIZE: # 0 <= linha < 7
            dest = self._positions[r][c]
            if not dest.is_occupied:
                moves.append(dest)

        # Para os lados (esquerda e direita) como peça normal
        for dc in [-1, 1]:
            r, c = origin.row, origin.col + dc
            if 0 <= c < BOARD_SIZE: # 0 <= coluna < 7
                dest = self._positions[r][c]
                if not dest.is_occupied:
                    moves.append(dest)

        return moves
    
    def verify_capture_as_man(self, selected_linha, selected_coluna, piece_selected_linha, piece_selected_coluna):
        calculo_linha = selected_linha - piece_selected_linha
        calculo_coluna = selected_coluna - piece_selected_coluna

        cond1 = (
            (calculo_linha == 0 and (calculo_coluna == 1 or calculo_coluna == -1)) or
            (calculo_coluna == 0 and calculo_linha == 1)
        )

        if cond1:
            return False

        positions = self.positions

        if calculo_linha == 0:
            direcao = 1 if calculo_coluna > 0 else -1
            captura = positions[selected_linha][selected_coluna + direcao].is_occupied
        else:
            direcao = 1 if calculo_linha > 0 else -1
            captura = positions[piece_selected_linha + direcao][selected_coluna].is_occupied

        if captura:
            return True

        captura = positions[piece_selected_linha][selected_coluna].is_occupied
        if captura:
            return True

        captura = positions[selected_linha][selected_coluna].is_occupied
        if captura:
            return True

        return False

    def switch_turn(self) -> None:
        self._player1.toggle_turn()
        self._player2.toggle_turn()
