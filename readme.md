# 🔍 DATA DETECTIVE: KODE ANOMALI

```
╔════════════════════════════════════════════════════════════╗
║  BERKAS KASUS  No. 001                                     ║
║  Judul   : Pencuri di Toko Kelontong                       ║
║  Status  : TERBUKA                                         ║
║  Barang bukti : 1 tabel transaksi (29 baris)               ║
║  Penyidik     : Pemain                                       ║
╚════════════════════════════════════════════════════════════╝
```

> Pemilik toko curiga ada transaksi ilegal yang tercatat di sistem kasir.
> Tidak ada saksi, tidak ada rekaman CCTV. Satu-satunya petunjuk: **data**.

Game ini mengajak pemain memecahkan misteri dengan cara yang dipakai analis data sungguhan:
menyaring, membandingkan, lalu menarik kesimpulan yang bisa dibuktikan.

---

## § 1. Briefing misi

Pemain harus menjawab **tiga pertanyaan** lalu mengajukannya sebagai tuduhan resmi:

| # | Pertanyaan | Bentuk jawaban |
|---|-----------|----------------|
| 1 | Siapa pelakunya? | Pilih satu dari 4 kasir |
| 2 | Pada rentang waktu apa kejadiannya? | Pilih satu dari 4 rentang waktu |
| 3 | Berapa transaksi ilegal yang terjadi? | Angka |

Ketiganya harus benar agar kasus dinyatakan selesai.

---

## § 2. Perlengkapan penyidik (instalasi)

**Kebutuhan:** Python 3.10 atau lebih baru dan koneksi internet untuk memasang pustaka.

Simpan `data_detective_app.py` di sebuah folder, buka terminal di folder itu, lalu:

**Windows**
```bash
python -m venv .venv
.venv\Scripts\activate
pip install streamlit pandas numpy
streamlit run data_detective_app.py
```

**macOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install streamlit pandas numpy
streamlit run data_detective_app.py
```

Browser akan terbuka otomatis di `http://localhost:8501`.



---

## § 3. Prosedur penyelidikan (cara bermain)


### Langkah demi langkah

1. **Baca datasetnya.** Satu baris = satu transaksi. Kolom: `jam` (0–23), `kasir`, `total` (Rp), `hari`.
2. **Selidiki di Notebook.** Pilih tahap yang nyaman (lihat tabel di bawah). Boleh pindah tahap kapan saja.
3. **Tempel temuan ke papan.** Setelah menjalankan analisis, ketik temuanmu dengan kata-kata sendiri (opsional), lalu klik **📌 Tempel sebagai clue**.
4. **Kumpulkan minimal 2 clue.** Sebelum itu, tuduhan akan ditolak.
5. **Ajukan tuduhan.** Isi formulir di bagian bawah.

### Tiga tahap Notebook


| 🟢 **1: Pilih & Klik :** Memilih kolom, operator, dan nilai dari dropdown (Terbentuk otomatis dan ditampilkan)
| 🟡 **2: Isi Bagian Kosong :**  Mengisi dua angka pada kode yang sudah ada (Fill blank)
| 🔴 **3: Kode Bebas :** Menulis Python sendiri; hasilnya disimpan ke variabel `hasil` (Pemain yang tulis)

Di Tahap 3, tersedia `data` (tabel transaksi), `pd` (pandas), dan `np` (numpy).
Buka **🧾 Kartu contekan** di bawah Notebook kalau lupa sintaksnya.

Kalau kodemu salah, pesan error diterjemahkan ke bahasa biasa, misalnya
*"Kolom 'kolomx' tidak ditemukan. Kolom yang tersedia: jam, kasir, total, hari."*

### Sistem skor

```
Skor = 100  −  10 × (tuduhan salah)  −  3 × (query setelah query ke-6)
       (minimum 20)
```

| Skor        | Peringkat            |
|-------------|----------------------|
| 85 ke atas  | 🏅 Detektif Senior  |
| 60 – 84     | 🥈 Detektif Handal  |
| di bawah 60 | 🥉 Detektif Junior  |

Tuduhan yang salah tidak membocorkan jawaban. Game hanya menandai bagian mana yang
benar (✅) dan salah (❌).

