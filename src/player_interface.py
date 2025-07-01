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

class PlayerInterface(DogPlayerInterface):
    def __init__(self):
        self.main_window = tk.Tk()  # Instancia a janela principal
        self.fill_main_window()  # Organiza a janela e cria os widgets
        self.board = Board()
        self.message_notification = None  # Variável para a mensagem de notificação
        self.draw_board()  # Desenha o tabuleiro inicial
        self.associate_canva()
        player_name = simpledialog.askstring(title="Player identification", prompt="Qual o seu nome?")
        self.dog_server_interface = DogActor()
        message = self.dog_server_interface.initialize(player_name, self)
        messagebox.showinfo(message=message)
        self.main_window.mainloop()  # Mantém a janela aberta
        self.local_player_id = None

    def associate_canva(self):
        all_pieces = self.board.get_all_pieces()
        #tem que fazer o restante da associação do próprio canva

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
        self.canvas.bind("<Button-1>", self.on_tile_click)

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
        print(game_state)
        self.draw_board()
        self.place_all_pieces()

    def draw_board(self):
        self.canvas.delete("all")
        colors = ["#C8AD7F", "#5C3A21"]  # light and dark brown
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                x1 = col * TILE_SIZE
                y1 = row * TILE_SIZE
                x2 = x1 + TILE_SIZE
                y2 = y1 + TILE_SIZE
                color = colors[(row + col) % 2]
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")

                # Placeholder pieces (can be removed or replaced)
                #if row < 3 and row > 0:
                #    self.canvas.create_oval(x1+10, y1+10, x2-10, y2-10, fill="#1C1C1C", tags="piece")
                #elif row > 4 and row < 7:
                #    self.canvas.create_oval(x1+10, y1+10, x2-10, y2-10, fill="#8B5E3C", tags="piece")
        
    def place_all_pieces(self):
        all_pieces = self.board.get_all_pieces()
        
        for owner, pieces in all_pieces.items():
            is_local_owner = owner == self.board.player1

            for piece in pieces:
                if piece.position is not None:
                    row = piece.position.row
                    col = piece.position.col

                    # Inverte a posição se for jogador remoto
                    if not is_local_owner:
                        row = BOARD_SIZE - 1 - row
                        col = BOARD_SIZE - 1 - col

                    x1 = col * TILE_SIZE + 10
                    y1 = row * TILE_SIZE + 10
                    x2 = x1 + TILE_SIZE - 20
                    y2 = y1 + TILE_SIZE - 20

                    # Cores fixas: player1 é sempre marrom, player2 é sempre preto
                    fill_color = "#8B5E3C" if owner == 'player1' else "#1C1C1C"
                    self.canvas.create_oval(x1, y1, x2, y2, fill=fill_color, tags="piece")

    def on_tile_click(self, event):
        col = event.x // TILE_SIZE
        row = event.y // TILE_SIZE
        print(f"Clicked on tile: ({row}, {col})")  # Placeholder for move logic

    ## Talvez seja diferente no nosso código
    def reset_board(self):
        self.draw_board()
        messagebox.showinfo("Reset", "Board has been reset.")
    
    def receive_move(self, a_move):
        self.board.receive_move(a_move)
        game_state = self.board.game_status
        self.update_gui(game_state)

    def start_match(self):
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
                    self.local_player_id = local_player_id
                    game_state = self.board.game_status
                    self.update_gui(game_state)
                    messagebox.showinfo(message=start_status.get_message())

    def receive_start(self, start_status):
        self.start_game()
        players = start_status.get_players()
        local_player_id = start_status.get_local_id()
        self.board.start_match(players, local_player_id)
        game_state = self.board.game_status
        self.update_gui(game_state)

    def start_game(self):
        match_status = self.board.game_status
        if match_status == 2 or match_status == 6:
            ##self.board.reset_game()
            game_state = self.board.game_status
            self.update_gui(game_state)
