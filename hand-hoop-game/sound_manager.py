import pygame
import os

class SoundManager:
    """ Menangani inisialisasi mixer dan pemutaran efek suara (SFX). """
    def __init__(self):
        # Inisialisasi mixer pygame (frekuensi, size, channel, buffer)
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        
        # Dictionary untuk menyimpan objek suara
        self.sounds = {}
        
        self.sound_enabled = True

    def load_sound(self, name, file_path):
        try:
            if os.path.exists(file_path):
                self.sounds[name] = pygame.mixer.Sound(file_path)
                print(f"🔊 Suara dimuat: {name}")
            else:
                print(f"⚠️ File suara tidak ditemukan: {file_path}")
        except Exception as e:
            print(f"❌ Gagal memuat suara {name}: {e}")

    def play(self, name):
        """Memutar suara berdasarkan nama."""
        if self.sound_enabled and name in self.sounds:
            self.sounds[name].play()

    def cleanup(self):
        """Membersihkan resource mixer saat keluar game."""
        pygame.mixer.quit()