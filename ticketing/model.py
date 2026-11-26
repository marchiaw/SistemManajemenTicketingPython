"""Menyimpan satu acara beserta data peserta yang sudah diperiksa."""

# Fungsi pada validasi dipakai untuk masukan GUI maupun TXT.
from .validasi import buat_peserta, id_acara, kuota_acara, teks


class Acara:
    """Satu acara berisi ID, nama, kategori, ruangan, kuota, dan list peserta."""

    def __init__(self, id, nama, kategori, ruangan, kuota, peserta=None):
        """Validasi data dan simpan dalam atribut objek. Kembali None."""
        self.id = id_acara(id)
        self.nama = teks(nama, "Nama acara")
        self.kategori = teks(kategori, "Kategori")
        self.ruangan = teks(ruangan, "Ruangan")
        self.kuota = kuota_acara(kuota)
        self.peserta = []
        npm_terdaftar = set()

        for orang in peserta or []:
            orang = buat_peserta(**orang)
            npm = orang["npm"]
            if npm in npm_terdaftar:
                raise ValueError("NPM sudah terdaftar di acara ini.")
            npm_terdaftar.add(npm)
            self.peserta.append(orang)

        if self.terdaftar > self.kuota:
            raise ValueError("Jumlah peserta melebihi kuota acara.")

    @property
    def terdaftar(self):
        """Kembalikan jumlah peserta. GUI membacanya seperti atribut biasa."""
        return len(self.peserta)

    @property
    def sisa(self):
        """Kembalikan jumlah kursi yang masih tersedia."""
        return self.kuota - self.terdaftar

    def ke_dict(self):
        """Kembalikan salinan data acara dengan format yang siap disimpan ke TXT."""
        return {
            "id": self.id,
            "nama": self.nama,
            "kategori": self.kategori,
            "ruangan": self.ruangan,
            "kuota": self.kuota,
            "peserta": [orang.copy() for orang in self.peserta],
        }
