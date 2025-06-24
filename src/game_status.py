from enum import Enum

class GameStatus(Enum):
    NO_MATCH = 1              # Partida não iniciada
    FINISHED = 2              # Partida finalizada
    WAITING_LOCAL_MOVE = 3    # Esperando jogada do jogador local
    OCCURRING_LOCAL_MOVE = 4  # Jogada local em andamento
    WAITING_REMOTE_MOVE = 5   # Esperando jogada do jogador remoto
    ABANDONED = 6             # Partida abandonada pelo oponente