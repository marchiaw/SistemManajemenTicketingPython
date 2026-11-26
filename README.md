# Ticketing FMIPA

Aplikasi desktop Python untuk panitia yang mengelola acara kampus, kuota, dan tiket peserta. Acara bawaan **Seminar Web3 & Blockchain**, **Aula FMIPA**, dan **kuota 2** berasal dari proyek Java lama. Acara tambahan dan identitas peserta dalam data contoh bersifat fiktif.

## Menjalankan aplikasi dan pengujian

Ekstrak ZIP. Buka terminal di folder `ticketing_uas`. Gunakan Python 3.10 atau lebih baru dengan Tkinter. Tidak ada paket Python eksternal.

```bash
python --version
python -m tkinter
python main.py
python -m unittest -v
```

Tutup jendela kecil dari `python -m tkinter` sebelum menjalankan baris berikutnya. Di Windows, `py` dapat menggantikan `python`. Di macOS/Linux, coba `python3` jika perintah `python` tidak tersedia. Pada Ubuntu/Debian, instal paket sistem `python3-tk` jika Tkinter belum tersedia. Jalankan GUI dari sesi desktop.

## Operasi tabel

- **Tambah Acara** memberikan ID otomatis saat acara disimpan. Kategori dipilih dari daftar pada formulir tambah dan ubah. **Ubah** mempertahankan ID. **Hapus** meminta konfirmasi karena tiket terkait ikut dihapus.
- **Cari** menerima ID lengkap seperti `EVT-0001`, potongan nama seperti `python`, atau potongan kategori seperti `karya`. **Tampilkan semua** membersihkan filter.
- **Urutkan** mengurutkan hasil yang tampil. Pilih salah satu dari tujuh kolom, lalu arah **Naik** atau **Turun**.
- **Peserta** membuka tabel NPM, nama, dan program studi. Gunakan **Daftarkan Peserta** atau **Batalkan Tiket** untuk mengubah keterisian kuota.
- **Simpan** menulis ulang snapshot aktif, dan **Muat Ulang** membacanya. Perubahan acara dan tiket juga tersimpan otomatis. Saat pertama kali file aktif belum ada, data contoh disalin melalui layanan.
- File aktif berada di `data/acara.txt`. Jika file kosong atau rusak, pulihkan dari cadangan lalu pilih **Muat Ulang**. Untuk kembali ke contoh, tutup aplikasi, pindahkan file rusak ke nama lain sebagai cadangan, lalu buka kembali. Jalankan satu instance GUI untuk satu file data.

## Struktur proyek

```text
ticketing_uas/
├── main.py
├── test_app.py
├── README.md
├── .gitignore
├── data/
│   ├── contoh_acara.txt
│   └── acara.txt             # dibuat saat aplikasi pertama dijalankan
└── ticketing/
    ├── __init__.py
    ├── ui.py
    ├── services.py
    ├── storage.py
    ├── validasi.py
    ├── model.py
    └── algoritma.py
```

## Modul Python yang digunakan

| Modul | Penggunaan |
| --- | --- |
| `tkinter`, `tkinter.ttk`, `tkinter.messagebox`, `tkinter.font` | Jendela, kontrol, Treeview, dialog konfirmasi dan pesan, serta ukuran judul. |
| `pathlib` | Menentukan lokasi proyek serta file data lintas sistem operasi. |
| `csv` | Membaca dan menulis kolom TXT yang dipisahkan tanda pipa. |
| `os` | Mengganti file aktif setelah file sementara selesai ditulis. |
| `unittest`, `unittest.mock`, `tempfile` | Pengujian, simulasi kegagalan, dan direktori sementara untuk aplikasi serta tes. |

## Optimasi pencarian

Pencarian nama dan kategori menggunakan Linear Search dengan pencocokan substring. Pencarian ID lengkap menggunakan dictionary sebagai penyimpanan utama dan indeks sekaligus. Lookup rata-rata O(1) terhadap jumlah acara, dengan kemungkinan O(n) pada kasus terburuk hash map. Memuat ulang indeks membutuhkan O(n) untuk n acara, di luar validasi dan pembacaan peserta. Untuk uji yang membandingkan hasil indeks dengan 1.000 pemeriksaan baseline, jalankan:

```bash
python -m unittest -v test_app.TestTicketing.test_optimasi_pencarian_id
```

Insertion Sort mengambil satu baris lalu menggeser baris di sebelah kirinya sampai menemukan posisi yang tepat. Algoritma ini stabil karena baris yang nilainya sama tidak digeser. Waktu terburuk O(n²), sehingga dipakai untuk tabel acara berukuran kecil. Kuota, peserta, dan sisa dibandingkan sebagai bilangan.

## Urutan membaca kode untuk presentasi

1. Mulai dari `main.py`. Fungsi `main()` membuat jendela, penyimpanan, dan layanan.
2. Ikuti satu tombol di `ui.py`. Saat **Tambah Acara** ditekan, GUI mengambil isian lalu memanggil `layanan.tambah(...)`.
3. Buka `services.py` dan `model.py`. Data diperiksa saat objek `Acara` dibuat. Layanan menyimpan acara melalui `storage.py`, lalu UI menyegarkan tabel.
4. Baca `algoritma.py`. Coba jelaskan urutan kuota `30, 2, 24`: angka 2 disisipkan ke depan 30, lalu 24 disisipkan di antara keduanya. Jelaskan juga bahwa indeks memungkinkan pencarian ID langsung melalui `dictionary.get()`.

## Mengumpulkan bukti

Rekam demo 5–10 menit dan ambil screenshot dashboard, pencarian/pengurutan, serta hasil `python -m unittest -v`. Isi identitas pada sampul laporan, tambahkan tautan repo **Public** dan video YouTube **Public/Unlisted**, lalu gunakan format pengumpulan `UAS_NPM_Nama Lengkap_Kelas.pdf`. Unggah data fiktif saja. File aktif yang mungkin berisi data peserta dikecualikan dari Git.
