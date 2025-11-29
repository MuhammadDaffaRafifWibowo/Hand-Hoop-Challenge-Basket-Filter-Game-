import time
from game_objects import Ball
from utils import calculate_distance

def start_game(game_state):
    """Memulai sesi permainan baru dan mereset semua variabel ke kondisi awal."""
    # Reset skor dan target
    game_state.score = 0
    game_state.target = 15
    game_state.time_left = 60
    
    # Status permainan
    game_state.is_playing = True
    game_state.balls = []  # Kosongkan daftar bola
    game_state.holding_ball = None  # Tidak memegang bola
    game_state.last_spawn_time = time.time()  # Waktu spawn terakhir
    game_state.game_start_time = time.time()  # Waktu mulai permainan
    
    # Status layar
    game_state.show_start_screen = False
    game_state.show_game_over = False
    
    # Reset efek score
    game_state.last_score_time = 0
    game_state.score_effect_active = False
    game_state.freeze_frame = None
    
    # Spawn bola pertama
    spawn_ball(game_state)
    print(f"🎮 Game dimulai! Target: {game_state.target} poin dalam 60 detik")

def end_game(game_state, sound_manager=None):
    """Mengakhiri permainan dan menentukan kondisi menang/kalah."""
    # Menghentikan permainan
    game_state.is_playing = False
    game_state.show_game_over = True
    
    # Menentukan apakah pemain menang atau kalah
    game_state.win = game_state.score >= game_state.target
    
    # Memutar suara sesuai hasil
    if sound_manager:
        if game_state.win:
            sound_manager.play('win')
            print(f"🎉 MENANG! Skor akhir: {game_state.score}")
        else:
            sound_manager.play('lose')
            print(f"😢 Kalah. Skor akhir: {game_state.score}")

def spawn_ball(game_state):
    """Memunculkan bola baru jika jumlah bola di layar masih sedikit."""
    # Hanya spawn bola jika tidak ada bola di layar
    if len(game_state.balls) == 0:
        # Buat bola baru di posisi x=70% layar, y=ground level
        ball = Ball(x=0.7, y=game_state.ground)
        game_state.balls.append(ball)

