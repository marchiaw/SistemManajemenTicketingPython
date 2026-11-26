"""Menguji algoritma, validasi, dan penyimpanan tanpa mengimpor GUI."""

# unittest menyediakan TestCase, assertion, dan pelaksana pengujian.
import unittest
# Path membangun lokasi file uji di direktori sementara.
from pathlib import Path
# TemporaryDirectory memisahkan data pengujian dari file data pengguna.
from tempfile import TemporaryDirectory
# patch menyimulasikan kegagalan penggantian file.
from unittest.mock import patch

# Modul aplikasi yang diuji secara independen.
from ticketing.algoritma import jumlah_kuota, insertion_sort
from ticketing.services import LayananTicketing
from ticketing.storage import PenyimpananTXT


class TestTicketing(unittest.TestCase):
    """Uji aturan acara, hasil pencarian/pengurutan, dan persistensi TXT."""

    def setUp(self):
        """Buat layanan dan direktori data terisolasi sebelum tiap tes. Kembali None."""
        folder = TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.path = Path(folder.name) / "acara.txt"
        self.layanan = LayananTicketing(PenyimpananTXT(self.path))

    def test_crud_dan_id_duplikat(self):
        """Pastikan tambah, ubah, hapus dan penolakan duplikat bekerja."""
        self.layanan.tambah("evt-0001", "Seminar", "Umum", "Aula", "4")
        with self.assertRaises(ValueError):
            self.layanan.tambah("EVT-0001", "Lainnya", "Umum", "Aula", 5)
        hasil = self.layanan.ubah("EVT-0001", ruangan="Lab", kuota=12)
        self.assertEqual((hasil.ruangan, hasil.kuota), ("Lab", 12))
        self.layanan.hapus("EVT-0001")
        self.assertEqual(self.layanan.cari("id", "EVT-0001"), [])

    def test_validasi_masukan(self):
        """Pastikan nilai cacat ditolak sebelum program menulis file."""
        for kode, nama, kuota in (
            ("EVT-0000", "Python", 2), ("EVT-0001", "   ", 2),
            ("EVT-0001", "Python", -1), ("EVT-0001", "Python", True),
            ("EVT-0001", "Python", "2.5"),
        ):
            with self.subTest(kode=kode, nama=nama, kuota=kuota):
                with self.assertRaises(ValueError):
                    self.layanan.tambah(kode, nama, "Kelas", "Lab", kuota)
        self.assertFalse(self.path.exists())

    def test_cari_nama_id_kategori(self):
        """Uji substring nama/kategori, ID persis, normalisasi dan hasil kosong."""
        acara = self.layanan.tambah("EVT-0001", "Seminar Python", "Teknologi", "Aula", 3)
        for kolom, kata in (("nama", " PYTHON "), ("id", "evt-0001"), ("kategori", "noLOgi")):
            with self.subTest(kolom=kolom):
                self.assertEqual(self.layanan.cari(kolom, kata), [acara])
        self.assertEqual(self.layanan.cari("nama", "Java"), [])
        self.assertEqual(self.layanan.cari("id", "0001"), [])

    def test_insertion_sort_angka_dan_stabilitas(self):
        """Uji kedua arah, seri yang stabil, serta input yang tetap utuh."""
        tambahkan = self.layanan.tambah
        kecil = tambahkan("EVT-0001", "Beta", "Lomba", "Aula", 2)
        besar = tambahkan("EVT-0002", "Alfa", "Lomba", "Aula", 80)
        seri = tambahkan("EVT-0003", "Gama", "Lomba", "Aula", 2)
        data = [kecil, besar, seri]
        self.assertEqual(self.layanan.urutkan(data, kolom="kuota"), [kecil, seri, besar])
        self.assertEqual(self.layanan.urutkan(data, kolom="kuota", menurun=True),
                         [besar, kecil, seri])
        self.assertEqual(self.layanan.urutkan(data, kolom="nama"), [besar, kecil, seri])
        self.assertEqual(data, [kecil, besar, seri])
        self.assertEqual(insertion_sort([], kunci=int), [])

    def test_kuota_dan_npm_peserta(self):
        """Uji NPM unik, kuota penuh, batas edit kuota, dan pemulihan kursi."""
        kode = "EVT-0001"
        self.layanan.tambah(kode, "Seminar", "Umum", "Aula", 2)
        self.layanan.daftar(kode, "0007", "Nadia", "SI")
        with self.assertRaisesRegex(ValueError, "NPM sudah"):
            self.layanan.daftar(kode, "0007", "Nadia", "SI")
        self.layanan.daftar(kode, "0008", "Raka", "SI")
        with self.assertRaisesRegex(ValueError, "melebihi kuota"):
            self.layanan.daftar(kode, "0009", "Maya", "SI")
        with self.assertRaisesRegex(ValueError, "melebihi kuota"):
            self.layanan.ubah(kode, kuota=1)
        self.layanan.batalkan(kode, "0008")
        self.assertEqual(self.layanan.ambil(kode).sisa, 1)

    def test_persistensi_dan_kosong_valid(self):
        """Pastikan instance baru membaca data, NPM nol awal, dan list kosong valid."""
        kode = "EVT-0001"
        self.layanan.tambah(kode, "Kelas Python", "Kelas", "Aula", 3)
        self.layanan.daftar(kode, "0001", "Nadia", "SI")
        baru = LayananTicketing(PenyimpananTXT(self.path))
        self.assertEqual(baru.muat(), 1)
        self.assertEqual(baru.ambil(kode).ke_dict(), self.layanan.ambil(kode).ke_dict())
        self.assertEqual(baru.ambil(kode).peserta[0]["npm"], "0001")
        baru.hapus(kode)
        self.assertEqual(self.layanan.muat(), 0)

    def test_file_hilang_kosong_korup(self):
        """Uji file hilang dan pertahankan data aktif ketika TXT gagal dimuat."""
        with self.assertRaises(FileNotFoundError):
            self.layanan.muat()
        acara = self.layanan.tambah("EVT-0001", "Python", "Kelas", "Lab", 2)
        for isi in ("", "{rusak", '{"versi": 1, "acara": [8]}', '{"versi": true, "acara": []}'):
            with self.subTest(isi=isi):
                with open(self.path, "w", encoding="utf-8") as file:
                    file.write(isi)
                with self.assertRaises(ValueError):
                    self.layanan.muat()
                self.assertEqual(self.layanan.ambil(acara.id), acara)

    def test_gagal_simpan_mempertahankan_snapshot(self):
        """Pastikan perubahan gagal tidak mengubah memori maupun file aktif."""
        acara = self.layanan.tambah("EVT-0001", "Python", "Kelas", "Lab", 2)
        with patch("ticketing.storage.os.replace", side_effect=OSError("gagal")):
            with self.assertRaises(OSError):
                self.layanan.ubah(acara.id, kuota=5)
        self.assertEqual(self.layanan.ambil(acara.id), acara)
        data_di_file = PenyimpananTXT(self.path).muat()
        self.assertEqual(data_di_file[0].ke_dict(), acara.ke_dict())
        self.assertEqual(list(self.path.parent.iterdir()), [self.path])

    def test_agregasi_kuota(self):
        """Uji agregasi argumen posisi, termasuk tabel yang tidak memiliki hasil."""
        acara = self.layanan.tambah("EVT-0001", "Python", "Kelas", "Lab", 12)
        self.assertEqual(jumlah_kuota(2, 3, 5), 10)
        self.assertEqual(self.layanan.ringkasan([acara]), (12, 0, 12))
        self.assertEqual(self.layanan.ringkasan([]), (0, 0, 0))

    def test_optimasi_pencarian_id(self):
        """Bandingkan hasil pencarian ID dengan scan pada 1000 data sintetis."""
        data = [
            self._buat_acara_uji(i)
            for i in range(1, 1001)
        ]
        self.layanan.penyimpanan.simpan(data)
        self.layanan.muat()
        hasil = []
        diperiksa = 0
        for acara in data:
            diperiksa += 1
            if acara.id == "EVT-1000":
                hasil.append(acara)
                break
        self.assertEqual(diperiksa, 1000)
        with patch("ticketing.services.linear_search") as pemindaian:
            hasil_indeks = self.layanan.cari("id", "evt-1000")
            self.assertEqual(hasil_indeks[0].ke_dict(), hasil[0].ke_dict())
            pemindaian.assert_not_called()

    @staticmethod
    def _buat_acara_uji(nomor):
        """Kembalikan objek Acara sintetis menggunakan nomor 1 sampai 9999."""
        # Acara dibangun langsung untuk membuat dataset tanpa 1000 penulisan file.
        from ticketing.model import Acara

        return Acara(f"EVT-{nomor:04d}", f"Acara {nomor}", "Demo", "Aula", 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
