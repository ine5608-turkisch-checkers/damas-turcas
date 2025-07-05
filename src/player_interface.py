import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
from tkinter.messagebox import showinfo

from dog.dog_interface import DogPlayerInterface
from dog.dog_actor import DogActor
from board import Board

BOARD_SIZE = 8
TILE_SIZE = 80
ROOT_BG_COLOR = "#3B4A59"
ROOT_FONT_COLOR = "#F2F2F2"
#self.canvas.tag_bind(rect_id, "<Button-1>", lambda event, rid=rect_id: self.on_tile_click(event, rid))

class PlayerInterface(DogPlayerInterface):
    def __init__(self):
        self.main_window = tk.Tk()  # Instancia a janela principal
        self.fill_main_window()  # Organiza a janela e cria os widgets
        self.board = Board()
        self.message_notification = None  # Variável para a mensagem de notificação
        self.all_positions = []
        self.all_pieces = []
        self.draw_board()  # Desenha o tabuleiro inicial
        self.associate_canva()
        player_name = simpledialog.askstring(title="Player identification", prompt="Qual o seu nome?")
        self.dog_server_interface = DogActor()
        message = self.dog_server_interface.initialize(player_name, self)
        messagebox.showinfo(message=message)
        self.main_window.mainloop()  # Mantém a janela
        self.local_player_id = None

    def associate_canva(self):
        """Recoloca as peças no tabuleiro e associa os eventos de clique."""

        #self.all_pieces.clear()  # Limpa a lista de peças do canvas

        all_pieces_back = self.board.get_all_pieces()
        for owner, pieces in all_pieces_back.items():
            for piece in pieces:
                if piece.position is not None:
                    row = piece.position.row
                    col = piece.position.col
                    # Cores fixas: o jogador local vê suas peças como marrons
                    fill_color = "#1C1C1C" if owner == 'player1' else "#8B5E3C"

                    x1 = col * TILE_SIZE + 10
                    y1 = row * TILE_SIZE + 10
                    x2 = x1 + TILE_SIZE - 20
                    y2 = y1 + TILE_SIZE - 20

                    piece_canva = self.canvas.create_oval(x1, y1, x2, y2, fill=fill_color, tags="piece")

                    self.all_pieces.append(piece_canva)

                    # Associa o clique passando linha, coluna e id da peça
                    self.canvas.tag_bind(
                        piece_canva,
                        "<Button-1>",
                        lambda event, r=row, c=col, cid=piece_canva: self.make_move(r, c, cid)
                    )

        # Atualiza mensagem na interface, se houver
        if self.message_notification is not None:
            self.message_notification.config(text=self.board.message_game_status())

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
        #self.canvas.bind("<Button-1>", self.on_tile_click)

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
        # Adicionar itens de menu a cada menu adicionado à barra de menu:
        self.menu_file.add_command(label="Iniciar jogo", command=self.start_match)
        #self.menu_file.add_command(label="Restaurar estado inicial", command=self.start_game)

    def update_gui(self, game_state):
        pass #não precisa desse metodo, mover e deletar pode ser feito pelo proprio canva

    def draw_board(self):
        #self.canvas.delete("all")
        # Inicializa a matriz 8x8

        colors = ["#C8AD7F", "#5C3A21"]

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

    def reset_board(self):
        self.draw_board()
        messagebox.showinfo("Reset", "Board has been reset.")
    
    def receive_move(self, a_move):
        #self.board.receive_move(a_move)
        #game_state = self.board.game_status
        #self.update_gui(game_state)
        pass

    def start_match(self):
        print("Entrou no start match")
        match_status = self.board.game_status
        if match_status == 1:
            answer = messagebox.askyesno("START", "Deseja iniciar uma nova partida?")
            if answer:
                start_status = self.dog_server_interface.start_match(2)
                code = start_status.get_code()
                message = start_status.get_message()
                if code == "0" or code == "1":
                    messagebox.showinfo(message=message)
                elif code == 2:
                    players = start_status.get_players()
                    local_player_id = start_status.get_local_id()

                    my_turn = self.board.start_match(players, local_player_id)
                    self.local_player_id = local_player_id
                    game_state = self.board.game_status
                    messagebox.showinfo(message=start_status.get_message())
                    self.player1_label.config(text=f"Player 1 (Brown): {self.board.player1.name}")
                    self.player2_label.config(text=f"Player 2 (Black): {self.board.player2.name}")
                    self.update_gui(game_state)
                    messagebox.showinfo(message=start_status.get_message())
                    if my_turn:
                        all_pieces_back = self.board.get_all_pieces()
                        all_pieces_back = all_pieces_back["player1"]
                        all_pieces_canva = self.all_pieces
                        for i in range(8, 16):
                            piece_back = all_pieces_back[i]
                            row = piece_back.position.row
                            col = piece_back.position.col
                            piece_canva = all_pieces_canva[i]
                            piece_canva.tag_bind(i, "<Button-1>",
                                                 lambda event, r=row, c=col, cid=piece_canva: self.make_move(r, c, cid))

    def receive_start(self, start_status):#aqui se encontra o receive start match
        print("Entrou no receive start")
        self.start_game()
        players = start_status.get_players()
        local_player_id = start_status.get_local_id()
        my_turn = self.board.start_match(players, local_player_id)
        game_state = self.board.game_status
        self.player1_label.config(text=f"Player 1 (Brown): {self.board.player1.name}")
        self.player2_label.config(text=f"Player 2 (Black): {self.board.player2.name}")
        if my_turn:
            all_pieces_back = self.board.get_all_pieces()
            all_pieces_back = all_pieces_back["player1"]
            all_pieces_canva = self.all_pieces
            for i in range(8, 16):
                piece_back = all_pieces_back[i]
                row = piece_back.position.row
                col = piece_back.position.col
                piece_canva = all_pieces_canva[i]
                self.canvas.tag_bind(piece_canva, "<Button-1>", lambda event, r=row, c=col, cid=piece_canva: self.make_move(r, c, cid))
        self.update_gui(game_state)

    def start_game(self):
        print("Entrou no start game")

        match_status = self.board.game_status
        game_state = self.board.game_status
        if match_status == 2 or match_status == 6:
            ##self.board.reset_game()
            game_state = self.board.game_status
        self.update_gui(game_state)

    def make_move(self, row: int, col: int, cid) -> None:
        """Fazer a jogada. Ação quando se clica em uma peça habilitada"""
        print(f"Entrou no make_move()")

        game_status = self.board.game_status

        if game_status == 5: # Waiting remote move
            print(f"Aguarde a jogada do outro jogador")
            return
        for i in self.all_pieces:
            if i != cid:
                self.canvas.tag_unbind(i, "<Button-1>")

        position_at_clicked = self.board.positions[row][col]

        if game_status == 3: # Waiting local move
            piece_at_clicked = position_at_clicked.piece

            if piece_at_clicked is None:
                print(f"Não existe peça nessa posição. Posição: ({row},{col})")
                return

            local_pieces = self.board.player1.pieces
            if piece_at_clicked not in local_pieces:
                print("Essa peça não é sua")
                return

            print(f"Peça na posição ({row}, {col}):", piece_at_clicked)

            #self.clear_selection_highlight() # Retira marcações de tiles
            self.board.selected_position = position_at_clicked  # Guarda origem no modelo
            #self.hightlight_selected_tile(row, col) # Marca tile escolhido

            possible_moves = self.board.get_possible_moves(position_at_clicked)  # Positions válidas
            possible_coords = [(pos.row, pos.col) for pos in possible_moves] # Tuplas válidas
            print(f"Coordenadas possíveis para se mover:{possible_coords}")
            if possible_coords: #Se lista de movimentos possíveis tem algo
                self.board.game_status = 4
                print(f"self.board.selected_position: {self.board.selected_position}")
                #self.enable_possible_destinations(possible_coords)

        elif game_status == 4: # Ocurring local move
            origin = self.board.selected_position
            if not origin:
                print("Nenhuma peça selecionada.")
                return

            destination = position_at_clicked

            self.board.move_piece(origin, destination) #Move a peça para posição selecionada
            self.board.selected_position = None #Reseta posição anterior
            self.board.game_status = 5 # Waiting remote move

            #self.clear_selection_highlight()
            self.update_gui()

    def receive_withdrawal_notification(self):
        self.board.receive_withdrawal_notification()
        game_state = self.board.match_status()
        self.update_gui(game_state)
        #self.board.switch_turn()