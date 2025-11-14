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