import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Data Detective - Kode: Anomali", page_icon="🔍", layout="wide")

KASIR = ["Budi", "Rina", "Sari", "Dedi"]
WAKTU = [
    "Dini hari (00:00-05:59)",
    "Pagi (06:00-11:59)",
    "Siang-sore (12:00-17:59)",
    "Malam (18:00-23:59)",
]
WAKTU_BENAR = WAKTU[0]
PILIH = "— pilih —"
MIN_CLUE = 2


# ---------------------------------------------------------------------------
# DATA KASUS: "Pencuri di Toko Kelontong"
# ---------------------------------------------------------------------------
@st.cache_data
def load_data():
    np.random.seed(42)
    n = 25
    jam = np.random.randint(7, 22, n).tolist()
    kasir = np.random.choice(KASIR, n).tolist()
    total = (np.random.randint(15, 90, n) * 1000).tolist()
    hari = np.random.choice(
        ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"], n
    ).tolist()

    # 3 transaksi ilegal: dini hari, nominal besar, kasir yang sama
    jam += [3, 4, 2]
    kasir += ["Rina", "Rina", "Rina"]
    total += [1200000, 950000, 1100000]
    hari += ["Minggu", "Rabu", "Sabtu"]

    # red herring: nominal besar, tapi di siang hari (pesanan katering yang sah)
    jam += [12]
    kasir += ["Budi"]
    total += [850000]
    hari += ["Sabtu"]

    df = pd.DataFrame({"jam": jam, "kasir": kasir, "total": total, "hari": hari})
    return df.sample(frac=1, random_state=1).reset_index(drop=True)


data = load_data()

# kunci jawaban dihitung dari data, bukan ditulis manual
_curiga = data[data["jam"] < 6]
PELAKU_BENAR = _curiga["kasir"].mode()[0]
JUMLAH_BENAR = len(_curiga)


