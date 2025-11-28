import random
import time

class Ball:
    """
    Merepresentasikan objek bola basket dalam permainan.
    Menyimpan posisi, kecepatan, dan status bola.
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.radius = 0.03
        
        # Status Flags
        self.thrown = False
        self.grabbed = False
        self.on_ground = True
        self.scored = False
        self.roll_direction = 1 if random.random() > 0.5 else -1
        
        # Tracking Physics
        self.prev_x = None
        self.prev_y = None
        self.prev_positions = []  
        self.throw_start_pos = None  # Posisi saat lemparan dimulai
        
        # Scoring Logic Flags
        self.entered_from_top = False  # Bola masuk ring dari atas
        self.passed_through = False
        self.prev_entered_from_top = False

class GameState:
    """
    Menyimpan seluruh status global permainan (Score, Waktu, Konfigurasi Level).
    """
    def __init__(self):
        # Skor dan Waktu
        self.score = 0
        self.target = random.randint(10, 15)  # Target poin untuk menang
        self.time_left = 60
        
        # Status Permainan
        self.is_playing = False
        self.game_start_time = None
        self.show_start_screen = True
        self.show_game_over = False
        self.win = False
        
        # Tracking Tangan
        self.hand_position = None
        self.middle_finger_tip = None
        self.palm_center = None
        self.is_closed_hand = False
        
        # Objek Game
        self.balls = []
        self.holding_ball = None
        self.last_spawn_time = time.time()
        
        # Konfigurasi Arena
        self.hoop = {'x': 0.08, 'y': 0.25, 'radius': 0.055}
        self.zone_divider = 0.50  # Garis pemisah zona 2pt dan 3pt
        self.ground = 0.85
        
        # Efek Visual & Debug
        self.debug_mode = False
        self.last_score_time = 0
        
        # Efek Scoring
        self.score_effect_active = False
        self.score_effect_start_time = 0
        self.score_effect_points = 0
        self.score_effect_position = None
        self.freeze_frame = None