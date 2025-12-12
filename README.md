# Hand-Hoop-Challenge-Basket-Filter-Game-
Multimedia Tugasbesar

**Link Video Demonstrasi Filter:** https://youtu.be/P9VcYket7Vw?si=7kMKWbSGfSa_ytpZ

# 👥 Daftar Anggota Kelompok

| No | Nama                         | NIM        | ID Github                |
|----|------------------------------|------------|--------------------------|
| 1  | M. Raihan Athalah Ilham      | 122140022  | Hannntastix              | 
| 2  | Adin Adry Tjindarbumi        | 122140024  | AdinAdryTjindarbumi      |
| 3  | Muhammad Daffa Rafif Wibowo  | 122140036  | MuhammadDaffaRafifWibowo |

# 📝 Logbook Progres Mingguan Proyek Hand-Tracking Basketball Game

Hand Hoop Challenge adalah arcade game eksperimental yang mengubah webcam laptop Anda menjadi pengontrol permainan. Dibangun menggunakan Python, proyek ini mendemonstrasikan bagaimana Human-Computer Interaction (HCI) dapat diciptakan menggunakan teknologi Computer Vision sederhana namun efektif.

Pemain ditantang untuk mencetak skor sebanyak mungkin dalam 60 detik dengan cara "memegang" bola virtual di layar dan melemparkannya ke ring menggunakan gerakan tangan asli. Tidak ada keyboard, tidak ada mouse hanya gerakan tangan Anda.

Teknologi di Balik Layar:

- Bahasa: Python 3.9+ maksimal Python 3.11

- Computer Vision: OpenCV & MediaPipe Hands

- Audio: Pygame Mixer

- Konsep Teknis: Vector Math untuk fisika bola, Collision Detection, dan State Management.

- Arsitektur: Modular Design (Separated Logic, Visuals, and Objects).

---

## 📅 Logbook Mingguan

| Minggu | Tanggal    | Deskripsi Pengerjaan                                               |
|--------|------------|--------------------------------------------------------------------|
| 1      | 06/11/2025 | Mendiskusikan mekanisme dan alur pengerjaan project ini            |
| 2      | 11/11/2025 | Menentukan mekanisme permainan dalam filternya                     |
| 3      | 14/11/2025 | Commit code fungsi Menambahkan fungsi ke dalam repositori github   |
| 4      | 26/11/2025 | Commit melengkapi semua code fungsi-fungsi ke repositori github    |
| 5      | 29/11/2025 | Melakukan modifikasi terhadap kode dan merapihkan struktur kodenya |
| 6      | 12/12/2025 | Melakukan finalisasi terhadap kode dan modifikasi kode readme      |


# 🛠️ Persiapan & Instalasi

Pastikan Anda telah menginstal **Maksimal Python versi 3.11** di komputer Anda.

## 1. Clone atau Download Repository
Unduh folder proyek ini ke komputer Anda.

## 2. Buat Virtual Environment (Disarankan)
Agar library tidak bentrok dengan proyek lain, buatlah virtual environment.

### Windows
```bash
python -m venv venv
venv\Scripts\activate

* Mac/Linux
python3 -m venv venv
source venv/bin/activate

3. Instal Dependencies
Jalankan perintah berikut untuk menginstal semua library yang dibutuhkan:

```bash
-pip install -r requirements.txt
-Library yang akan diinstal meliputi:
-opencv-python
-mediapipe
-pygame
-numpy

4. Siapkan Aset Audio (Opsional)

Jika ingin fitur suara berfungsi, tambahkan file audio .wav ke folder berikut:  
assets/
Atau sesuaikan path audio pada file main.py.    

🚀 Cara Menjalankan Program

-Pastikan virtual environment sudah aktif, lalu jalankan:
python main.py

🎮 Cara Bermain (Kontrol)

-Mulai Game: Tekan tombol SPASI
-Ambil Bola: Arahkan tangan ke bola, lalu GENGGAM (kepalkan) tangan
-Lempar Bola: Arahkan membuka tangan ke arah ring

Skor:

-Zona Hijau (Dekat): 2 Poin
-Zona Merah (Jauh): 3 Poin
-Keluar Game: Tekan Q atau ESC
-Debug Mode: Tekan D untuk menampilkan hitbox (area deteksi)

📁 Struktur Folder (Opsional)
project/
│── assets/
│   ├── shoot.wav
│   ├── score.wav
│   └── ...
│── main.py
│── utils.py
│── game_logic.py
│── requirements.txt
│── README.md


💡 Catatan Tambahan

-Pastikan kamera laptop/PC Anda berfungsi.
-Gunakan pencahayaan yang baik agar deteksi tangan lebih akurat.
-Jarak kamera 30–60 cm dari tubuh sangat disarankan.