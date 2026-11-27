# Ticketing FMIPA

Ticketing FMIPA adalah aplikasi desktop untuk membantu panitia organisasi di lingkungan FMIPA Universitas Lampung mengelola acara dan pendaftaran peserta. Aplikasi ini dibuat dengan Python dan Tkinter. Data acara dan peserta disimpan di `data/acara.txt` sehingga bisa dibuka kembali saat aplikasi dijalankan.

## Fitur

- Menambah, mengubah, dan menghapus acara. ID acara dibuat otomatis saat data disimpan, dan kategori dipilih dari daftar.
- Mencari acara berdasarkan ID, nama, atau kategori. Daftar acara juga bisa diurutkan, misalnya berdasarkan sisa kuota.
- Melihat daftar peserta, mendaftarkan peserta baru, dan membatalkan pendaftaran melalui tombol **Peserta**.
- Memantau jumlah pendaftar dan sisa kuota. Sistem menolak pendaftaran jika kuota habis atau NPM yang sama sudah terdaftar pada acara tersebut.

## Cara menjalankan

Pastikan Python 3.10 atau lebih baru dan Tkinter sudah tersedia. Buka terminal di folder `ManajemenTicketing` yang berisi `main.py`, lalu jalankan:

```bat
py main.py
