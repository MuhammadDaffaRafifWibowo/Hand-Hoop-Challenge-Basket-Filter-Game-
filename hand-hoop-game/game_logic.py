import time
import random
from game_objects import Ball
from utils import calculate_distance

def start_game(game_state):
    """Memulai sesi permainan baru dan mereset variabel."""
    game_state.score = 0
    game_state.target = random.randint(5, 15)
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

def end_game(game_state):
    """Mengakhiri permainan dan menentukan kondisi menang/kalah."""
    game_state.is_playing = False
    game_state.show_game_over = True
    game_state.win = game_state.score >= game_state.target
    
    if game_state.win:
        print(f"🎉 MENANG! Skor akhir: {game_state.score}")
    else:
        print(f"😢 Kalah. Skor akhir: {game_state.score}")

def spawn_ball(game_state):
    """Memunculkan bola baru jika jumlah bola di layar masih sedikit."""
    if len(game_state.balls) == 0:
        ball = Ball(x=0.7, y=game_state.ground)
        game_state.balls.append(ball)

def update_game(game_state, sound_manager=None):
    """
    Loop utama logika game: Fisika, interaksi tangan, dan scoring.
    Versi yang ditingkatkan untuk kemudahan lemparan.
    """
    now = time.time()
    
    # 1. Spawning Mechanics
    if now - game_state.last_spawn_time > 3 and len(game_state.balls) < 5:
        spawn_ball(game_state)
        game_state.last_spawn_time = now
    
    # 2. Hand Grab Mechanics (Mengambil bola) - DIPERBESAR RADIUS
    if game_state.is_closed_hand and game_state.middle_finger_tip and not game_state.holding_ball:
        for ball in game_state.balls:
            if not ball.thrown and not ball.grabbed:
                dist = calculate_distance(game_state.middle_finger_tip, {'x': ball.x, 'y': ball.y})
                if dist < 0.15: # Radius pengambilan DIPERBESAR dari 0.1 ke 0.15
                    game_state.holding_ball = ball
                    ball.grabbed = True
                    ball.on_ground = False
                    ball.throw_start_pos = {'x': ball.x, 'y': ball.y}
                    ball.grab_time = now  # Simpan waktu grab
                    break
    
    # 3. Throw Mechanics (Melempar bola) - DITINGKATKAN
    # Tambahkan delay 0.2 detik sebelum bola bisa dilepas (mencegah lepas tidak sengaja)
    if not game_state.is_closed_hand and game_state.holding_ball:
        ball = game_state.holding_ball
        
        # Cek apakah sudah dipegang minimal 0.2 detik
        hold_duration = now - ball.grab_time if hasattr(ball, 'grab_time') else 999
        
        if hold_duration > 0.2:  # Hanya lempar jika sudah dipegang cukup lama
            # Menghitung kecepatan lempar berdasarkan pergerakan terakhir
            if ball.prev_x is not None:
                # Kecepatan lempar DITINGKATKAN untuk lebih responsif
                ball.vx = (ball.x - ball.prev_x) * 4.5  # Ditingkatkan dari 3 ke 4.5
                ball.vy = (ball.y - ball.prev_y) * 4.5 - 0.04  # Ditingkatkan dari 3 ke 4.5, boost awal dari -0.03 ke -0.04
            
            ball.thrown = True
            ball.grabbed = False
            game_state.holding_ball = None
    
    # 4. Update Posisi Bola yang Dipegang - SMOOTHING DITINGKATKAN
    if game_state.holding_ball and game_state.middle_finger_tip:
        ball = game_state.holding_ball
        ball.prev_x = ball.x
        ball.prev_y = ball.y
        
        # Smoothing untuk mencegah gerakan terlalu cepat/jittery
        target_x = game_state.middle_finger_tip['x']
        target_y = game_state.middle_finger_tip['y']
        
        # Interpolasi lebih halus (0.3 = 30% ke target, 70% posisi lama)
        ball.x = ball.x * 0.3 + target_x * 0.7
        ball.y = ball.y * 0.3 + target_y * 0.7
    
    # 5. Physics Update untuk semua bola
    balls_to_keep = []
    for ball in game_state.balls:
        # A. Bola menggelinding di tanah
        if ball.on_ground and not ball.thrown and not ball.grabbed:
            ball.vx += ball.roll_direction * 0.0005
            ball.vx *= 0.98 # Friction
            ball.x += ball.vx
            
            # Pantulan dinding kiri/kanan saat menggelinding
            if ball.x < 0.05 or ball.x > 0.95:
                ball.x = max(0.05, min(0.95, ball.x))
                ball.roll_direction *= -1
                ball.vx *= -0.7

        # B. Bola sedang dilempar (di udara) - GRAVITY DISESUAIKAN
        if ball.thrown:
            ball.vy += 0.0018 # Gravity DIKURANGI dari 0.002 agar lemparan lebih smooth
            ball.x += ball.vx
            ball.y += ball.vy
            
            # Wall Collision (Kiri/Kanan)
            if ball.x < 0.05 or ball.x > 0.95:
                ball.x = max(0.05, min(0.95, ball.x))
                ball.vx *= -0.6
            
            # Ceiling Collision
            if ball.y < 0.05:
                ball.y = 0.05
                ball.vy *= -0.5
            
            # Floor Collision
            if ball.y > game_state.ground:
                ball.y = game_state.ground
                ball.vy *= -0.6
                ball.vx *= 0.8
                
                # Jika pantulan sangat kecil, anggap berhenti
                if abs(ball.vy) < 0.01:
                    ball.thrown = False
                    ball.on_ground = True
                    ball.vy = 0
            
            # C. Scoring System
            dist_to_hoop = calculate_distance({'x': ball.x, 'y': ball.y}, game_state.hoop)
            inside_ring = dist_to_hoop < game_state.hoop['radius']
            was_inside_ring = ball.entered_from_top
            
            if inside_ring and ball.thrown:
                if not was_inside_ring:
                    if now - game_state.last_score_time > 0.3:
                        _handle_score(game_state, ball, now, sound_manager) 
                ball.entered_from_top = True
            else:
                ball.entered_from_top = False
        
        balls_to_keep.append(ball)
    
    game_state.balls = balls_to_keep
    
    # 6. Timer Update
    if game_state.game_start_time:
        elapsed = time.time() - game_state.game_start_time
        game_state.time_left = max(0, 60 - int(elapsed))
        if game_state.time_left <= 0:
            end_game(game_state, sound_manager)

def _handle_score(game_state, ball, now, sound_manager=None):
    """Helper function internal untuk memproses penambahan poin."""
    points = 2
    throw_x = 0
    
    if ball.throw_start_pos:
        throw_x = ball.throw_start_pos['x']
        if throw_x >= game_state.zone_divider:
            points = 3
    
    game_state.score += points
    game_state.last_score_time = now
    
    # Trigger efek visual
    game_state.score_effect_active = True
    game_state.score_effect_start_time = now
    game_state.score_effect_points = points
    game_state.score_effect_position = {'x': ball.x, 'y': ball.y}
    
    if sound_manager:
        sound_manager.play('score')
    
    print(f"🏀 SCORE! +{points} poin! Total: {game_state.score}")

def end_game(game_state, sound_manager=None):
    game_state.is_playing = False
    game_state.show_game_over = True
    game_state.win = game_state.score >= game_state.target
    
    # 🔊 Mainkan suara menang/kalah
    if sound_manager:
        if game_state.win:
            sound_manager.play('win')
        else:
            sound_manager.play('lose')