# ---------------------------------------------------------------------------
# STATE
# ---------------------------------------------------------------------------
DEFAULTS = {
    "clues": [],
    "n_query": 0,
    "pakai_coding": False,
    "last": None,
    "salah": 0,
    "selesai": False,
    "skor": None,
    "feedback": None,
    "intro_seen": False,
    "catatan": "",
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


def reset_game():
    for k in list(st.session_state.keys()):
        if k != "intro_seen":
            del st.session_state[k]


def mulai():
    st.session_state.intro_seen = True


def tampil_df(df, **kw):
    try:
        st.dataframe(df, width="stretch", **kw)
    except TypeError:
        st.dataframe(df, use_container_width=True, **kw)


def friendly_error(e: Exception) -> str:
    msg = str(e)
    if isinstance(e, KeyError):
        return f"Kolom {msg} tidak ditemukan. Kolom yang tersedia: jam, kasir, total, hari."
    if isinstance(e, SyntaxError):
        return "Ada bagian kode yang belum lengkap atau salah tulis. Cek tanda kurung dan tanda kutip."
    if isinstance(e, NameError):
        return f"Ada nama yang belum dikenal: {msg}. Pastikan kamu memakai variabel `data`."
    if isinstance(e, TypeError):
        return "Ada perbandingan yang tipenya tidak cocok, misalnya teks dibandingkan dengan angka."
    return f"Terjadi kesalahan: {msg}"


def jalankan(kode: str, tahap: int, label: str):
    """Jalankan kode pemain, simpan hasilnya ke state supaya tombol clue bisa memakainya."""
    try:
        ns = {"data": data.copy(), "pd": pd, "np": np}
        exec(kode, ns)
        if "hasil" not in ns:
            st.warning("Kode jalan, tapi belum ada variabel bernama `hasil`.")
            return
        st.session_state.n_query += 1
        if tahap > 1:
            st.session_state.pakai_coding = True
        st.session_state.last = {"label": label, "kode": kode, "hasil": ns["hasil"]}
    except Exception as e:
        st.error(friendly_error(e))


def ringkas(hasil) -> str:
    if isinstance(hasil, (pd.DataFrame, pd.Series)):
        return f"{len(hasil)} baris"
    return str(hasil)


def tempel_clue():
    last = st.session_state.last
    if not last:
        return
    catatan = st.session_state.catatan.strip()
    teks = catatan if catatan else f"{last['label']} → {ringkas(last['hasil'])}"
    if teks not in st.session_state.clues:
        st.session_state.clues.append(teks)
    st.session_state.catatan = ""


def hitung_skor() -> int:
    return max(20, 100 - 10 * st.session_state.salah - 3 * max(0, st.session_state.n_query - 6))


def peringkat(skor: int) -> str:
    if skor >= 85:
        return "🏅 Detektif Senior"
    if skor >= 60:
        return "🥈 Detektif Handal"
    return "🥉 Detektif Junior"


# ---------------------------------------------------------------------------
# HEADER, TUJUAN, CARA BERMAIN
# ---------------------------------------------------------------------------
st.title("🔍 Data Detective: Kode Anomali")
st.subheader("Kasus: Pencuri di Toko Kelontong")
st.markdown(
    "Pemilik toko curiga ada transaksi ilegal yang tercatat di sistem kasir. "
    "Kamu detektif yang ditugaskan. Satu-satunya petunjukmu adalah **data transaksi**."
)

st.info(
    "🎯 **Tujuanmu:** temukan **siapa pelakunya**, **pada rentang waktu apa** ia beraksi, dan "
    "**berapa transaksi ilegal** yang terjadi. Setelah yakin, ajukan tuduhanmu di bagian bawah halaman."
)

with st.expander("📖 Cara bermain", expanded=not st.session_state.intro_seen):
    st.markdown(
        """
**Langkah-langkah**
1. **Lihat datasetnya** (tabel di kiri). Satu baris = satu transaksi.
2. **Selidiki lewat Notebook** (di kanan). Mulai dari **Tahap 1** (tinggal pilih dari dropdown),
   lanjut ke **Tahap 2** (isi bagian kosong pada kode), lalu **Tahap 3** (tulis kode sendiri).
   Kamu boleh pindah tahap kapan saja.
3. **Tempel temuan penting sebagai clue** di papan investigasi. Kamu butuh minimal
   **2 clue** sebelum boleh menuduh.
4. **Ajukan tuduhan** di bagian paling bawah: pilih pelaku, rentang waktu, dan jumlah transaksi ilegal.

**Sistem skor**
- Mulai dari **100 poin**.
- Setiap **tuduhan salah**: **-10 poin**.
- Setiap analisis setelah **6 query pertama**: **-3 poin**. Berpikirlah dulu, jangan asal coba.
- Peringkat: 🏅 Senior (≥85), 🥈 Handal (≥60), 🥉 Junior (<60).

**Tips**
- Tidak semua yang tampak aneh itu pelaku. Periksa dari lebih dari satu sisi.
- Bingung menulis kode? Buka **Kartu contekan** di bawah Notebook.
"""
    )
    st.button("Saya mengerti, mulai investigasi!", on_click=mulai, type="primary")

# ---------------------------------------------------------------------------
# MISI + STATISTIK
# ---------------------------------------------------------------------------
misi = [
    ("Jalankan analisis pertamamu", st.session_state.n_query >= 1),
    (f"Tempel minimal {MIN_CLUE} clue di papan investigasi", len(st.session_state.clues) >= MIN_CLUE),
    ("Coba analisis dengan kode (Tahap 2 atau 3)", st.session_state.pakai_coding),
    ("Ajukan tuduhan yang benar", st.session_state.selesai),
]
selesai_count = sum(1 for _, ok in misi if ok)

col_m1, col_m2 = st.columns([1.4, 1])
with col_m1:
    st.markdown("**✅ Misi**")
    for teks, ok in misi:
        st.markdown(f"{'✅' if ok else '⬜'} {teks}")
    st.progress(selesai_count / len(misi))
with col_m2:
    a, b, c = st.columns(3)
    a.metric("Query", st.session_state.n_query)
    b.metric("Clue", len(st.session_state.clues))
    c.metric("Salah tuduh", st.session_state.salah)

st.divider()

# ---------------------------------------------------------------------------
# DATASET + NOTEBOOK
# ---------------------------------------------------------------------------
col_data, col_tool = st.columns([1, 1.2])

with col_data:
    st.markdown("#### 🗂️ Dataset transaksi")
    tampil_df(data, height=380)
    st.caption("Kolom: `jam` (0-23), `kasir`, `total` (Rp), `hari`")

with col_tool:
    st.markdown("#### 🧑‍💻 Notebook investigasi")
    tahap = st.tabs(["Tahap 1: Pilih & Klik", "Tahap 2: Isi Bagian Kosong", "Tahap 3: Kode Bebas"])

    # ---------------- TAHAP 1 ----------------
    with tahap[0]:
        st.caption("Pilih kondisi untuk menyaring data. Kode Python terbentuk otomatis di bawahnya.")
        kolom = st.selectbox("Kolom", ["jam", "total", "kasir", "hari"], key="t1_kolom")
        operator = st.selectbox("Operator", ["<", ">", "==", "!="], key="t1_op")

        if kolom in ["jam", "total"]:
            nilai = st.number_input("Nilai", value=6, key="t1_nilai")
            nilai_repr = str(nilai)
        else:
            nilai = st.selectbox("Nilai", sorted(data[kolom].unique().tolist()), key="t1_nilai_kat")
            nilai_repr = f'"{nilai}"'

        kode1 = f'hasil = data[data["{kolom}"] {operator} {nilai_repr}]'
        st.code(kode1, language="python")
        if st.button("Jalankan", key="run1"):
            jalankan(kode1, 1, f"{kolom} {operator} {nilai_repr}")

    # ---------------- TAHAP 2 ----------------
    with tahap[1]:
        st.caption("Misi: cari transaksi bernominal di atas Rp500.000 yang terjadi sebelum jam 6 pagi.")
        st.code(
            'hasil = data[(data["total"] > ____) & (data["jam"] < ____)]',
            language="python",
        )
        c1, c2 = st.columns(2)
        blank_total = c1.text_input("Blank pertama (nominal)", placeholder="isi angka", key="t2_b1")
        blank_jam = c2.text_input("Blank kedua (jam)", placeholder="isi angka", key="t2_b2")

        if st.button("Jalankan", key="run2"):
            if not (blank_total.strip().isdigit() and blank_jam.strip().isdigit()):
                st.warning("Isi kedua bagian kosong dengan angka (tanpa titik atau huruf).")
            else:
                kode2 = (
                    f'hasil = data[(data["total"] > {int(blank_total)}) '
                    f'& (data["jam"] < {int(blank_jam)})]'
                )
                jalankan(kode2, 2, f"total > {int(blank_total)} dan jam < {int(blank_jam)}")

    # ---------------- TAHAP 3 ----------------
    with tahap[2]:
        st.caption(
            "Mode Detektif Senior: tulis kode Python sendiri. Variabel `data` (pandas DataFrame) sudah tersedia. "
            "Simpan hasil akhir ke variabel `hasil`."
        )
        default_code = (
            "# Contoh: total nominal per kasir pada transaksi dini hari\n"
            "dini_hari = data[data[\"jam\"] < 6]\n"
            "hasil = dini_hari.groupby(\"kasir\")[\"total\"].sum().sort_values(ascending=False)"
        )
        kode3 = st.text_area("Editor kode", value=default_code, height=160, key="t3_code")
        if st.button("Jalankan", key="run3"):
            jalankan(kode3, 3, "Analisis kode bebas")

    with st.expander("🧾 Kartu contekan"):
        st.code(
            'data[data["kolom"] > 5]                 # saring baris\n'
            'data[(kondisi1) & (kondisi2)]           # gabung dua kondisi\n'
            'data.sort_values("total", ascending=False)  # urutkan\n'
            'data.groupby("kasir")["total"].sum()    # total per kelompok\n'
            'data["total"].mean()                    # rata-rata',
            language="python",
        )

    # ---------------- HASIL TERAKHIR ----------------
    last = st.session_state.last
    if last:
        st.markdown("**Hasil terakhir**")
        st.caption(f"Analisis: {last['label']}")
        if isinstance(last["hasil"], (pd.DataFrame, pd.Series)):
            tampil_df(last["hasil"])
        else:
            st.write(last["hasil"])
        st.text_input(
            "Apa temuanmu dari hasil ini? (opsional, kalau kosong dipakai ringkasan otomatis)",
            key="catatan",
        )
        st.button("📌 Tempel sebagai clue", on_click=tempel_clue)

st.divider()

# ---------------------------------------------------------------------------
# PAPAN CLUE
# ---------------------------------------------------------------------------
st.markdown("#### 📌 Papan investigasi")
if st.session_state.clues:
    cols = st.columns(min(4, len(st.session_state.clues)))
    for i, c in enumerate(st.session_state.clues):
        with cols[i % len(cols)]:
            st.info(c)
else:
    st.caption("Belum ada clue. Jalankan analisis, lalu tempel temuan pentingnya ke papan.")

st.divider()

# ---------------------------------------------------------------------------
# TUDUHAN AKHIR
# ---------------------------------------------------------------------------
st.markdown("#### ⚖️ Ajukan tuduhan")

if st.session_state.selesai:
    skor = st.session_state.skor
    st.success(f"🎉 Kasus terpecahkan! Skor akhir: **{skor}/100** • {peringkat(skor)}")
    st.markdown(
        f"**Kesimpulan:** kasir **{PELAKU_BENAR}** melakukan **{JUMLAH_BENAR} transaksi** bernominal besar "
        f"di **dini hari**, saat toko seharusnya sepi. Transaksi besar milik kasir lain pada siang hari "
        "ternyata pesanan katering yang sah. Itulah *red herring* di kasus ini: nominal besar saja belum "
        "cukup jadi bukti, waktu kejadiannya juga harus ikut dilihat."
    )
    st.button("🔄 Main lagi", on_click=reset_game)
else:
    st.caption(
        f"Kamu butuh minimal {MIN_CLUE} clue di papan sebelum boleh menuduh. "
        "Tuduhan salah mengurangi 10 poin."
    )
    if st.session_state.feedback:
        tipe, pesan = st.session_state.feedback
        (st.error if tipe == "error" else st.warning)(pesan)

    with st.form("tuduhan"):
        pelaku = st.selectbox("Siapa pelakunya?", [PILIH] + KASIR)
        waktu = st.selectbox("Pada rentang waktu apa kejadiannya?", [PILIH] + WAKTU)
        jumlah = st.number_input("Berapa transaksi ilegal yang terjadi?", min_value=0, max_value=30, value=0, step=1)
        kirim = st.form_submit_button("⚖️ Ajukan tuduhan")

    if kirim:
        if pelaku == PILIH or waktu == PILIH:
            st.session_state.feedback = ("warning", "Pilih pelaku dan rentang waktu dulu sebelum menuduh.")
        elif len(st.session_state.clues) < MIN_CLUE:
            st.session_state.feedback = (
                "warning",
                f"Belum cukup bukti. Tempel minimal {MIN_CLUE} clue di papan investigasi dulu.",
            )
        else:
            cek = {
                "Pelaku": pelaku == PELAKU_BENAR,
                "Rentang waktu": waktu == WAKTU_BENAR,
                "Jumlah transaksi": jumlah == JUMLAH_BENAR,
            }
            if all(cek.values()):
                st.session_state.selesai = True
                st.session_state.skor = hitung_skor()
                st.session_state.feedback = None
            else:
                st.session_state.salah += 1
                baris = [f"{'✅' if ok else '❌'} {nama}" for nama, ok in cek.items()]
                st.session_state.feedback = (
                    "error",
                    "Tuduhanmu belum tepat (-10 poin). Periksa lagi datamu.\n\n" + "  \n".join(baris),
                )
        st.rerun()
