"""Memeriksa masukan formulir dan isi file TXT."""


def teks(nilai, label):
    """Kembalikan teks yang sudah dirapikan. label dipakai pada pesan kesalahan."""
    if not isinstance(nilai, str):
        raise ValueError(f"{label} harus berupa teks.")

    nilai = nilai.strip()
    if not nilai or len(nilai) > 100 or not nilai.isprintable():
        raise ValueError(f"{label} harus berisi 1–100 karakter yang dapat dicetak.")
    return nilai


def id_acara(nilai):
    """Kembalikan ID dalam format EVT-0001 sampai EVT-9999."""
    kode = teks(nilai, "ID acara").upper()
    angka = kode[4:]
    if not kode.startswith("EVT-") or len(angka) != 4:
        raise ValueError("ID harus berformat EVT-0001 sampai EVT-9999.")
    if not angka.isascii() or not angka.isdigit() or angka == "0000":
        raise ValueError("ID harus berformat EVT-0001 sampai EVT-9999.")
    return kode


def kuota_acara(nilai):
    """Ubah teks angka dari formulir menjadi integer dan periksa batas kuota."""
    if isinstance(nilai, str):
        nilai = nilai.strip()
        if nilai.isascii() and nilai.isdigit() and len(nilai) <= 6:
            nilai = int(nilai)

    if type(nilai) is not int or not 1 <= nilai <= 999999:
        raise ValueError("Kuota harus berupa bilangan bulat 1–999999.")
    return nilai


def npm_peserta(nilai):
    """Kembalikan NPM sebagai teks agar angka nol di depan tetap ada."""
    npm = teks(nilai, "NPM")
    if not npm.isascii() or not npm.isdigit() or len(npm) > 20:
        raise ValueError("NPM harus terdiri dari 1–20 digit.")
    return npm


def buat_peserta(npm, nama, prodi):
    """Periksa tiga masukan peserta dan kembalikan hasilnya sebagai dictionary."""
    return {
        "npm": npm_peserta(npm),
        "nama": teks(nama, "Nama peserta"),
        "prodi": teks(prodi, "Program studi"),
    }
