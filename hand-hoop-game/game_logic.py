import time
from game_objects import Ball
from utils import calculate_distance

def start_game(game_state):
    """Memulai sesi permainan baru dan mereset variabel."""
    game_state.score = 0
    game_state.target = 15
    game_state.time_left = 60
    game_state.is_playing = True
    game_state.balls = []
    game_state.holding_ball = None
    game_state.last_spawn_time = time.time()
    game_state.game_start_time = time.time()
    game_state.show_start_screen = False
    game_state.show_game_over = False
    game_state.last_score_time = 0
    game_state.score_effect_active = False
    game_state.freeze_frame = None
    
    spawn_ball(game_state)
    print(f"🎮 Game dimulai! Target: {game_state.target} poin dalam 60 detik")