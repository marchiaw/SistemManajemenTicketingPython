"""Menyimpan acara dan peserta dalam satu file teks UTF-8."""

import csv  # Membaca kolom berpemisah | dan menangani tanda | dalam nama.
import os  # Mengganti file aktif setelah seluruh data selesai ditulis.
from pathlib import Path  # Menentukan lokasi file.
from tempfile import TemporaryDirectory  # Menampung hasil tulis sementara.
from .model import Acara  # Memvalidasi data sebelum ditampilkan.
from .validasi import id_acara  # Menyeragamkan ID pada setiap baris.


class PenyimpananTXT:
    """Membaca dan menulis baris ACARA dan PESERTA dalam satu file TXT."""

    def __init__(self, path):
        """Simpan lokasi file dari path. Kembali None."""
        self.path = Path(path)
        self.nomor_terakhir = 0

    def muat(self):
        """Baca seluruh baris dan kembalikan daftar objek Acara."""
        data = {}
        terakhir = 0
        with open(self.path, "r", encoding="utf-8", newline="") as file:
            pembaca = csv.reader(file, delimiter="|", strict=True)
            try:
                header = next(pembaca, [])
                if len(header) not in (2, 3) or header[:2] != ["TICKETING", "1"]:
                    raise ValueError("Judul file harus TICKETING|1.")
                if len(header) == 3:
                    terakhir = int(header[2])
                    if not 0 <= terakhir <= 9999:
                        raise ValueError("Nomor acara terakhir tidak valid.")
                for baris in pembaca:
                    if len(baris) == 6 and baris[0] == "ACARA":
                        jenis, kode, nama, kategori, ruangan, kuota = baris
                        kode = id_acara(kode)
                        if kode in data:
                            raise ValueError("ID acara duplikat.")
                        data[kode] = dict(id=kode, nama=nama, kategori=kategori,
                                          ruangan=ruangan, kuota=kuota, peserta=[])
                    elif len(baris) == 5 and baris[0] == "PESERTA":
                        jenis, kode, npm, nama, prodi = baris
                        kode = id_acara(kode)
                        if kode not in data:
                            raise ValueError("Acara peserta belum tercatat.")
                        data[kode]["peserta"].append(dict(npm=npm, nama=nama, prodi=prodi))
                    else:
                        raise ValueError("Jenis baris atau jumlah kolom salah.")
            except (csv.Error, ValueError) as error:
                raise ValueError(f"TXT baris {pembaca.line_num}: {error}") from error

        hasil = [Acara(**acara) for acara in data.values()]
        for acara in hasil:
            terakhir = max(terakhir, int(acara.id[4:]))
        self.nomor_terakhir = terakhir
        return hasil

    def simpan(self, daftar_acara):
        """Tulis daftar acara beserta pesertanya ke file TXT. Kembali None."""
        daftar_acara = list(daftar_acara)
        terakhir = self.nomor_terakhir
        for acara in daftar_acara:
            terakhir = max(terakhir, int(acara.id[4:]))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with TemporaryDirectory(dir=self.path.parent) as folder:
            sementara = Path(folder) / "acara.txt"
            with open(sementara, "w", encoding="utf-8", newline="") as file:
                penulis = csv.writer(file, delimiter="|", lineterminator="\n")
                penulis.writerow(["TICKETING", "1", terakhir])
                for acara in daftar_acara:
                    penulis.writerow(["ACARA", acara.id, acara.nama, acara.kategori,
                                      acara.ruangan, acara.kuota])
                    for peserta in acara.peserta:
                        penulis.writerow(["PESERTA", acara.id, peserta["npm"],
                                          peserta["nama"], peserta["prodi"]])
            os.replace(sementara, self.path)
        self.nomor_terakhir = terakhir