**Empat misi** di bagian atas melacak progresmu: jalankan analisis pertama, tempel 2 clue,
coba analisis dengan kode (Tahap 2 atau 3), lalu ajukan tuduhan yang benar.

---

## § 4. Metode forensik: data science di balik kasus

Pemain mengira sedang main detektif. Sebenarnya mereka mempraktikkan alur kerja analisis data.

| Yang dilakukan di game | Konsep data science | Contoh kode |
|------------------------|---------------------|-------------|
| Menyaring transaksi sebelum jam 6 pagi | **Filtering** (boolean mask) | `data[data["jam"] < 6]` |
| Mencari nominal besar *dan* dini hari | **Kondisi gabungan** | `data[(data["total"] > 500000) & (data["jam"] < 6)]` |
| Menjumlahkan nominal per kasir | **Agregasi** (`groupby`) | `dini.groupby("kasir")["total"].sum()` |
| Mengurutkan dari yang terbesar | **Sorting** | `.sort_values(ascending=False)` |
| Menandai transaksi yang tidak wajar | **Deteksi anomali** | jam tidak lazim + nominal jauh di atas rata-rata |
| Menempel clue dan mencari polanya | **Menyusun bukti** | catatan temuan sendiri |
| Dihukum karena terlalu banyak query | **Efisiensi analisis** | berpikir sebelum menjalankan |

### Jebakan yang sengaja dipasang: *red herring*

Ada **4 transaksi bernominal besar** di dataset, tetapi hanya 3 yang ilegal.
Satu lagi (nominal besar, tapi siang hari, kasir lain) adalah transaksi sah.

Pemain yang hanya memfilter `total > 800000` akan mendapat **4 baris** dan menuduh dengan jumlah salah.
Pelajarannya: **satu variabel saja jarang cukup**. Kesimpulan yang kuat berasal dari beberapa sudut pandang,
dan korelasi bukan berarti bukti.

### Dari klik ke kode

Alur tiga tahap meniru cara belajar coding yang wajar:

```
Pilih dropdown  →  Lihat kode yang terbentuk  →  Isi bagian kosong  →  Tulis sendiri                                
```

Di Tahap 1 Pemain **melihat kode Python asli** muncul dari pilihan mereka. Itu jembatan paling
ringan dari "klik" menuju "kode".

---

## § 5. Pertanyaan diskusi untuk kelas

1. Kenapa transaksi Rp850.000 di siang hari tidak ikut dituduh? Data apa yang membedakannya?
2. Apa bedanya "ada transaksi besar" dengan "ada transaksi mencurigakan"?
3. Kalau pelakunya lebih pintar dan hanya mencuri Rp50.000 per transaksi, apakah metode kita masih menemukannya?
4. Kenapa game mengurangi skor untuk query berlebihan? Apa yang hilang kalau kita mencoba semua kemungkinan secara acak?

---

## § 6. Catatan teknis dan batasan

- **Hanya 1 kasus.** Datanya dibuat dengan seed tetap, jadi **kasusnya selalu sama** setiap kali dimainkan.
  Kasus lain (email bocor, wabah, nilai ujian) masih rencana pengembangan.
- **Progres hilang jika browser di-refresh.** Semua state hanya hidup selama satu sesi.
- **Kode Pemain dijalankan dengan `exec()` tanpa sandbox.** Aman untuk komputer sendiri atau jaringan kelas yang
  dipercaya, tetapi **jangan dipublikasikan ke internet** tanpa isolasi tambahan.

<details>
<summary>🔒 <b>Lampiran pengajar: kunci jawaban (spoiler!)</b></summary>

<br>

- **Pelaku:** Rina
- **Rentang waktu:** Dini hari (00:00–05:59)
- **Jumlah transaksi ilegal:** 3 (jam 02:00, 03:00, 04:00; nominal Rp1.100.000, Rp1.200.000, Rp950.000)
- **Red herring:** Budi, Rp850.000, jam 12:00, hari Sabtu (pesanan katering yang sah)

Jalur tercepat: `data[data["jam"] < 6]` menghasilkan tepat 3 baris, semuanya milik Rina.
Dengan 1 query + 2 clue, Pemain bisa menuduh dan mendapat skor **100** (Detektif Senior).

</details>
