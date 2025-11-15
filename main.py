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
    
    def draw_hoop(self, frame):
        """Draw basketball hoop"""
        # Backboard
        cv2.rectangle(frame, 
                     (self.HOOP_X - 10, self.HOOP_Y - 100),
                     (self.HOOP_X + 10, self.HOOP_Y + 20),
                     (255, 255, 255), -1)
        cv2.rectangle(frame,
                     (self.HOOP_X - 10, self.HOOP_Y - 100),
                     (self.HOOP_X + 10, self.HOOP_Y + 20),
                     (0, 0, 0), 3)
        
        # Hoop ring
        cv2.circle(frame, (self.HOOP_X, self.HOOP_Y), 
                  self.HOOP_RADIUS, (35, 107, 255), 8)
        cv2.circle(frame, (self.HOOP_X, self.HOOP_Y),
                  self.HOOP_RADIUS - 10, (35, 107, 255, 50), 4)
        
        # Net
        for i in range(8):
            angle = (i / 8) * math.pi * 2
            x1 = int(self.HOOP_X + math.cos(angle) * self.HOOP_RADIUS)
            y1 = int(self.HOOP_Y + math.sin(angle) * self.HOOP_RADIUS)
            x2 = int(self.HOOP_X + math.cos(angle) * (self.HOOP_RADIUS - 20))
            y2 = self.HOOP_Y + 40
            cv2.line(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)
    
    def draw_ball(self, frame, ball):
        """Draw basketball"""
        x, y = int(ball['x']), int(ball['y'])
        
        # Ball shadow
        cv2.circle(frame, (x, y), self.BALL_RADIUS, (0, 0, 0), -1)
        
        # Ball gradient effect (using circles)
        for r in range(self.BALL_RADIUS, 0, -3):
            color_intensity = int(255 - (self.BALL_RADIUS - r) * 3)
            color = (66, 140, min(255, color_intensity))
            cv2.circle(frame, (x, y), r, color, -1)
        
        # Basketball lines
        cv2.line(frame, (x - self.BALL_RADIUS, y), (x + self.BALL_RADIUS, y), (0, 0, 0), 2)
        cv2.line(frame, (x, y - self.BALL_RADIUS), (x, y + self.BALL_RADIUS), (0, 0, 0), 2)
        
        # Highlight if held
        if ball.get('held', False):
            cv2.circle(frame, (x, y), self.BALL_RADIUS + 3, (0, 255, 0), 3)
    
    def handle_ball_interaction(self, hand_center, is_closed):
        """Handle picking up and throwing the ball"""
        if not self.ball:
            return
        
        # Pick up ball
        if not self.ball['held'] and is_closed and not self.hand_closed:
            dist = math.sqrt((hand_center['x'] - self.ball['x'])**2 + 
                           (hand_center['y'] - self.ball['y'])**2)
            if dist < self.BALL_RADIUS + 50:
                self.ball['held'] = True
        
        # Move ball with hand
        elif self.ball['held']:
            if is_closed:
                self.ball['x'] = hand_center['x']
                self.ball['y'] = hand_center['y']
            elif self.hand_closed:  # Just released
                # Throw ball
                zone = 3 if hand_center['x'] < self.THREE_POINT_LINE else 2
                self.ball['held'] = False
                self.ball['vx'] = self.hand_velocity['x']
                self.ball['vy'] = self.hand_velocity['y']
                self.ball['zone'] = zone
                self.ball['scored'] = False
                self.flying_balls.append(dict(self.ball))
                self.ball = None  # Remove held ball
                self.play_sound('throw')
        
        self.hand_closed = is_closed
    
    def update_balls(self, frame):
        """Update physics for flying balls"""
        balls_to_remove = []
        
        for i, ball in enumerate(self.flying_balls):
            # Apply gravity
            ball['vy'] += self.GRAVITY
            ball['x'] += ball['vx']
            ball['y'] += ball['vy']
            
            # Check if ball scores
            dist_to_hoop = math.sqrt((ball['x'] - self.HOOP_X)**2 + 
                                    (ball['y'] - self.HOOP_Y)**2)
            
            if (dist_to_hoop < self.HOOP_RADIUS and 
                ball['vy'] > 0 and 
                not ball.get('scored', False)):
                
                ball['scored'] = True
                points = ball['zone']
                self.score += points
                self.play_sound('score')
                
                # Draw score effect
                cv2.putText(frame, f"+{points}", 
                           (self.HOOP_X - 30, self.HOOP_Y - 50),
                           cv2.FONT_HERSHEY_DUPLEX, 2,
                           (0, 255, 0) if points == 2 else (0, 165, 255),
                           3)
                
                # Spawn new ball at center
                self.spawn_ball()
                
                # Check win condition
                if self.score >= self.target_score:
                    self.game_state = 'game_over'
                    self.game_result = 'win'
                    self.play_sound('win')
                    self.create_confetti()
            
            # Remove ball if out of bounds
            if ball['y'] > self.WINDOW_HEIGHT + 100:
                balls_to_remove.append(i)
        
        # Remove out of bounds balls
        for i in reversed(balls_to_remove):
            self.flying_balls.pop(i)
    
    def create_confetti(self):
        """Create confetti particles"""
        colors = [(107, 76, 255), (196, 77, 255), (255, 107, 53), 
                 (61, 207, 255), (111, 207, 107)]
        
        for _ in range(100):
            self.confetti.append({
                'x': self.WINDOW_WIDTH // 2,
                'y': self.WINDOW_HEIGHT // 2,
                'vx': random.uniform(-10, 10),
                'vy': random.uniform(-10, -5),
                'color': random.choice(colors),
                'size': random.randint(5, 12)
            })
    
    def update_confetti(self, frame):
        """Update and draw confetti"""
        confetti_to_remove = []
        
        for i, particle in enumerate(self.confetti):
            particle['vy'] += 0.3
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            
            if particle['y'] < self.WINDOW_HEIGHT:
                cv2.rectangle(frame,
                            (int(particle['x']), int(particle['y'])),
                            (int(particle['x']) + particle['size'], 
                             int(particle['y']) + particle['size']),
                            particle['color'], -1)
            else:
                confetti_to_remove.append(i)
        
        for i in reversed(confetti_to_remove):
            self.confetti.pop(i)
    
    def draw_ui(self, frame):
        """Draw game UI"""
        # Semi-transparent overlay for UI
        overlay = frame.copy()
        
        # Score panel
        cv2.rectangle(overlay, (10, 10), (250, 160), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        cv2.putText(frame, "SCORE", (20, 40),
               cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 215, 0), 2)
        cv2.putText(frame, f"Current: {self.score}", (20, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, f"Target: {self.target_score}", (20, 100),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, f"Round: {self.round_num}", (20, 130),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Timer panel
        overlay = frame.copy()
        cv2.rectangle(overlay, (self.WINDOW_WIDTH - 180, 10), 
                     (self.WINDOW_WIDTH - 10, 100), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        timer_color = (107, 107, 255) if self.time_left > 10 else (76, 76, 255)
        cv2.putText(frame, "TIME", (self.WINDOW_WIDTH - 160, 40),
               cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 215, 0), 2)
        cv2.putText(frame, str(self.time_left), (self.WINDOW_WIDTH - 130, 85),
               cv2.FONT_HERSHEY_DUPLEX, 1.5, timer_color, 3)
        
        # Zone indicator
        if self.last_hand_pos:
            zone_text = "3-POINT ZONE" if self.last_hand_pos['x'] < self.THREE_POINT_LINE else "2-POINT ZONE"
            zone_color = (0, 165, 255) if "3-POINT" in zone_text else (0, 255, 0)
            
            text_size = cv2.getTextSize(zone_text, cv2.FONT_HERSHEY_DUPLEX, 0.8, 2)[0]
            text_x = (self.WINDOW_WIDTH - text_size[0]) // 2
            
            overlay = frame.copy()
            cv2.rectangle(overlay, (text_x - 20, self.WINDOW_HEIGHT - 70),
                         (text_x + text_size[0] + 20, self.WINDOW_HEIGHT - 20),
                         (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
            
            cv2.putText(frame, zone_text, (text_x, self.WINDOW_HEIGHT - 35),
                       cv2.FONT_HERSHEY_DUPLEX, 0.8, zone_color, 2)
    
    def draw_start_screen(self, frame):
        """Draw start screen"""
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (self.WINDOW_WIDTH, self.WINDOW_HEIGHT),
                     (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)
        
        # Title
        cv2.putText(frame, "HAND HOOP CHALLENGE", 
               (self.WINDOW_WIDTH // 2 - 350, 150),
               cv2.FONT_HERSHEY_DUPLEX, 1.5, (255, 215, 0), 3)
        
        # Instructions
        instructions = [
            "Cara Bermain:",
            "",
            "1. Tutup tangan (kepal) untuk ambil bola",
            "2. Buka tangan cepat untuk melempar",
            "3. 2-Point Zone: Dekat ring (kanan)",
            "4. 3-Point Zone: Jauh dari ring (kiri)",
            "5. Capai target poin sebelum waktu habis!",
            "",
            "Tekan SPASI untuk mulai"
        ]
        
        y_offset = 250
        for i, text in enumerate(instructions):
            color = (255, 215, 0) if i == 0 else (255, 255, 255)
            font_scale = 1.0 if i == 0 else 0.7
            thickness = 2 if i == 0 else 1
            
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 
                                       font_scale, thickness)[0]
            text_x = (self.WINDOW_WIDTH - text_size[0]) // 2
            
            cv2.putText(frame, text, (text_x, y_offset + i * 40),
                       cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)
        
        # Ball respawn info
        cv2.putText(frame, "Bola akan muncul di tengah setelah setiap goal!", 
                   (self.WINDOW_WIDTH // 2 - 350, self.WINDOW_HEIGHT - 100),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (107, 255, 107), 2)
    
    def draw_game_over_screen(self, frame):
        """Draw game over screen"""
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (self.WINDOW_WIDTH, self.WINDOW_HEIGHT),
                     (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)
        
        if self.game_result == 'win':
            title = "VICTORY!"
            color = (0, 255, 0)
            message = f"Amazing! You scored {self.score} points!"
        else:
            title = "TIME UP!"
            color = (76, 76, 255)
            message = f"So close! You scored {self.score} points!"
        
        # Title
        title_size = cv2.getTextSize(title, cv2.FONT_HERSHEY_DUPLEX, 2.5, 4)[0]
        title_x = (self.WINDOW_WIDTH - title_size[0]) // 2
        cv2.putText(frame, title, (title_x, 200),
               cv2.FONT_HERSHEY_DUPLEX, 2.5, color, 4)
        
        # Message
        message_size = cv2.getTextSize(message, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 2)[0]
        message_x = (self.WINDOW_WIDTH - message_size[0]) // 2
        cv2.putText(frame, message, (message_x, 300),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
        
        # Score details
        details = f"Target: {self.target_score} | Your Score: {self.score}"
        details_size = cv2.getTextSize(details, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)[0]
        details_x = (self.WINDOW_WIDTH - details_size[0]) // 2
        cv2.putText(frame, details, (details_x, 370),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
        
        # Restart instruction
        restart_text = "Tekan SPASI untuk main lagi | ESC untuk keluar"
        restart_size = cv2.getTextSize(restart_text, cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2)[0]
        restart_x = (self.WINDOW_WIDTH - restart_size[0]) // 2
        cv2.putText(frame, restart_text, (restart_x, self.WINDOW_HEIGHT - 100),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 215, 0), 2)
    
    def run(self):
        """Main game loop"""
        print("🏀 Hand Hoop Challenge - Python Version")
        print("=" * 50)
        print("Controls:")
        print("  SPACE - Start/Restart game")
        print("  ESC   - Quit")
        print("=" * 50)
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process hand tracking
            results = self.hands.process(rgb_frame)
            
            if self.game_state == 'playing':
                # Update timer
                if self.start_time is None:
                    self.start_time = time.time()
                
                elapsed = int(time.time() - self.start_time)
                self.time_left = max(0, self.ROUND_TIME - elapsed)
                
                if self.time_left == 0 and self.score < self.target_score:
                    self.game_state = 'game_over'
                    self.game_result = 'lose'
                    self.play_sound('lose')
                
                # Process hand detection
                if results.multi_hand_landmarks:
                    hand_landmarks = results.multi_hand_landmarks[0].landmark
                    hand_center = self.calculate_hand_center(hand_landmarks)
                    is_closed = self.detect_hand_closed(hand_landmarks)
                    
                    # Calculate velocity
                    if self.last_hand_pos:
                        self.hand_velocity['x'] = (hand_center['x'] - self.last_hand_pos['x']) * self.VELOCITY_MULTIPLIER
                        self.hand_velocity['y'] = (hand_center['y'] - self.last_hand_pos['y']) * self.VELOCITY_MULTIPLIER
                    
                    self.last_hand_pos = hand_center
                    
                    # Draw hand
                    self.draw_hand_landmarks(frame, hand_landmarks)
                    
                    # Handle ball interaction
                    self.handle_ball_interaction(hand_center, is_closed)
                
                # Update and draw game elements
                self.draw_hoop(frame)
                self.update_balls(frame)
                
                # Draw all balls
                for ball in self.flying_balls:
                    self.draw_ball(frame, ball)
                
                if self.ball:
                    self.draw_ball(frame, self.ball)
                
                self.draw_ui(frame)
            
            elif self.game_state == 'start':
                self.draw_start_screen(frame)
            
            elif self.game_state == 'game_over':
                self.update_confetti(frame)
                self.draw_game_over_screen(frame)
            
            # Show frame
            cv2.imshow('Hand Hoop Challenge', frame)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            
            if key == 27:  # ESC
                break
            elif key == 32:  # SPACE
                if self.game_state == 'start':
                    self.game_state = 'playing'
                    self.start_time = None
                elif self.game_state == 'game_over':
                    self.reset_game()
                    self.game_state = 'playing'
                    self.start_time = None
        
        # Cleanup
        self.cap.release()
        cv2.destroyAllWindows()
        self.hands.close()


if __name__ == "__main__":
    game = HandHoopChallenge()
    game.run()