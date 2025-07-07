import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
from tkinter.messagebox import showinfo
from typing import List, Tuple

from dog.dog_interface import DogPlayerInterface
from dog.dog_actor import DogActor
from board import Board

BOARD_SIZE = 8
TILE_SIZE = 80
ROOT_BG_COLOR = "#3B4A59"
ROOT_FONT_COLOR = "#F2F2F2"
HIGHLIGHT_COLOR = "#EEDD82"
LIGHT_TILE_COLOR = "#C8AD7F"
DARK_TILE_COLOR = "#5C3A21"

class PlayerInterface(DogPlayerInterface):
    def __init__(self):
        self.main_window = tk.Tk()  # Instancia a janela principal
        self.pieces_id_by_position = {} #ID das posições do canva
        self.all_positions = []
        self.fill_main_window()  # Organiza a janela e cria os widgets
        self.board = Board()
        #self.message_notification = None  # Variável para a mensagem de notificação
        self.all_pieces = []
        self.draw_board()  # Desenha o tabuleiro inicial
        self.associate_canva() # Coloca as peças no tabuleiro
        player_name = simpledialog.askstring(title="Player identification", prompt="Qual o seu nome?")
        self.dog_server_interface = DogActor()
        message = self.dog_server_interface.initialize(player_name, self)
        messagebox.showinfo(message=message)
        self.main_window.mainloop()  # Mantém a janela

    def fill_main_window(self):
        # Configuração do título, tamanho e fundo da janela
        self.main_window.title("Turkish Checkers")
        self.main_window.geometry("640x780")
        self.main_window.resizable(False, False)
        self.main_window.configure(bg=ROOT_BG_COLOR)

        # Frame superior com informações do jogador
        self.info_frame = tk.Frame(self.main_window, bg=ROOT_BG_COLOR)
        self.info_frame.pack(pady=10)

        # Player 1 - Brown
        self.circle1 = tk.Canvas(self.info_frame, width=40, height=40, highlightthickness=0, bg=ROOT_BG_COLOR)
        self.circle1.create_oval(4, 4, 36, 36, fill="#8B5E3C")
        self.circle1.grid(row=0, column=0, padx=(10, 5))

        self.player1_label = tk.Label(self.info_frame, text="Player 1 (Brown): Name1", bg=ROOT_BG_COLOR, fg=ROOT_FONT_COLOR)
        self.player1_label.grid(row=0, column=1, padx=10)

        # VS
        self.vs_label = tk.Label(self.info_frame, text="VS", font=("Arial", "20", "bold"), bg=ROOT_BG_COLOR, fg=ROOT_FONT_COLOR)
        self.vs_label.grid(row=0, column=2, padx=10)

        # Player 2 - Black
        self.player2_label = tk.Label(self.info_frame, text="Player 2 (Black): Name2", bg=ROOT_BG_COLOR, fg=ROOT_FONT_COLOR)
        self.player2_label.grid(row=0, column=3, padx=10)

        self.circle2 = tk.Canvas(self.info_frame, width=40, height=40, highlightthickness=0, bg=ROOT_BG_COLOR)
        self.circle2.create_oval(4, 4, 36, 36, fill="#1C1C1C")
        self.circle2.grid(row=0, column=4, padx=(5, 10))

        # Canvas para desenhar o tabuleiro
        self.canvas = tk.Canvas(self.main_window, width=BOARD_SIZE*TILE_SIZE, height=BOARD_SIZE*TILE_SIZE)
        self.canvas.pack()

        # Área de controle para mensagens
        self.message_notification = tk.Label(self.main_window, text="Message notification here", font=("Arial", 12), bg=ROOT_BG_COLOR, fg=ROOT_FONT_COLOR)
        self.message_notification.pack()

        # Botões de controle
        self.controls_frame = tk.Frame(self.main_window, bg=ROOT_BG_COLOR)
        self.controls_frame.pack(fill="x", pady=10)
        self.controls_frame.columnconfigure(0, weight=1)

        self.spacer = tk.Label(self.controls_frame, text="", bg=ROOT_BG_COLOR)
        self.spacer.grid(row=0, column=0, sticky="ew")

        self.withdraw_button = tk.Button(self.controls_frame, text="Withdraw", command=self.reset_board, bg=ROOT_BG_COLOR, fg=ROOT_FONT_COLOR)
        self.withdraw_button.grid(row=0, column=1, padx=10, sticky="e")

        self.menubar = tk.Menu(self.main_window)
        self.menubar.option_add("*tearOff", False)
        self.main_window["menu"] = self.menubar

        self.menu_file = tk.Menu(self.menubar)
        self.menubar.add_cascade(menu=self.menu_file, label="File")

        self.menu_file.add_command(label="Iniciar jogo", command=self.start_match)

    def update_gui(self, game_status):
        """Atualiza interface com as peças e estados do jogo"""

        self.associate_canva()

    def draw_board(self):
        """Desenha o tabuleiro sem peça nenhuma"""

        self.canvas.delete("all")

        colors = [LIGHT_TILE_COLOR, DARK_TILE_COLOR]

        for row in range(8):
            self.all_positions.append([])
            for col in range(8):
                x1 = col * TILE_SIZE
                y1 = row * TILE_SIZE
                x2 = x1 + TILE_SIZE
                y2 = y1 + TILE_SIZE
                color = colors[(row + col) % 2]

                rect_id = self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")
                self.all_positions[row].append({
                    "rect_id": rect_id,
                    "row": row,
                    "col": col,
                    "obj_piece_back": None
                })

    def clear_pieces(self):
        for canvas_id in self.pieces_id_by_position.values():
            self.canvas.delete(canvas_id)
        self.pieces_id_by_position.clear()

    def associate_canva(self):
        """Recoloca as peças no tabuleiro. Lembrando que a origem
        está no canto superior esquerdo"""

        self.clear_pieces() #Retira todas peças antes de recolocá-las. Forma mais segura.

        all_pieces_back = self.board.get_all_pieces()
        all_pieces = []
        for owner, pieces in all_pieces_back.items():
            all_pieces.append([])
            for piece in pieces:
                if piece.position is not None:
                    row = piece.position.row
                    col = piece.position.col

                    # Cores fixas: na visão de cada jogador, suas próprias peças são sempre marrons
                    fill_color = "#8B5E3C" if owner == 'player1' else "#1C1C1C"

                    x1 = col * TILE_SIZE + 10
                    y1 = row * TILE_SIZE + 10
                    x2 = x1 + TILE_SIZE - 20
                    y2 = y1 + TILE_SIZE - 20

                    piece_tag = f"piece_r{row}c{col}"

                    # Círculo das peças damas
                    # ####### novidade #######
                    self.canvas.create_oval(x1, y1, x2, y2, fill=fill_color, tags=(piece_tag)) # Agora a tag é diferente

                    if piece.is_king:
                        margin = TILE_SIZE // 4
                        inner_x1 = x1 + margin
                        inner_y1 = y1 + margin
                        inner_x2 = x2 - margin
                        inner_y2 = y2 - margin
                        self.canvas.create_oval(inner_x1, inner_y1, inner_x2, inner_y2, fill="white", tags=(piece_tag))
                    
                    ################################################

                    self.pieces_id_by_position[(row, col)] = piece_tag

                    # Notificação na tela de mensagem sobre o status do jogo
                    if self.message_notification is not None:
                        self.message_notification.config(text=self.board.message_game_status())

    def reset_board(self):
        """Retira todas peças do tabuleiro"""
        
        self.draw_board()
        messagebox.showinfo("Reset", "Board has been reset.")

    def restore_initial_state(self):

        self.board = Board()
        self.all_pieces = []
        self.draw_board()  # Desenha o tabuleiro inicial
        self.associate_canva() # Coloca as peças no tabuleiro

    def start_match(self) -> None:
        """Inicia start match"""

        match_status = self.board.game_status
        if match_status == 1:
            answer = messagebox.askyesno("START", "Deseja iniciar uma nova partida?")
            if answer:
                start_status = self.dog_server_interface.start_match(2)
                code = start_status.get_code()
                message = start_status.get_message()
                if code == "0" or code == "1":
                    messagebox.showinfo(message=message)
                else:
                    players = start_status.get_players()
                    local_player_id = start_status.get_local_id()

                    self.board.start_match(players, local_player_id)
                    game_state = self.board.game_status
                    messagebox.showinfo(message=start_status.get_message())

                    self.player1_label.config(text=f"Player 1: {self.board.player1.name}")
                    self.player2_label.config(text=f"Player 2: {self.board.player2.name}")

                    self.update_gui(game_state)

                    #Permitir movimento inicial
                    clickable_positions = [(5, col) for col in range(8)] #3a Linha de baixo para cima 
                    self.enable_clickable_positions(clickable_positions)

    def receive_start(self, start_status) -> None:
        """Recebe start match"""

        self.start_game()
        players = start_status.get_players()
        local_player_id = start_status.get_local_id()
        self.board.start_match(players, local_player_id)

        game_state = self.board.game_status

        self.player1_label.config(text=f"Player 1: {self.board.player1.name}")
        self.player2_label.config(text=f"Player 2: {self.board.player2.name}")

        self.update_gui(game_state)

        clickable_pieces = [(5, col) for col in range(8)] #3a Linha de baixo para cima 
        self.enable_clickable_positions(clickable_pieces)

    def start_game(self) -> None:
        """Inicia o jogo"""

        match_status = self.board.game_status
        game_status = self.board.game_status
        if match_status == 2 or match_status == 6:
            self.board.reset_game()  # Definir o que acontece se FINISHED ou ABANDONED
        self.update_gui(match_status)

    def make_move(self, row: int, col: int) -> None:
        """Fazer a jogada. Ação quando se clica em uma peça habilitada"""

        game_status = self.board.game_status

        if game_status == 5: # Waiting remote move
            
            return

        position_at_clicked = self.board.positions[row][col]

        if game_status == 3: # Waiting local move
            piece_at_clicked = position_at_clicked.piece

            if piece_at_clicked is None:
                return

            local_pieces = self.board.player1.pieces
            if piece_at_clicked not in local_pieces:
                return
            
            mandatory_pieces = self.board.check_mandatory_capture_pieces()
            if mandatory_pieces and piece_at_clicked not in mandatory_pieces:
                messagebox.showinfo("Atenção", "Você deve capturar uma peça.")
                return
            elif not mandatory_pieces:
                moveable_pieces = self.board.get_moveable_pieces()
                if piece_at_clicked not in moveable_pieces:
                    messagebox.showinfo("Atenção", "Essa peça não pode se mover.")
                    return

            self.clear_selection_highlight() # Retira marcações de tiles
            self.board.first_selected_origin = position_at_clicked # Guarda origem no modelo
            self.board.current_selected_origin = position_at_clicked # Guarda origem no modelo
            self.hightlight_selected_tile(row, col) # Marca tile escolhido

            all_coords = [(row, col) for row in range(BOARD_SIZE) for col in range(BOARD_SIZE)]
            self.enable_clickable_positions(all_coords)
            self.board.game_status = 4

            self.update_gui(game_status) ########################################################Talvez não precisa

        elif game_status == 4: # Occurring local move
            origin = self.board.current_selected_origin

            possible_moves = self.board.get_possible_moves(origin)  # Positions válidas
            if position_at_clicked not in possible_moves:
                messagebox.showinfo("Error", "Movimento inválido")
                return

            if not origin:
                return

            destination = position_at_clicked
            self.board.move_piece(origin, destination)
            self.clear_selection_highlight()
            self.clear_all_tile_binds()

            updated_status = self.board.game_status

            if updated_status == 4:  # Ainda há captura obrigatória
                self.board.current_selected_origin = destination
                self.hightlight_selected_tile(destination.row, destination.col)
                
                # Reativa apenas destinos válidos da peça atual
                possible_moves = self.board.get_possible_moves(destination)
                clickable_coords = [(pos.row, pos.col) for pos in possible_moves]
                self.enable_clickable_positions(clickable_coords)
            
            elif updated_status == 2:
                self.send_move()
                #sleep(5) # Espera 5 segundos
                #self.restore_initial_state()

            elif updated_status == 5:  # Jogada acabou, envia para o adversário
                self.send_move()
                self.board.switch_turn()

            self.update_gui(updated_status)

    def send_move(self):
        """Envia um dicionário ao dogActor com todas as informações da jogada"""

        move_to_send = self.board.move_to_send
        self.dog_server_interface.send_move(move_to_send)

        # Reset da jogada
        self.board.first_selected_origin = None
        self.board.current_selected_origin = None
        self.board.move_to_send = None
        self.board.clear_captured_pieces_on_this_turn()

    def receive_move(self, a_move):
        """Recebe a jogada do DogActor"""

        self.board.receive_move(a_move)

        # ATUALIZA GUI antes de qualquer bind
        game_status = self.board.game_status
        self.update_gui(game_status)  # Isso redesenha tudo, inclusive pieces_id_by_position

        if self.board.game_status == 3 or self.board.game_status == 4:
            # Verifica peças que podem capturar
            mandatory_pieces = self.board.check_mandatory_capture_pieces()
            if not mandatory_pieces:
                clickable_positions = self.board.get_moveable_pieces()
                clickable_coords = [(p.position.row, p.position.col) for p in clickable_positions if p.position]
            else:
                clickable_coords = [(p.position.row, p.position.col) for p in mandatory_pieces if p.position]
                messagebox.showinfo("Atenção", "Você deve capturar uma peça.")

            self.enable_clickable_positions(clickable_coords)

    def hightlight_selected_tile(self, row, col):
        tile_id = self.all_positions[row][col]["rect_id"]
        self.canvas.itemconfig(tile_id, fill=HIGHLIGHT_COLOR)

    def clear_selection_highlight(self) -> None:
        """Percorre todos os tiles e restaura qualquer tile com cor de destaque para sua cor original."""

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                tile_id = self.all_positions[row][col]["rect_id"]
                current_color = self.canvas.itemcget(tile_id, "fill")
                if current_color == HIGHLIGHT_COLOR:  # cor de destaque
                    default_color = LIGHT_TILE_COLOR if (row + col) % 2 == 0 else DARK_TILE_COLOR
                    self.canvas.itemconfig(tile_id, fill=default_color)

    def enable_clickable_positions(self, clickable_positions: List[Tuple[int, int]]) -> None:
        """Habilita cliques nas peças e nos tiles dados."""

        self.clear_all_tile_binds()
        for row, col in clickable_positions:
            # Tile (fundo)
            tile_id = self.all_positions[row][col]["rect_id"]
            self.canvas.tag_bind(tile_id, "<Button-1>", lambda event, r=row, c=col: self.make_move(r, c))

            # Peça (se existir)
            piece_id = self.pieces_id_by_position.get((row, col))
            if piece_id is not None:
                self.canvas.tag_bind(piece_id, "<Button-1>", lambda event, r=row, c=col: self.make_move(r, c))


    def clear_all_tile_binds(self) -> None:
        """Remove todos os event bindings (<Button-1>) de todos os tiles do tabuleiro."""

        self.canvas.tag_unbind("piece", "<Button-1>")
