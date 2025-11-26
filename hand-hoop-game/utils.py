import math

def calculate_distance(p1, p2):
    """
    Menghitung jarak Euclidean antara dua titik.
    
    """
    return math.sqrt((p1['x'] - p2['x'])**2 + (p1['y'] - p2['y'])**2)