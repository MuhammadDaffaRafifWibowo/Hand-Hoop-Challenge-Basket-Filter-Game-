import cv2
import numpy as np
import math
import time
from utils import calculate_distance

def draw_text_with_background(img, text, position, font_scale=1, thickness=2, 
                             text_color=(255, 255, 255), bg_color=(0, 0, 0, 180)):
    """Menggambar teks dengan latar belakang persegi panjang agar mudah dibaca."""
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    # Mendapatkan ukuran teks untuk menentukan besar background
    text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
    
    x, y = position
    padding = 10  # Jarak antara teks dan border background
    
    # Membuat overlay untuk background transparan
    overlay = img.copy()
    
    # Menggambar rectangle sebagai background teks
    cv2.rectangle(overlay, 
                  (x - padding, y - text_size[1] - padding),
                  (x + text_size[0] + padding, y + padding),
                  bg_color[:3], -1)  # -1 berarti fill rectangle
    
    # Mengatur transparansi background
    alpha = bg_color[3] / 255.0 if len(bg_color) > 3 else 0.7
    cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)
    
    # Menambahkan teks di atas background
    cv2.putText(img, text, (x, y), font, font_scale, text_color, thickness)

def draw_start_screen(img, width, height):
    """Menggambar layar awal instruksi."""
    # Membuat overlay hitam untuk background menu
    overlay = img.copy()
    cv2.rectangle(overlay, (0, 0), (width, height), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.8, img, 0.2, 0, img)
    
    # Menambahkan judul game
    title = "Hand Hoop Challenge"
    title_size = cv2.getTextSize(title, cv2.FONT_HERSHEY_DUPLEX, 2, 3)[0]
    cv2.putText(img, title, (width//2 - title_size[0]//2, 100), 
                cv2.FONT_HERSHEY_DUPLEX, 2, (255, 255, 255), 3)
    
    # Daftar instruksi permainan
    instructions = [
        "Cara Bermain:", "",
        "GENGGAM tangan (buat kepalan) untuk ambil bola",
        "Bola akan spawn di bawah dan bergelinding",
        "Masukkan bola ke ring orange untuk dapat poin!", "",
        "ZONA KIRI (hijau) = 2 poin", "ZONA KANAN (merah) = 3 poin", "",
        "Target: 15 poin dalam 60 detik!", "",
        "Tekan SPASI untuk mulai", "Tekan ESC atau Q untuk keluar"
    ]
    
    # Menampilkan setiap baris instruksi
    y = 200
    for line in instructions:
        if line:
            text_size = cv2.getTextSize(line, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
            cv2.putText(img, line, (width//2 - text_size[0]//2, y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        y += 40  # Jarak antar baris

def draw_game_over_screen(img, width, height, game_state):
    """Menggambar layar akhir permainan (Menang/Kalah)."""
    # Background overlay gelap
    overlay = img.copy()
    cv2.rectangle(overlay, (0, 0), (width, height), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.8, img, 0.2, 0, img)
    
    # Menentukan tampilan berdasarkan menang/kalah
    if game_state.win:
        title = "SELAMAT!"
        color = (0, 255, 0)  # Hijau untuk menang
        result = f"Anda berhasil mencapai target {game_state.target} poin!"
    else:
        title = "GAGAL"
        color = (0, 0, 255)  # Merah untuk kalah
        result = f"Target: {game_state.target} poin. Coba lagi!"
    
    # Menampilkan judul hasil game
    title_size = cv2.getTextSize(title, cv2.FONT_HERSHEY_DUPLEX, 2.5, 4)[0]
    cv2.putText(img, title, (width//2 - title_size[0]//2, height//2 - 100), 
                cv2.FONT_HERSHEY_DUPLEX, 2.5, color, 4)
    
    # Menampilkan pesan hasil
    result_size = cv2.getTextSize(result, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
    cv2.putText(img, result, (width//2 - result_size[0]//2, height//2), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    # Menampilkan skor akhir
    score_text = f"Skor Akhir: {game_state.score}"
    score_size = cv2.getTextSize(score_text, cv2.FONT_HERSHEY_SIMPLEX, 1.5, 3)[0]
    cv2.putText(img, score_text, (width//2 - score_size[0]//2, height//2 + 80), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
    
    # Instruksi restart
    restart = "Tekan SPASI untuk main lagi"
    restart_size = cv2.getTextSize(restart, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
    cv2.putText(img, restart, (width//2 - restart_size[0]//2, height//2 + 150), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

def draw_hoop(img, hoop, width, height, debug_mode=False):
    """Menggambar ring basket (tiang, papan, jaring, dan ring)."""
    # Konversi koordinat relatif ke piksel
    hoop_x = int(hoop['x'] * width)
    hoop_y = int(hoop['y'] * height)
    hoop_radius = int(hoop['radius'] * width)
    
    # 1. Tiang & Penyangga
    pole_x = 15
    cv2.rectangle(img, (pole_x - 4, 0), (pole_x + 4, int(height * 0.9)), (50, 50, 50), -1)
    cv2.line(img, (pole_x, hoop_y - hoop_radius//2), (hoop_x - hoop_radius, hoop_y - hoop_radius//2), (70, 70, 70), 6)
    
    # 2. Backboard (Papan)
    backboard_w = hoop_radius // 3
    backboard_h = int(hoop_radius * 2.5)
    bb_top_left = (hoop_x - hoop_radius - backboard_w, hoop_y - backboard_h//2)
    bb_btm_right = (hoop_x - hoop_radius, hoop_y + backboard_h//2)
    cv2.rectangle(img, bb_top_left, bb_btm_right, (200, 200, 200), -1)
    cv2.rectangle(img, bb_top_left, bb_btm_right, (100, 100, 100), 2)
    
    # Kotak target kecil di papan
    target_s = hoop_radius // 2
    cv2.rectangle(img, 
                  (hoop_x - hoop_radius - backboard_w//2 - target_s//2, hoop_y - target_s//2),
                  (hoop_x - hoop_radius - backboard_w//2 + target_s//2, hoop_y + target_s//2),
                  (255, 100, 100), 2)
    
    # 3. Ring (Oranye)
    cv2.circle(img, (hoop_x, hoop_y), hoop_radius, (0, 102, 255), 6)
    
    # 4. Jaring (Net) - menggambar garis dari ring ke bawah
    net_segments = 12  # Jumlah segmen jaring
    net_depth = int(hoop_radius * 1.8)  # Panjang jaring
    for i in range(net_segments):
        angle = (i / net_segments) * math.pi * 2  # Sudut untuk setiap segmen
        sx = int(hoop_x + math.cos(angle) * hoop_radius)  # Start point di ring
        sy = int(hoop_y + math.sin(angle) * hoop_radius)
        ex = int(hoop_x + math.cos(angle) * hoop_radius * 0.4)  # End point di tengah
        ey = int(hoop_y + net_depth)
        cv2.line(img, (sx, sy), (ex, ey), (255, 255, 255), 1)
        
    # Mode debug: menampilkan radius detection ring
    if debug_mode:
        cv2.circle(img, (hoop_x, hoop_y), hoop_radius, (0, 255, 0), 2)

def draw_ball(img, ball, width, height, game_state):
    """Menggambar bola basket dengan bayangan dan efek outline."""
    # Konversi koordinat relatif ke piksel
    x = int(ball.x * width)
    y = int(ball.y * height)
    radius = int(ball.radius * width)
    
    # Bayangan di bawah bola
    cv2.circle(img, (x + 5, y + 5), radius, (0, 0, 0), -1)
    
    # Warna bola berubah jika berada dalam ring
    dist = calculate_distance({'x': ball.x, 'y': ball.y}, game_state.hoop)
    inside_ring = dist < game_state.hoop['radius']
    ball_color = (0, 255, 0) if (inside_ring and ball.thrown) else (0, 140, 255)  # Hijau jika dalam ring, oranye default
    
    # Menggambar bola utama
    cv2.circle(img, (x, y), radius, ball_color, -1)
    cv2.circle(img, (x, y), radius, (0, 0, 0), 2)  # Outline hitam
    
    # Garis karakteristik bola basket
    cv2.line(img, (x - radius, y), (x + radius, y), (0, 0, 0), 2)
    cv2.line(img, (x, y - radius), (x, y + radius), (0, 0, 0), 2)
    
    # Highlight kuning jika bola bisa diambil (tangan mengepal dekat bola)
    if not ball.thrown and not ball.grabbed and game_state.is_closed_hand:
        cv2.circle(img, (x, y), radius + 5, (0, 255, 255), 3)

def draw_ui(img, game_state, width, height):
    """Menggambar elemen UI (Skor, Waktu, Indikator)."""
    # Menampilkan skor, target, dan timer dengan background
    draw_text_with_background(img, f"Skor: {game_state.score}", (20, 40), 1, 2)
    
    target_txt = f"Target: {game_state.target}"
    t_size = cv2.getTextSize(target_txt, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
    draw_text_with_background(img, target_txt, (width//2 - t_size[0]//2, 40), 1, 2)
    
    timer_txt = f"Waktu: {game_state.time_left}s"
    tm_size = cv2.getTextSize(timer_txt, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
    draw_text_with_background(img, timer_txt, (width - tm_size[0] - 40, 40), 1, 2)
    
    # Indikator status tangan di bagian bawah layar
    if game_state.is_playing:
        if game_state.holding_ball:
            ind = "Lepas genggaman untuk lempar!"
            col = (0, 255, 0)  # Hijau
        elif game_state.is_closed_hand:
            ind = "Menggenggam!"
            col = (0, 255, 0)  # Hijau
        else:
            ind = "Genggam tangan untuk ambil bola!"
            col = (255, 255, 255)  # Putih
            
        i_size = cv2.getTextSize(ind, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
        draw_text_with_background(img, ind, (width//2 - i_size[0]//2, height - 80), 0.8, 2, col)

def draw_scoring_zones(img, game_state, width, height):
    """Menggambar garis pembatas zona 2 poin dan 3 poin."""
    # Garis pemisah zona
    div_x = int(game_state.zone_divider * width)
    cv2.line(img, (div_x, 0), (div_x, height), (255, 255, 0), 8)  # Garis kuning
    
    # Zona Kiri (2PT - Hijau transparan)
    overlay = img.copy()
    cv2.rectangle(overlay, (0, 0), (div_x, height), (0, 255, 0), -1)
    cv2.addWeighted(overlay, 0.15, img, 0.85, 0, img)  # Transparansi 15%
    cv2.putText(img, "2 PT", (30, 80), cv2.FONT_HERSHEY_DUPLEX, 1.2, (255, 255, 255), 3)
    
    # Zona Kanan (3PT - Merah transparan)
    overlay = img.copy()
    cv2.rectangle(overlay, (div_x, 0), (width, height), (0, 0, 255), -1)
    cv2.addWeighted(overlay, 0.15, img, 0.85, 0, img)  # Transparansi 15%
    cv2.putText(img, "3 PT", (width - 130, 80), cv2.FONT_HERSHEY_DUPLEX, 1.2, (255, 255, 255), 3)

def draw_score_effect(img, game_state, width, height):
    """Menggambar efek animasi saat mencetak skor."""
    if not game_state.score_effect_active:
        return
        
    # Cek durasi efek (0.8 detik)
    elapsed = time.time() - game_state.score_effect_start_time
    if elapsed > 0.8:
        game_state.score_effect_active = False
        game_state.freeze_frame = None
        return
        
    # Freeze frame background - membekukan latar saat efek score
    if game_state.freeze_frame is not None:
        overlay = game_state.freeze_frame.copy()
        dark = cv2.addWeighted(overlay, 0.6, np.zeros_like(overlay), 0.4, 0)  # Menggelapkan background
        img[:] = dark  # Menyalin background yang sudah digelapkan
        
    # Animasi lingkaran dan teks yang membesar
    cx, cy = width // 2, height // 2
    scale = 1.0 + (elapsed / 0.3) * 0.5 if elapsed < 0.3 else 1.5  # Scaling animasi
    
    # Tentukan teks dan warna berdasarkan poin
    text = "+3 POINTS!" if game_state.score_effect_points == 3 else "+2 POINTS!"
    color = (0, 0, 255) if game_state.score_effect_points == 3 else (0, 255, 0)  # Merah untuk 3pt, hijau untuk 2pt
    
    # Lingkaran efek score
    cv2.circle(img, (cx, cy), int(80 * scale), color, -1)
    cv2.circle(img, (cx, cy), int(80 * scale), (255, 255, 255), 5)  # Outline putih
    
    # Teks efek score
    ts = cv2.getTextSize(text, cv2.FONT_HERSHEY_DUPLEX, 2 * scale, 4)[0]
    cv2.putText(img, text, (cx - ts[0]//2, cy + 10), cv2.FONT_HERSHEY_DUPLEX, 2 * scale, (255, 255, 255), 4)

def draw_hand_landmarks(img, landmarks, width, height, is_closed):
    """Menggambar skeleton tangan."""
    # Koneksi antara landmark tangan
    connections = [
        [0,1],[1,2],[2,3],[3,4], [0,5],[5,6],[6,7],[7,8],
        [0,9],[9,10],[10,11],[11,12], [0,13],[13,14],[14,15],[15,16],
        [0,17],[17,18],[18,19],[19,20], [5,9],[9,13],[13,17]
    ]
    
    # Warna hijau jika tangan mengepal, putih jika terbuka
    color = (0, 255, 0) if is_closed else (255, 255, 255)
    
    # Gambar garis penghubung antar landmark
    for conn in connections:
        start = landmarks.landmark[conn[0]]
        end = landmarks.landmark[conn[1]]
        start_pt = (int(start.x * width), int(start.y * height))
        end_pt = (int(end.x * width), int(end.y * height))
        cv2.line(img, start_pt, end_pt, color, 2)
        
    # Gambar titik-titik landmark
    for lm in landmarks.landmark:
        pt = (int(lm.x * width), int(lm.y * height))
        cv2.circle(img, pt, 4, color, -1)