def update_game(game_state, sound_manager=None):
    """
    Loop utama logika game: Fisika, interaksi tangan, dan scoring.
    Fungsi ini dipanggil terus menerus selama permainan berlangsung.
    """
    now = time.time()
    
    # 1. Spawning Mechanics - spawn bola baru setiap 3 detik jika kurang dari 5 bola
    if now - game_state.last_spawn_time > 3 and len(game_state.balls) < 5:
        spawn_ball(game_state)
        game_state.last_spawn_time = now
    
    # 2. Hand Grab Mechanics - mengambil bola dengan tangan mengepal
    if game_state.is_closed_hand and game_state.middle_finger_tip and not game_state.holding_ball:
        for ball in game_state.balls:
            # Cek bola yang belum dilempar dan belum dipegang
            if not ball.thrown and not ball.grabbed:
                # Hitung jarak antara ujung jari tengah dan bola
                dist = calculate_distance(game_state.middle_finger_tip, {'x': ball.x, 'y': ball.y})
                if dist < 0.1:  # Radius pengambilan bola
                    game_state.holding_ball = ball
                    ball.grabbed = True
                    ball.on_ground = False
                    # Simpan posisi awal lemparan untuk perhitungan poin
                    ball.throw_start_pos = {'x': ball.x, 'y': ball.y}
                    break
    
    # 3. Throw Mechanics - melempar bola saat tangan terbuka
    if not game_state.is_closed_hand and game_state.holding_ball:
        ball = game_state.holding_ball
        # Menghitung kecepatan lempar berdasarkan pergerakan terakhir
        if ball.prev_x is not None:
            ball.vx = (ball.x - ball.prev_x) * 3  # Kecepatan horizontal
            ball.vy = (ball.y - ball.prev_y) * 3 - 0.03  # Kecepatan vertikal + gravity offset
        
        ball.thrown = True      # Status bola sedang dilempar
        ball.grabbed = False    # Bola tidak dipegang lagi
        game_state.holding_ball = None  # Tangan kosong
    
    # 4. Update Posisi Bola yang Dipegang - ikuti posisi jari tengah
    if game_state.holding_ball and game_state.middle_finger_tip:
        ball = game_state.holding_ball
        ball.prev_x = ball.x  # Simpan posisi sebelumnya untuk perhitungan kecepatan
        ball.prev_y = ball.y
        ball.x = game_state.middle_finger_tip['x']  # Update posisi x
        ball.y = game_state.middle_finger_tip['y']  # Update posisi y
    
    # 5. Physics Update untuk semua bola
    balls_to_keep = []  # Daftar bola yang masih aktif
    for ball in game_state.balls:
        # A. Bola menggelinding di tanah
        if ball.on_ground and not ball.thrown and not ball.grabbed:
            ball.vx += ball.roll_direction * 0.0005  # Akselerasi gelinding
            ball.vx *= 0.98  # Friction - mengurangi kecepatan
            ball.x += ball.vx  # Update posisi horizontal
            
            # Pantulan dinding kiri/kanan saat menggelinding
            if ball.x < 0.05 or ball.x > 0.95:
                ball.x = max(0.05, min(0.95, ball.x))  # Clamp posisi
                ball.roll_direction *= -1  # Balik arah gelinding
                ball.vx *= -0.7  # Kurangi kecepatan setelah memantul

        # B. Bola sedang dilempar (di udara)
        if ball.thrown:
            ball.vy += 0.002  # Gravity - percepatan vertikal ke bawah
            ball.x += ball.vx  # Update posisi horizontal
            ball.y += ball.vy  # Update posisi vertikal
            
            # Wall Collision (Kiri/Kanan)
            if ball.x < 0.05 or ball.x > 0.95:
                ball.x = max(0.05, min(0.95, ball.x))  # Clamp posisi
                ball.vx *= -0.6  # Balik arah dan kurangi kecepatan horizontal
            
            # Ceiling Collision - tabrakan dengan langit-langit
            if ball.y < 0.05:
                ball.y = 0.05
                ball.vy *= -0.5  # Balik arah vertikal
            
            # Floor Collision - tabrakan dengan tanah
            if ball.y > game_state.ground:
                ball.y = game_state.ground
                ball.vy *= -0.6  # Pantulan vertikal
                ball.vx *= 0.8   # Reduksi kecepatan horizontal
                
                # Jika pantulan sangat kecil, anggap bola berhenti
                if abs(ball.vy) < 0.01:
                    ball.thrown = False
                    ball.on_ground = True
                    ball.vy = 0
            
            # C. Scoring System - cek apakah bola masuk ring
            dist_to_hoop = calculate_distance({'x': ball.x, 'y': ball.y}, game_state.hoop)
            inside_ring = dist_to_hoop < game_state.hoop['radius']  # Bola dalam radius ring
            was_inside_ring = ball.entered_from_top  # Apakah sebelumnya sudah dalam ring
            
            if inside_ring and ball.thrown:
                if not was_inside_ring:
                    # Cegah score spam dengan cooldown 0.3 detik
                    if now - game_state.last_score_time > 0.3:
                        _handle_score(game_state, ball, now, sound_manager) 
                ball.entered_from_top = True  # Tandai bola sudah masuk ring
            else:
                ball.entered_from_top = False  # Reset status masuk ring
        
        # Tambahkan bola ke daftar yang akan dipertahankan
        balls_to_keep.append(ball)
    
    # Update daftar bola (untuk menghapus bola yang sudah tidak aktif)
    game_state.balls = balls_to_keep
    
    # 6. Timer Update - update waktu permainan
    if game_state.game_start_time:
        elapsed = time.time() - game_state.game_start_time  # Waktu yang sudah berlalu
        game_state.time_left = max(0, 60 - int(elapsed))    # Sisa waktu (60 detik total)
        
        # Cek apakah waktu sudah habis
        if game_state.time_left <= 0:
            end_game(game_state, sound_manager)

def _handle_score(game_state, ball, now, sound_manager=None):
    """Helper function internal untuk memproses penambahan poin."""
    # Default 2 poin, bisa menjadi 3 poin tergantung zona lemparan
    points = 2
    throw_x = 0
    
    # Tentukan jumlah poin berdasarkan posisi awal lemparan
    if ball.throw_start_pos:
        throw_x = ball.throw_start_pos['x']
        # Jika lempar dari zona kanan (x > zone_divider), dapat 3 poin
        if throw_x >= game_state.zone_divider:
            points = 3
    
    # Tambahkan poin ke skor
    game_state.score += points
    game_state.last_score_time = now  # Catat waktu score terakhir
    
    # Trigger efek visual score
    game_state.score_effect_active = True
    game_state.score_effect_start_time = now
    game_state.score_effect_points = points
    game_state.score_effect_position = {'x': ball.x, 'y': ball.y}
    
    # Mainkan suara score
    if sound_manager:
        sound_manager.play('score')
    
    print(f"🏀 SCORE! +{points} poin! Total: {game_state.score}")