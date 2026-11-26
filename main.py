"""Titik masuk aplikasi desktop manajemen acara FMIPA."""

# tkinter membuat jendela utama dan menyediakan exception ketika GUI gagal dibuka.
import tkinter as tk
# Path menentukan lokasi data relatif terhadap proyek, tidak bergantung pada cwd.
from pathlib import Path

# Layanan menangani aturan aplikasi, penyimpanan menangani berkas, UI menangani aksi.
from ticketing.services import LayananTicketing
from ticketing.storage import PenyimpananTXT
from ticketing.ui import TicketingUI


def main():
    """Buka aplikasi dan proses event hingga ditutup. Kembali kode keluar integer."""
    folder_data = Path(__file__).resolve().parent / "data"
    try:
        root = tk.Tk()
    except tk.TclError as error:
        print(f"Jendela aplikasi tidak dapat dibuka ({error}).")
        return 1

    layanan = LayananTicketing(PenyimpananTXT(folder_data / "acara.txt"))
    contoh = PenyimpananTXT(folder_data / "contoh_acara.txt")
    TicketingUI(root, layanan, contoh)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
