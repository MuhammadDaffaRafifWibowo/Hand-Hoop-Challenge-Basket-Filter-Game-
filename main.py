import cv2
import mediapipe as mp
import numpy as np
import time
import random
import math

try:
    import pygame
    SOUND_ENABLED = True
except ImportError:
    SOUND_ENABLED = False
    print("⚠️ Pygame not installed. Sound effects disabled.")
    print("Install with: pip install pygame")


class HandHoopChallenge:
    def __init__(self):
        # Game Configuration
        self.WINDOW_WIDTH = 1280
        self.WINDOW_HEIGHT = 720
        self.ROUND_TIME = 60
        self.MIN_TARGET = 8
        self.MAX_TARGET = 20
        self.BALL_RADIUS = 30
        self.HOOP_X = int(self.WINDOW_WIDTH * 0.8)
        self.HOOP_Y = int(self.WINDOW_HEIGHT * 0.25)
        self.HOOP_RADIUS = 60
        self.GRAVITY = 0.5
        self.THREE_POINT_LINE = self.WINDOW_WIDTH * 0.4
        self.VELOCITY_MULTIPLIER = 1.5
        
        # Game State
        self.reset_game()
        
        # MediaPipe Setup
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        # Hand tracking variables
        self.last_hand_pos = None
        self.hand_velocity = {'x': 0, 'y': 0}
        self.hand_closed = False
        
        # Sound setup
        if SOUND_ENABLED:
            pygame.mixer.init()
            self.setup_sounds()
        
        # Camera setup
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.WINDOW_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.WINDOW_HEIGHT)
        
        # Confetti particles
        self.confetti = []

    def reset_game(self):
        """Reset game state"""
        self.game_state = 'start'  # 'start', 'playing', 'game_over'
        self.score = 0
        self.target_score = random.randint(self.MIN_TARGET, self.MAX_TARGET)
        self.round_num = 1
        self.time_left = self.ROUND_TIME
        self.start_time = None
        
        # Ball state
        self.ball = None
        self.flying_balls = []
        self.spawn_ball()  # Spawn initial ball
        
    def spawn_ball(self):
        """Spawn a new ball at the center of the screen"""
        self.ball = {
            'x': self.WINDOW_WIDTH // 2,
            'y': self.WINDOW_HEIGHT // 2,
            'vx': 0,
            'vy': 0,
            'held': False,
            'zone': 2
        }
        
    def setup_sounds(self):
        pass
    
    def play_sound(self, sound_type):
        if not SOUND_ENABLED:
            return
        
        try:
            # beep sounds
            sample_rate = 22050
            duration = 0.1
            
            if sound_type == 'throw':
                frequency = 200
            elif sound_type == 'score':
                frequency = 600
                duration = 0.3
            elif sound_type == 'win':
                # Play a melody
                for freq in [523, 659, 784]:
                    samples = np.sin(2 * np.pi * freq * np.linspace(0, 0.15, int(sample_rate * 0.15)))
                    sound = np.array(samples * 32767, dtype=np.int16)
                    stereo_sound = np.column_stack((sound, sound))
                    sound_obj = pygame.sndarray.make_sound(stereo_sound)
                    sound_obj.play()
                    time.sleep(0.15)
                return
            elif sound_type == 'lose':
                frequency = 150
                duration = 0.5
            else:
                return
            
            samples = np.sin(2 * np.pi * frequency * np.linspace(0, duration, int(sample_rate * duration)))
            sound = np.array(samples * 32767, dtype=np.int16)
            stereo_sound = np.column_stack((sound, sound))
            sound_obj = pygame.sndarray.make_sound(stereo_sound)
            sound_obj.play()
        except Exception as e:
            pass
    
    def calculate_hand_center(self, landmarks):
        """Kalkulasikan tengah tangan berdasarkan landmark"""
        palm_base = landmarks[0]
        return {
            'x': int(palm_base.x * self.WINDOW_WIDTH),
            'y': int(palm_base.y * self.WINDOW_HEIGHT)
        }
    
    def detect_hand_closed(self, landmarks):
        """deteksi apakah tangan tertutup (kepal)"""
        palm_base = landmarks[0]
        finger_tips = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky
        
        closed_count = 0
        for tip in finger_tips:
            distance = math.sqrt(
                (landmarks[tip].x - palm_base.x) ** 2 +
                (landmarks[tip].y - palm_base.y) ** 2
            )
            if distance < 0.15:
                closed_count += 1
        
        return closed_count >= 3
    
    def draw_hand_landmarks(self, frame, landmarks):
        """Gambar landmark tangan"""
        h, w, _ = frame.shape
        
        # Draw connections
        connections = [
            [0, 1], [1, 2], [2, 3], [3, 4],
            [0, 5], [5, 6], [6, 7], [7, 8],
            [0, 9], [9, 10], [10, 11], [11, 12],
            [0, 13], [13, 14], [14, 15], [15, 16],
            [0, 17], [17, 18], [18, 19], [19, 20],
            [5, 9], [9, 13], [13, 17]
        ]
        
        for connection in connections:
            start_idx, end_idx = connection
            start_point = landmarks[start_idx]
            end_point = landmarks[end_idx]
            
            start_pos = (int(start_point.x * w), int(start_point.y * h))
            end_pos = (int(end_point.x * w), int(end_point.y * h))
            
            cv2.line(frame, start_pos, end_pos, (0, 255, 0), 3)
        
        # Draw points
        for idx, landmark in enumerate(landmarks):
            x = int(landmark.x * w)
            y = int(landmark.y * h)
            color = (0, 255, 0) if idx == 0 else (255, 255, 255)
            cv2.circle(frame, (x, y), 5, color, -1)
            cv2.circle(frame, (x, y), 5, (0, 0, 0), 2)
    
    def reset_game(self):
        """Reset game state"""
        self.game_state = 'start'  # 'start', 'playing', 'game_over'
        self.score = 0
        self.target_score = random.randint(self.MIN_TARGET, self.MAX_TARGET)
        self.round_num = 1
        self.time_left = self.ROUND_TIME
        self.start_time = None
        
        # Ball state
        self.ball = None
        self.flying_balls = []
        self.spawn_ball()  # Spawn initial ball
        
    def spawn_ball(self):
        """Spawn a new ball at the center of the screen"""
        self.ball = {
            'x': self.WINDOW_WIDTH // 2,
            'y': self.WINDOW_HEIGHT // 2,
            'vx': 0,
            'vy': 0,
            'held': False,
            'zone': 2
        }
        
    def setup_sounds(self):
        pass
    
    def play_sound(self, sound_type):
        if not SOUND_ENABLED:
            return
        
        try:
            # beep sounds
            sample_rate = 22050
            duration = 0.1
            
            if sound_type == 'throw':
                frequency = 200
            elif sound_type == 'score':
                frequency = 600
                duration = 0.3
            elif sound_type == 'win':
                # Play a melody
                for freq in [523, 659, 784]:
                    samples = np.sin(2 * np.pi * freq * np.linspace(0, 0.15, int(sample_rate * 0.15)))
                    sound = np.array(samples * 32767, dtype=np.int16)
                    stereo_sound = np.column_stack((sound, sound))
                    sound_obj = pygame.sndarray.make_sound(stereo_sound)
                    sound_obj.play()
                    time.sleep(0.15)
                return
            elif sound_type == 'lose':
                frequency = 150
                duration = 0.5
            else:
                return
            
            samples = np.sin(2 * np.pi * frequency * np.linspace(0, duration, int(sample_rate * duration)))
            sound = np.array(samples * 32767, dtype=np.int16)
            stereo_sound = np.column_stack((sound, sound))
            sound_obj = pygame.sndarray.make_sound(stereo_sound)
            sound_obj.play()
        except Exception as e:
            pass
    
    def calculate_hand_center(self, landmarks):
        """Kalkulasikan tengah tangan berdasarkan landmark"""
        palm_base = landmarks[0]
        return {
            'x': int(palm_base.x * self.WINDOW_WIDTH),
            'y': int(palm_base.y * self.WINDOW_HEIGHT)
        }
    
    def detect_hand_closed(self, landmarks):
        """deteksi apakah tangan tertutup (kepal)"""
        palm_base = landmarks[0]
        finger_tips = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky
        
        closed_count = 0
        for tip in finger_tips:
            distance = math.sqrt(
                (landmarks[tip].x - palm_base.x) ** 2 +
                (landmarks[tip].y - palm_base.y) ** 2
            )
            if distance < 0.15:
                closed_count += 1
        
        return closed_count >= 3
    
    def draw_hand_landmarks(self, frame, landmarks):
        """Gambar landmark tangan"""
        h, w, _ = frame.shape
        
        # Draw connections
        connections = [
            [0, 1], [1, 2], [2, 3], [3, 4],
            [0, 5], [5, 6], [6, 7], [7, 8],
            [0, 9], [9, 10], [10, 11], [11, 12],
            [0, 13], [13, 14], [14, 15], [15, 16],
            [0, 17], [17, 18], [18, 19], [19, 20],
            [5, 9], [9, 13], [13, 17]
        ]
        
        for connection in connections:
            start_idx, end_idx = connection
            start_point = landmarks[start_idx]
            end_point = landmarks[end_idx]
            
            start_pos = (int(start_point.x * w), int(start_point.y * h))
            end_pos = (int(end_point.x * w), int(end_point.y * h))
            
            cv2.line(frame, start_pos, end_pos, (0, 255, 0), 3)
        
        # Draw points
        for idx, landmark in enumerate(landmarks):
            x = int(landmark.x * w)
            y = int(landmark.y * h)
            color = (0, 255, 0) if idx == 0 else (255, 255, 255)
            cv2.circle(frame, (x, y), 5, color, -1)
            cv2.circle(frame, (x, y), 5, (0, 0, 0), 2)