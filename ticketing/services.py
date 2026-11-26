"""Mengelola acara, pencarian, dan tiket untuk antarmuka pengguna."""

# Algoritma dapat diuji sendiri karena tidak bergantung pada GUI.
from .algoritma import insertion_sort, jumlah_kuota, linear_search
# Acara memeriksa aturan data, validasi memeriksa ID dan data peserta.
from .model import Acara
from .validasi import buat_peserta, id_acara, npm_peserta


class LayananTicketing:
    """Simpan objek acara dalam dictionary dengan ID sebagai kunci."""

    KOLOM_URUT = ("id", "nama", "kategori", "ruangan", "kuota", "terdaftar", "sisa")

    def __init__(self, penyimpanan):
        """Siapkan dictionary kosong dan simpan objek penyimpanan. Kembali None."""
        self.penyimpanan = penyimpanan
        self._acara = {}

    def muat(self):
        """Muat file aktif dan kembalikan jumlah acara yang dibaca."""
        daftar = self.penyimpanan.muat()
        self._acara = {acara.id: acara for acara in daftar}
        return len(self._acara)

    def inisialisasi(self, sumber):
        """Simpan data contoh dari sumber, lalu kembalikan jumlah acaranya."""
        daftar = sumber.muat()
        self._terapkan({acara.id: acara for acara in daftar})
        return len(self._acara)

    def simpan(self):
        """Simpan semua acara aktif ke file. Kembali None."""
        self.penyimpanan.simpan(self._acara.values())

    def _terapkan(self, perubahan):
        """Simpan dictionary perubahan sebelum mengganti data aktif. Kembali None."""
        self.penyimpanan.simpan(perubahan.values())
        self._acara = perubahan

    def _simpan_acara(self, acara):
        """Masukkan satu acara baru atau hasil edit ke salinan data. Kembali None."""
        perubahan = self._acara.copy()
        perubahan[acara.id] = acara
        self._terapkan(perubahan)

    def ambil(self, kode):
        """Kembalikan objek Acara dengan ID kode atau naikkan ValueError."""
        kode = id_acara(kode)
        acara = self._acara.get(kode)
        if acara is None:
            raise ValueError(f"Acara {kode} tidak ditemukan.")
        return acara

    def tambah_otomatis(self, nama, kategori, ruangan, kuota):
        """Buat acara memakai nomor berikutnya dan kembalikan objek yang tersimpan."""
        nomor = self.penyimpanan.nomor_terakhir + 1
        if nomor > 9999:
            raise ValueError("Seluruh nomor acara telah digunakan.")
        return self.tambah(f"EVT-{nomor:04d}", nama, kategori, ruangan, kuota)

    def pilihan_kategori(self):
        """Kembalikan kategori bawaan dan kategori tambahan dari data lama."""
        pilihan = ["Seminar", "Lokakarya", "Lomba", "Diskusi", "Lainnya"]
        for acara in self._acara.values():
            if acara.kategori not in pilihan:
                pilihan.append(acara.kategori)
        return pilihan

    def tambah(self, kode, nama, kategori, ruangan, kuota):
        """Buat dan simpan Acara baru dari data formulir, lalu kembalikan objeknya."""
        acara = Acara(kode, nama, kategori, ruangan, kuota)
        if acara.id in self._acara:
            raise ValueError(f"ID {acara.id} sudah digunakan.")
        self._simpan_acara(acara)
        return acara

    def ubah(self, kode, **perubahan):
        """Perbarui kolom yang dikirim melalui **perubahan dan kembalikan Acara."""
        data = self.ambil(kode).ke_dict()
        for kolom in perubahan:
            if kolom not in ("nama", "kategori", "ruangan", "kuota"):
                raise ValueError("Kolom perubahan acara tidak dikenal.")

        data.update(perubahan)
        acara = Acara(**data)
        self._simpan_acara(acara)
        return acara

    def hapus(self, kode):
        """Hapus acara ber-ID kode beserta tiketnya. Kembali None."""
        acara = self.ambil(kode)
        perubahan = self._acara.copy()
        del perubahan[acara.id]
        self._terapkan(perubahan)

    def daftar(self, kode, npm, nama, prodi):
        """Simpan peserta pada acara ber-ID kode dan kembalikan data peserta."""
        data = self.ambil(kode).ke_dict()
        peserta = buat_peserta(npm, nama, prodi)
        data["peserta"].append(peserta)
        self._simpan_acara(Acara(**data))
        return peserta

    def batalkan(self, kode, npm):
        """Hapus peserta berdasarkan NPM dari acara ber-ID kode. Kembali None."""
        data = self.ambil(kode).ke_dict()
        npm = npm_peserta(npm)
        for peserta in data["peserta"]:
            if peserta["npm"] == npm:
                data["peserta"].remove(peserta)
                self._simpan_acara(Acara(**data))
                return
        raise ValueError("NPM belum terdaftar di acara ini.")

    def cari(self, kolom="nama", kata=""):
        """Kembalikan list acara yang cocok dengan kata pada kolom pencarian."""
        if kolom not in ("id", "nama", "kategori"):
            raise ValueError("Kolom pencarian tidak dikenal.")

        kata = kata.strip()
        if not kata:
            return list(self._acara.values())

        if kolom == "id":
            # Langsung ambil berdasarkan kunci. Tidak perlu memeriksa semua baris.
            acara = self._acara.get(kata.upper())
            if acara is None:
                return []
            return [acara]

        return linear_search(self._acara.values(), kata.casefold(), kolom)

    def urutkan(self, data, *, kolom, menurun=False):
        """Kembalikan list data terurut berdasarkan kolom dan pilihan arah."""
        if kolom not in self.KOLOM_URUT:
            raise ValueError("Kolom pengurutan tidak dikenal.")

        if kolom in ("kuota", "terdaftar", "sisa"):
            return insertion_sort(data, kunci=lambda acara: getattr(acara, kolom),
                                  menurun=menurun)

        return insertion_sort(data, kunci=lambda acara: getattr(acara, kolom).casefold(),
                              menurun=menurun)

    def ringkasan(self, data):
        """Kembalikan total kuota, total peserta, dan sisa dari baris yang tampil."""
        daftar_kuota = []
        daftar_peserta = []
        for acara in data:
            daftar_kuota.append(acara.kuota)
            daftar_peserta.append(acara.terdaftar)

        # * membuka list menjadi argumen, misalnya jumlah_kuota(2, 30, 45).
        kuota = jumlah_kuota(*daftar_kuota)
        peserta = jumlah_kuota(*daftar_peserta)
        return kuota, peserta, kuota - peserta
