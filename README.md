# 📄 RafPDF Studio

**RafPDF Studio** adalah alat manipulasi PDF berbasis web yang berjalan **100% secara lokal di komputer Anda**. Tidak ada file yang diunggah ke cloud. Privasi dan keamanan dokumen Anda adalah prioritas utama.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)

## ✨ Fitur Utama

- **Kompres PDF**: Perkecil ukuran file (hingga >90%) tanpa menghilangkan teks.
- **Gabungkan PDF (Merge)**: Satukan beberapa file PDF dengan fitur *preview grid* dan rotasi per halaman.
- **Pisahkan PDF (Split)**: Ambil halaman tertentu dari dokumen besar menjadi PDF baru.
- **JPG ke PDF**: Ubah foto/gambar menjadi PDF. Bisa diputar sebelum dikonversi.
- **Putar PDF**: Perbaiki orientasi halaman yang miring.
- **Watermark**: Tambahkan teks transparan (misal: "RAHASIA") secara diagonal.
- **Hapus Halaman**: Klik halaman yang tidak diinginkan, lalu simpan.
- **Tambah Nomor Halaman**: Beri penomoran otomatis (bawah tengah/kanan).
- **Kunci PDF (Protect)**: Amankan dokumen dengan kata sandi.
- **Buka Kunci PDF (Unlock)**: Hapus kata sandi dari PDF yang terkunci.
- **Antarmuka Premium**: Desain *dark mode* dengan efek kaca (*glassmorphism*), animasi halus, dan pencarian alat.

## 🛠️ Prasyarat

Proyek ini membutuhkan **Ghostscript** untuk fitur kompresi PDF yang maksimal.

- **Linux (Fedora/RHEL):** `sudo dnf install ghostscript`
- **Linux (Ubuntu/Debian):** `sudo apt install ghostscript`
- **Windows:** Unduh dan instal [Ghostscript untuk Windows](https://www.ghostscript.com/releases/gsdnld.html), lalu pastikan folder `bin`-nya masuk ke *Environment Variables*.
- **macOS:** `brew install ghostscript`

## 🚀 Cara Instalasi & Menjalankan

1. **Clone repositori ini:**
   `git clone https://github.com/RaviAdinata/rafPDF.git`
   `cd rafPDF`

2. **Buat Virtual Environment (Disarankan):**
   `python -m venv venv`
   - Linux/Mac: `source venv/bin/activate`
   - Windows: `venv\Scripts\activate`

3. **Install Dependensi:**
   `pip install -r requirements.txt`

4. **Jalankan Server:**
   `python main.py`

5. **Buka Browser:**
   Akses `http://127.0.0.1:8000`

## 🧰 Teknologi yang Digunakan

- **Backend**: FastAPI, Uvicorn
- **Pemrosesan PDF**: pikepdf, PyMuPDF (fitz), Ghostscript
- **Pemrosesan Gambar**: Pillow (PIL)
- **Frontend**: HTML5, CSS3 (Vanilla), JavaScript (Vanilla)
- **Keamanan**: Auto-cleanup file setiap 30 menit.

## 📸 Tangkapan Layar
<img width="1920" height="932" alt="image" src="https://github.com/user-attachments/assets/ef7ad2d2-1cf7-4a92-ac69-61ac973a23ee" />


## 🤝 Kontribusi

Kontribusi selalu diterima! Silakan buat *Pull Request* atau buka *Issue* jika ada bug atau saran fitur.

## 📜 Lisensi

Proyek ini dilisensikan di bawah MIT License.
