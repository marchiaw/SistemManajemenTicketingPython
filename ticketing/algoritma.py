"""Menyediakan algoritma pencarian, pengurutan, dan penjumlahan kuota."""


def linear_search(data, kata, kolom):
    """Periksa atribut kolom pada tiap acara. Kembalikan list hasil pencarian."""
    hasil = []
    for acara in data:
        # getattr membaca atribut berdasarkan nama kolom, misalnya acara.nama.
        nilai = getattr(acara, kolom).casefold()
        if kata in nilai:
            hasil.append(acara)
    return hasil


def insertion_sort(data, kunci, menurun=False):
    """Kembalikan salinan list yang diurutkan memakai fungsi kunci."""
    hasil = list(data)

    # Anggap bagian kiri sudah urut. Sisipkan item berikutnya pada posisi tepat.
    for i in range(1, len(hasil)):
        item = hasil[i]
        nilai = kunci(item)
        posisi = i

        while posisi > 0:
            nilai_kiri = kunci(hasil[posisi - 1])
            if menurun:
                perlu_geser = nilai_kiri < nilai
            else:
                perlu_geser = nilai_kiri > nilai

            if not perlu_geser:
                break
            hasil[posisi] = hasil[posisi - 1]
            posisi -= 1

        hasil[posisi] = item

    return hasil


def jumlah_kuota(*angka):
    """Kembalikan jumlah semua angka. Banyaknya argumen boleh berbeda-beda."""
    return sum(angka)
