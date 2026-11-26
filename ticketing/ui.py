"""Menyajikan dashboard panitia dan dialog peserta menggunakan Tkinter."""

# tkinter menyediakan jendela serta variabel yang terhubung dengan widget.
import tkinter as tk
# ttk menyediakan widget, messagebox membuka dialog, dan font mengatur tipografi.
from tkinter import font, messagebox, ttk


class TicketingUI:
    """Hubungkan aksi antarmuka dengan layanan tanpa menulis file dari widget."""

    KOLOM = {
        "id": ("ID Acara", 100),
        "nama": ("Nama Acara", 250),
        "kategori": ("Kategori", 110),
        "ruangan": ("Ruangan", 160),
        "kuota": ("Kuota", 75),
        "terdaftar": ("Terdaftar", 85),
        "sisa": ("Sisa", 65),
    }

    def __init__(self, root, layanan, contoh):
        """Bangun dashboard untuk root, layanan, dan sumber data contoh. Kembali None."""
        self.root = root
        self.layanan = layanan
        self.contoh = contoh
        self.siap = False
        self.kolom_cari = tk.StringVar(root, "Nama Acara")
        self.kata = tk.StringVar(root)
        self.kolom_urut = tk.StringVar(root, "ID Acara")
        self.arah = tk.StringVar(root, "Naik")
        self.pesan = tk.StringVar(root)
        self.statistik = tk.StringVar(root)
        self.rincian = tk.StringVar(root, "Pilih acara untuk melihat rincian.")
        self.kunci_cari = {"ID Acara": "id", "Nama Acara": "nama", "Kategori": "kategori"}
        self.kunci_urut = {label: kode for kode, (label, _) in self.KOLOM.items()}
        self.kriteria = ("nama", "")
        self.urutan = ("id", False)
        self._bangun()
        self._muat(awal=True)

    def _bangun(self):
        """Buat menu, kontrol pencarian, tabel, scrollbar, dan tombol. Kembali None."""
        self.root.title("Ticketing FMIPA")
        self.root.geometry("1040x620")
        self.root.minsize(820, 460)
        self.root.configure(background="#ffffff")
        gaya = ttk.Style(self.root)
        gaya.theme_use("clam")
        gaya.configure("TFrame", background="#ffffff")
        gaya.configure("TLabel", background="#ffffff", foreground="#252a31")
        gaya.configure("TLabelframe", background="#ffffff", bordercolor="#d6dae0")
        gaya.configure("TLabelframe.Label", background="#ffffff", foreground="#252a31")
        gaya.configure("Treeview", rowheight=29, background="#ffffff",
                       fieldbackground="#ffffff", foreground="#252a31", bordercolor="#d6dae0")
        gaya.configure("Treeview.Heading", background="#edf0f3", foreground="#252a31",
                       padding=(7, 7), bordercolor="#d6dae0")
        gaya.map("Treeview", background=[("selected", "#dce9fa")],
                 foreground=[("selected", "#173452")])
        gaya.configure("TButton", padding=(9, 5))
        gaya.configure("Utama.TButton", background="#245a9a", foreground="#ffffff")
        gaya.map("Utama.TButton", background=[("active", "#1c497e")])
        gaya.configure("Status.TFrame", background="#edf0f3")
        gaya.configure("Status.TLabel", background="#edf0f3", foreground="#404953")

        menu = tk.Menu(self.root)
        berkas = tk.Menu(menu, tearoff=False)
        berkas.add_command(label="Simpan", command=self._simpan)
        berkas.add_command(label="Muat ulang", command=self._muat)
        berkas.add_separator()
        berkas.add_command(label="Keluar", command=self.root.destroy)
        menu.add_cascade(label="Berkas", menu=berkas)
        self.root.configure(menu=menu)

        isi = ttk.Frame(self.root, padding=(18, 14))
        isi.pack(fill="both", expand=True)
        isi.columnconfigure(0, weight=1)
        isi.rowconfigure(3, weight=1)

        kepala = ttk.Frame(isi)
        kepala.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.font_judul = font.nametofont("TkDefaultFont", root=self.root).copy()
        self.font_judul.configure(size=15, weight="bold")
        ttk.Label(kepala, text="Daftar Acara", font=self.font_judul).pack(side="left")
        ttk.Button(kepala, text="Tambah Acara", command=self._tambah,
                   style="Utama.TButton").pack(side="right")

        alat = ttk.Frame(isi)
        alat.grid(row=2, column=0, sticky="ew", pady=(0, 9))
        alat.columnconfigure(2, weight=1)
        ttk.Label(alat, text="Cari menurut").grid(row=0, column=0, sticky="w", padx=(0, 6))
        ttk.Combobox(alat, textvariable=self.kolom_cari, values=tuple(self.kunci_cari),
                     state="readonly", width=13).grid(row=0, column=1, padx=(0, 6))
        masukan = ttk.Entry(alat, textvariable=self.kata)
        masukan.grid(row=0, column=2, sticky="ew", padx=(0, 6))
        masukan.bind("<Return>", self._cari)
        ttk.Button(alat, text="Cari", command=self._cari).grid(row=0, column=3, padx=(0, 6))
        ttk.Button(alat, text="Tampilkan semua", command=self._reset).grid(row=0, column=4)

        urut = ttk.Frame(isi)
        urut.grid(row=4, column=0, sticky="ew", pady=(8, 0))
        ttk.Label(urut, text="Urut menurut").pack(side="left", padx=(0, 6))
        ttk.Combobox(urut, textvariable=self.kolom_urut, values=tuple(self.kunci_urut),
                     state="readonly", width=13).pack(side="left", padx=(0, 6))
        ttk.Combobox(urut, textvariable=self.arah, values=("Naik", "Turun"),
                     state="readonly", width=8).pack(side="left", padx=(0, 6))
        ttk.Button(urut, text="Urutkan", command=self._urut).pack(side="left")

        bidang = ttk.Frame(isi)
        bidang.grid(row=3, column=0, sticky="nsew")
        self.tabel = ttk.Treeview(bidang, columns=tuple(self.KOLOM), show="headings",
                                 selectmode="browse", height=7)
        for kode, (label, lebar) in self.KOLOM.items():
            self.tabel.heading(kode, text=label)
            self.tabel.column(kode, width=lebar, minwidth=55,
                              anchor="e" if kode in {"kuota", "terdaftar", "sisa"} else "w")
        self.tabel.tag_configure("alternatif", background="#f6f7f9")
        vertikal = ttk.Scrollbar(bidang, orient="vertical", command=self.tabel.yview)
        horizontal = ttk.Scrollbar(bidang, orient="horizontal", command=self.tabel.xview)
        self.tabel.configure(yscrollcommand=vertikal.set, xscrollcommand=horizontal.set)
        self.tabel.grid(row=0, column=0, sticky="nsew")
        vertikal.grid(row=0, column=1, sticky="ns")
        horizontal.grid(row=1, column=0, sticky="ew")
        bidang.columnconfigure(0, weight=1)
        bidang.rowconfigure(0, weight=1)

        tombol = ttk.Frame(isi)
        tombol.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        for label, aksi in (
            ("Peserta", self._peserta), ("Ubah", self._ubah), ("Hapus", self._hapus)
        ):
            ttk.Button(tombol, text=label, command=aksi).pack(side="left", padx=(0, 6))
        ttk.Button(tombol, text="Muat Ulang", command=self._muat).pack(side="right")
        ttk.Button(tombol, text="Simpan", command=self._simpan).pack(side="right", padx=6)

        rincian = ttk.LabelFrame(isi, text="Acara terpilih", padding=(9, 5))
        rincian.grid(row=5, column=0, sticky="ew", pady=(10, 0))
        ttk.Label(rincian, textvariable=self.rincian, wraplength=745).pack(anchor="w")
        self.tabel.bind("<<TreeviewSelect>>", self._tampilkan_rincian)
        self.tabel.bind("<Return>", lambda event: self._peserta())

        status = ttk.Frame(isi, style="Status.TFrame", padding=(8, 5))
        status.grid(row=6, column=0, sticky="ew", pady=(10, 0))
        ttk.Label(status, textvariable=self.pesan, style="Status.TLabel",
                  wraplength=420).pack(side="left")
        ttk.Label(status, textvariable=self.statistik, style="Status.TLabel").pack(side="right")

    def _tampilkan_rincian(self, event=None):
        """Tampilkan rincian dari pilihan tabel atau petunjuk jika pilihan kosong."""
        pilihan = self.tabel.selection()
        if not pilihan:
            self.rincian.set("Pilih acara untuk melihat rincian.")
            return
        acara = self.layanan.ambil(pilihan[0])
        self.rincian.set(f"{acara.id}  |  {acara.nama}  |  {acara.ruangan}  |  "
                         f"{acara.terdaftar}/{acara.kuota} peserta")

    def _tampilkan(self):
        """Perbarui baris dan ringkasan berdasarkan filter dan urutan aktif. Kembali None."""
        kolom, kata = self.kriteria
        kolom_urut, menurun = self.urutan
        hasil = self.layanan.cari(kolom, kata)
        hasil = self.layanan.urutkan(hasil, kolom=kolom_urut, menurun=menurun)
        pilihan = self.tabel.selection()
        self.tabel.delete(*self.tabel.get_children())
        for i, acara in enumerate(hasil):
            self.tabel.insert("", "end", iid=acara.id,
                              values=tuple(getattr(acara, key) for key in self.KOLOM),
                              tags=("alternatif",) if i % 2 else ())
        if pilihan and self.tabel.exists(pilihan[0]):
            self.tabel.selection_set(pilihan[0])
        self._tampilkan_rincian()
        kuota, peserta, sisa = self.layanan.ringkasan(hasil)
        self.statistik.set(
            f"{len(hasil)} acara tampil   ·   Kuota {kuota}   ·   Terdaftar {peserta}   ·   Sisa {sisa}"
        )

    def _cari(self, event=None):
        """Terapkan kata dari formulir. event opsional berasal dari Enter. Kembali None."""
        kolom = self.kunci_cari[self.kolom_cari.get()]
        kata = self.kata.get().strip()
        self.kriteria = (kolom, kata)
        self._tampilkan()
        metode = "indeks ID (cocok persis)" if kolom == "id" else "Linear Search"
        self.pesan.set(f"Pencarian melalui {metode}." if kata else "Semua acara ditampilkan.")

    def _reset(self):
        """Kosongkan kata pencarian dan tampilkan semua acara. Kembali None."""
        self.kata.set("")
        self._cari()

    def _urut(self):
        """Terapkan Insertion Sort dengan kolom dan arah pilihan UI. Kembali None."""
        self.urutan = (self.kunci_urut[self.kolom_urut.get()], self.arah.get() == "Turun")
        self._tampilkan()
        self.pesan.set(f"Insertion Sort · {self.kolom_urut.get()} · {self.arah.get().lower()}.")

    def _muat(self, *, awal=False):
        """Muat data aktif, atau buat dari contoh jika awal dan file hilang. Kembali None."""
        try:
            try:
                jumlah = self.layanan.muat()
            except FileNotFoundError:
                if not awal:
                    raise
                jumlah = self.layanan.inisialisasi(self.contoh)
            self.siap = True
            self._tampilkan()
            self.pesan.set(f"{jumlah} acara dimuat dari data proyek.")
        except FileNotFoundError:
            self.pesan.set("File data tidak ditemukan. Tabel dalam memori dipertahankan.")
            messagebox.showerror("Data tidak ditemukan", self.pesan.get(), parent=self.root)
        except (ValueError, OSError) as error:
            self.siap = False
            self.pesan.set("Muat gagal. Perbaiki atau pulihkan TXT, lalu tekan Muat Ulang.")
            messagebox.showerror("Gagal memuat", str(error), parent=self.root)

    def _aksi(self, operasi, pesan, *argumen, induk=None, **nilai):
        """Kirim argumen ke operasi dan kembalikan True jika berhasil."""
        if not self.siap:
            messagebox.showwarning("Data belum siap", "Pulihkan file lalu pilih Muat Ulang.",
                                   parent=induk or self.root)
            return False
        try:
            operasi(*argumen, **nilai)
        except (ValueError, OSError) as error:
            messagebox.showerror("Aksi gagal", str(error), parent=induk or self.root)
            return False
        self._tampilkan()
        self.pesan.set(pesan)
        return True

    def _simpan(self):
        """Simpan snapshot aktif melalui layanan. Kembali None."""
        self._aksi(self.layanan.simpan, "Data tersimpan di data/acara.txt.")

    def _pilihan(self):
        """Kembalikan ID baris terpilih atau None setelah menampilkan pengingat."""
        pilihan = self.tabel.selection()
        if not pilihan:
            messagebox.showinfo("Pilih acara", "Pilih satu baris pada tabel acara.",
                                parent=self.root)
            return None
        return pilihan[0]

    def _tambah(self):
        """Buka formulir acara baru. Kembali None."""
        kolom = []
        for nama in ("nama", "kategori", "ruangan", "kuota"):
            label = self.KOLOM[nama][0]
            kolom.append((nama, label, ""))
        self._form("Tambah acara", kolom, self.layanan.tambah_otomatis,
                   "Acara baru tersimpan.")

    def _ubah(self):
        """Buka formulir data acara terpilih dengan ID tetap. Kembali None."""
        kode = self._pilihan()
        if kode is None:
            return
        acara = self.layanan.ambil(kode)
        kolom = []
        for nama in ("nama", "kategori", "ruangan", "kuota"):
            label = self.KOLOM[nama][0]
            kolom.append((nama, label, getattr(acara, nama)))
        self._form(f"Ubah {kode}", kolom, self.layanan.ubah,
                   "Perubahan acara tersimpan.", kode)

    def _hapus(self):
        """Minta konfirmasi sebelum menghapus acara beserta tiket. Kembali None."""
        kode = self._pilihan()
        if kode and messagebox.askyesno(
            "Hapus acara", f"Hapus {kode} beserta tiket pesertanya?", parent=self.root
        ):
            self._aksi(self.layanan.hapus, f"{kode} dihapus.", kode)

    def _form(self, judul, kolom, operasi, pesan, *argumen, induk=None):
        """Buka formulir dari daftar kolom dan kembalikan status penyimpanan."""
        tersimpan = False
        induk = induk or self.root
        dialog = tk.Toplevel(induk)
        dialog.title(judul)
        dialog.transient(induk)
        dialog.resizable(False, False)
        isi = ttk.Frame(dialog, padding=16)
        isi.pack(fill="both", expand=True)
        isian = {}
        for baris, (key, label, nilai) in enumerate(kolom, start=1):
            ttk.Label(isi, text=label).grid(row=baris, column=0, sticky="w", padx=(0, 12))
            if key == "kategori":
                entri = ttk.Combobox(isi, width=31, state="readonly",
                                     values=self.layanan.pilihan_kategori())
                entri.set(nilai)
            else:
                entri = ttk.Entry(isi, width=33)
                entri.insert(0, str(nilai))
            entri.grid(row=baris, column=1, sticky="ew", pady=3)
            isian[key] = entri

        def simpan(event=None):
            """Kirim nilai formulir dari tombol atau Enter. Kembali None."""
            nonlocal tersimpan
            nilai = {}
            for nama, entri in isian.items():
                nilai[nama] = entri.get()

            tersimpan = self._aksi(operasi, pesan, *argumen, induk=dialog, **nilai)
            if tersimpan:
                dialog.destroy()

        ttk.Button(isi, text="Batal", command=dialog.destroy).grid(
            row=len(kolom) + 1, column=0, sticky="w", pady=(10, 0))
        ttk.Button(isi, text="Simpan", command=simpan, style="Utama.TButton").grid(
            row=len(kolom) + 1, column=1, sticky="e", pady=(10, 0))
        dialog.bind("<Return>", simpan)
        dialog.wait_visibility()
        grab_sebelum = dialog.grab_current()
        dialog.grab_set()
        isian[kolom[0][0]].focus_set()
        dialog.wait_window()
        if grab_sebelum is not None and grab_sebelum.winfo_exists():
            grab_sebelum.grab_set()
        return tersimpan

    def _peserta(self):
        """Tampilkan tabel peserta dan tombol daftar/batalkan tiket. Kembali None."""
        kode = self._pilihan()
        if kode is None:
            return
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Peserta {kode}")
        dialog.transient(self.root)
        isi = ttk.Frame(dialog, padding=16)
        isi.pack(fill="both", expand=True)
        teks = tk.StringVar(dialog)
        ttk.Label(isi, textvariable=teks).pack(anchor="w", pady=(0, 8))
        bingkai = ttk.Frame(isi)
        bingkai.pack(fill="both", expand=True)
        tabel = ttk.Treeview(bingkai, columns=("npm", "nama", "prodi"), height=7,
                             show="headings", selectmode="browse")
        for key, label, lebar in (
            ("npm", "NPM", 140), ("nama", "Nama", 195), ("prodi", "Program Studi", 175)
        ):
            tabel.heading(key, text=label)
            tabel.column(key, width=lebar)
        tabel.pack(side="left", fill="both", expand=True)
        gulir = ttk.Scrollbar(bingkai, orient="vertical", command=tabel.yview)
        gulir.pack(side="right", fill="y")
        tabel.configure(yscrollcommand=gulir.set)

        def tampilkan():
            """Muat ulang baris dan kuota dari acara aktif. Kembali None."""
            acara = self.layanan.ambil(kode)
            teks.set(f"{acara.nama} · {acara.terdaftar}/{acara.kuota} terdaftar")
            tabel.delete(*tabel.get_children())
            for orang in acara.peserta:
                tabel.insert("", "end", iid=orang["npm"],
                             values=(orang["npm"], orang["nama"], orang["prodi"]))

        def daftar():
            """Buka formulir pendaftaran tiket dan segarkan tabel. Kembali None."""
            isian = [("npm", "NPM", ""), ("nama", "Nama", ""), ("prodi", "Program Studi", "")]
            if self._form("Daftarkan peserta", isian, self.layanan.daftar,
                          "Tiket peserta tersimpan.", kode, induk=dialog):
                tampilkan()

        def batalkan():
            """Batalkan tiket terpilih setelah konfirmasi. Kembali None."""
            pilihan = tabel.selection()
            if not pilihan:
                messagebox.showinfo("Pilih peserta", "Pilih satu baris peserta.", parent=dialog)
                return
            npm = pilihan[0]
            if messagebox.askyesno("Batalkan tiket", f"Batalkan tiket NPM {npm}?", parent=dialog):
                if self._aksi(self.layanan.batalkan,
                              "Tiket dibatalkan.", kode, npm, induk=dialog):
                    tampilkan()

        tombol = ttk.Frame(isi)
        tombol.pack(fill="x", pady=(9, 0))
        ttk.Button(tombol, text="Daftarkan Peserta", command=daftar,
                   style="Utama.TButton").pack(side="left", padx=(0, 6))
        ttk.Button(tombol, text="Batalkan Tiket", command=batalkan).pack(side="left")
        ttk.Button(tombol, text="Tutup", command=dialog.destroy).pack(side="right")
        tampilkan()
        dialog.wait_visibility()
        dialog.grab_set()
