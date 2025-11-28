import cv2
import mediapipe as mp
import visualizer as viz
import game_logic as logic
from game_objects import GameState
from utils import is_hand_closed
from sound_manager import SoundManager

def main():
    """ Fungsi utama untuk inisialisasi kamera, MediaPipe, dan menjalankan Game Loop. """
    # 1. Setup MediaPipe
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        max_num_hands=1,
        model_complexity=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    
    # 2. Setup Kamera
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    # 5. SETUP AUDIO 
    sound_mgr = SoundManager()
    # Pastikan Ada file suara .wav di folder yang sama atau folder assets
    # path suara:
    sound_mgr.load_sound('score', 'goalSound.wav') 
    sound_mgr.load_sound('win', 'win.wav')
    sound_mgr.load_sound('lose', 'lose.wav')
    
    # 4. Inisialisasi Game State
    game_state = GameState()
    
    print("=" * 50)
    print("Hand Hoop Challenge - Modular Version")
    print("=" * 50)
    print("Tekan SPASI untuk mulai/restart")
    print("Tekan Q untuk keluar")
    
    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Mirror frame
            frame = cv2.flip(frame, 1)
            height, width, _ = frame.shape
            
            # Deteksi Tangan
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)
            
            # Update data tangan ke GameState
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Ambil posisi ujung jari tengah (untuk grabbing)
                    middle_tip = hand_landmarks.landmark[12]
                    game_state.middle_finger_tip = {
                        'x': middle_tip.x, 'y': middle_tip.y, 'z': middle_tip.z
                    }
                    
                    palm = hand_landmarks.landmark[0]
                    game_state.palm_center = {'x': palm.x, 'y': palm.y}
                    
                    # Deteksi kepalan
                    game_state.is_closed_hand = is_hand_closed(hand_landmarks)
                    
                    # Gambar tangan
                    # viz.draw_hand_landmarks(frame, hand_landmarks, width, height, game_state.is_closed_hand)
            else:
                game_state.middle_finger_tip = None
                game_state.is_closed_hand = False
            
            # Update Logika Game (hanya jika sedang main dan tidak freeze frame score)
            if game_state.is_playing:
                if not game_state.score_effect_active:
                    # PASS sound_mgr ke fungsi update_game
                    logic.update_game(game_state, sound_manager=sound_mgr)
                
                # Render Elemen Game
                # Ground
                ground_y = int(game_state.ground * height)
                cv2.line(frame, (0, ground_y), (width, ground_y), (255, 255, 255), 2)
                
                viz.draw_scoring_zones(frame, game_state, width, height)
                viz.draw_hoop(frame, game_state.hoop, width, height, game_state.debug_mode)
                
                for ball in game_state.balls:
                    viz.draw_ball(frame, ball, width, height, game_state)
                    
                viz.draw_ui(frame, game_state, width, height)
                
                # Capture freeze frame untuk efek skor
                if game_state.score_effect_active and game_state.freeze_frame is None:
                    game_state.freeze_frame = frame.copy()
                
                viz.draw_score_effect(frame, game_state, width, height)
            
            # Render Layar Menu
            if game_state.show_start_screen:
                viz.draw_start_screen(frame, width, height)
            elif game_state.show_game_over:
                viz.draw_game_over_screen(frame, width, height, game_state)
            
            cv2.imshow('Hand Hoop Challenge', frame)
            
            # Input Control
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                break
            elif key == ord(' '):
                if game_state.show_start_screen or game_state.show_game_over:
                    logic.start_game(game_state)
                
    finally:
        cap.release()
        cv2.destroyAllWindows()
        sound_mgr.cleanup()

if __name__ == "__main__":
    main()