import math

def calculate_distance(p1, p2):
    """
    Menghitung jarak Euclidean antara dua titik.

    """
    return math.sqrt((p1['x'] - p2['x'])**2 + (p1['y'] - p2['y'])**2)

def is_hand_closed(hand_landmarks):
    """
    Mendeteksi apakah tangan sedang mengepal (closed fist) berdasarkan kelengkungan jari.
    
    """
    # Ambil posisi pergelangan tangan (wrist)
    wrist = hand_landmarks.landmark[0]
    
    # Indeks landmark untuk ujung jari dan ruas jari (knuckles)
    finger_tips = [4, 8, 12, 16, 20]      # Jempol, Telunjuk, Tengah, Manis, Kelingking
    finger_knuckles = [3, 6, 10, 14, 18]
    
    closed_fingers = 0
    
    for tip_idx, knuckle_idx in zip(finger_tips, finger_knuckles):
        tip = hand_landmarks.landmark[tip_idx]
        knuckle = hand_landmarks.landmark[knuckle_idx]
        
        # Hitung jarak dari ujung ke wrist vs ruas ke wrist
        tip_dist = math.sqrt((tip.x - wrist.x)**2 + (tip.y - wrist.y)**2)
        knuckle_dist = math.sqrt((knuckle.x - wrist.x)**2 + (knuckle.y - wrist.y)**2)
        
        # Jika ujung jari lebih dekat ke wrist daripada ruasnya, berarti jari melengkung
        if tip_dist < knuckle_dist * 1.1:  # 1.1 adalah toleransi
            closed_fingers += 1
    
    # Tangan dianggap mengepal jika 4 atau lebih jari tertutup
    return closed_fingers >= 4