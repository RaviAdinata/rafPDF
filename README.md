# 📄 RafPDF Studio

**RafPDF Studio** adalah alat manipulasi PDF berbasis web yang berjalan **100% secara lokal di komputer Anda**. Tidak ada file yang diunggah ke cloud. Privasi dan keamanan dokumen Anda adalah prioritas utama.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)

## ✨ Fitur Utama

- **Kompres PDF**: Perkecil ukuran file (hingga >90%) tanpa menghilangkan teks.
- **Gabungkan PDF (Merge)**: Satukan beberapa file PDF dengan fitur *preview grid* dan rotasi per halaman.
- **JPG ke PDF**: Ubah foto/gambar menjadi PDF. Bisa diputar sebelum dikonversi.
- **Putar PDF**: Perbaiki orientasi halaman yang miring.
- **Watermark**: Tambahkan teks transparan (misal: "RAHASIA") secara diagonal.
- **Hapus Halaman**: Klik halaman yang tidak diinginkan, lalu simpan.
- **Antarmuka Modern**: Desain *dark mode* yang bersih dan responsif.

## 🛠️ Prasyarat

Proyek ini membutuhkan **Ghostscript** untuk fitur kompresi PDF yang maksimal.

**Linux (Fedora/RHEL):**
`sudo dnf install ghostscript`

**Linux (Ubuntu/Debian):**
`sudo apt install ghostscript`

## 🚀 Cara Instalasi & Menjalankan

1. **Clone repositori ini:**
   `git clone https://github.com/username-anda/RafPDF.git`
   `cd RafPDF`

2. **Install Dependensi:**
   `pip install -r requirements.txt`

3. **Jalankan Server:**
   `python main.py`

4. **Buka Browser:**
   Akses `http://127.0.0.1:8000`

## 🧰 Teknologi yang Digunakan

- **Backend**: FastAPI, Uvicorn
- **Pemrosesan PDF**: pikepdf, PyMuPDF (fitz), Ghostscript
- **Pemrosesan Gambar**: Pillow (PIL)
- **Frontend**: HTML5, CSS3 (Vanilla), JavaScript (Vanilla)

## 🤝 Kontribusi

Kontribusi selalu diterima! Silakan buat *Pull Request* atau buka *Issue* jika ada bug atau saran fitur.

## 📜 Lisensi

Proyek ini dilisensikan di bawah MIT License.
