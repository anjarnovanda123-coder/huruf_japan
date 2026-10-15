import streamlit as st
import streamlit.components.v1 as components
import random
import os
import urllib.request
from xml.dom import minidom

try:
    from svg.path import parse_path
except ImportError:
    st.error("Install `svg.path` dulu: tambahkan `svg.path` ke requirements.txt")
    st.stop()

# =========================================================
#  KONFIGURASI
# =========================================================
st.set_page_config(
    page_title="Kuis Gambar Hiragana & Katakana",
    page_icon="🎌",
    layout="wide"
)

# =========================================================
#  DATABASE HURUF
# =========================================================
HIRAGANA_BASIC = {
    "あ":"a","い":"i","う":"u","え":"e","お":"o",
    "か":"ka","き":"ki","く":"ku","け":"ke","こ":"ko",
    "さ":"sa","し":"shi","す":"su","せ":"se","そ":"so",
    "た":"ta","ち":"chi","つ":"tsu","て":"te","と":"to",
    "な":"na","に":"ni","ぬ":"nu","ね":"ne","の":"no",
    "は":"ha","ひ":"hi","ふ":"fu","へ":"he","ほ":"ho",
    "ま":"ma","み":"mi","む":"mu","め":"me","も":"mo",
    "や":"ya","ゆ":"yu","よ":"yo",
    "ら":"ra","り":"ri","る":"ru","れ":"re","ろ":"ro",
    "わ":"wa","を":"wo","ん":"n",
}
HIRAGANA_VARIAN = {
    "が":"ga","ぎ":"gi","ぐ":"gu","げ":"ge","ご":"go",
    "ざ":"za","じ":"ji","ず":"zu","ぜ":"ze","ぞ":"zo",
    "だ":"da","ぢ":"ji","づ":"zu","で":"de","ど":"do",
    "ば":"ba","び":"bi","ぶ":"bu","べ":"be","ぼ":"bo",
    "ぱ":"pa","ぴ":"pi","ぷ":"pu","ぺ":"pe","ぽ":"po",
}
HIRAGANA_KOMBINASI = {
    "きゃ":"kya","きゅ":"kyu","きょ":"kyo","しゃ":"sha","しゅ":"shu","しょ":"sho",
    "ちゃ":"cha","ちゅ":"chu","ちょ":"cho","にゃ":"nya","にゅ":"nyu","にょ":"nyo",
    "ひゃ":"hya","ひゅ":"hyu","ひょ":"hyo","みゃ":"mya","みゅ":"myu","みょ":"myo",
    "りゃ":"rya","りゅ":"ryu","りょ":"ryo","ぎゃ":"gya","ぎゅ":"gyu","ぎょ":"gyo",
    "じゃ":"ja","じゅ":"ju","じょ":"jo","びゃ":"bya","びゅ":"byu","びょ":"byo",
    "ぴゃ":"pya","ぴゅ":"pyu","ぴょ":"pyo",
}
KATAKANA_BASIC = {
    "ア":"a","イ":"i","ウ":"u","エ":"e","オ":"o",
    "カ":"ka","キ":"ki","ク":"ku","ケ":"ke","コ":"ko",
    "サ":"sa","シ":"shi","ス":"su","セ":"se","ソ":"so",
    "タ":"ta","チ":"chi","ツ":"tsu","テ":"te","ト":"to",
    "ナ":"na","ニ":"ni","ヌ":"nu","ネ":"ne","ノ":"no",
    "ハ":"ha","ヒ":"hi","フ":"fu","ヘ":"he","ホ":"ho",
    "マ":"ma","ミ":"mi","ム":"mu","メ":"me","モ":"mo",
    "ヤ":"ya","ユ":"yu","ヨ":"yo",
    "ラ":"ra","リ":"ri","ル":"ru","レ":"re","ロ":"ro",
    "ワ":"wa","ヲ":"wo","ン":"n",
}
KATAKANA_VARIAN = {
    "ガ":"ga","ギ":"gi","グ":"gu","ゲ":"ge","ゴ":"go",
    "ザ":"za","ジ":"ji","ズ":"zu","ゼ":"ze","ゾ":"zo",
    "ダ":"da","ヂ":"ji","ヅ":"zu","デ":"de","ド":"do",
    "バ":"ba","ビ":"bi","ブ":"bu","ベ":"be","ボ":"bo",
    "パ":"pa","ピ":"pi","プ":"pu","ペ":"pe","ポ":"po",
}
KATAKANA_KOMBINASI = {
    "キャ":"kya","キュ":"kyu","キョ":"kyo","シャ":"sha","シュ":"shu","ショ":"sho",
    "チャ":"cha","チュ":"chu","チョ":"cho","ニャ":"nya","ニュ":"nyu","ニョ":"nyo",
    "ヒャ":"hya","ヒュ":"hyu","ヒョ":"hyo","ミャ":"mya","ミュ":"myu","ミョ":"myo",
    "リャ":"rya","リュ":"ryu","リョ":"ryo","ギャ":"gya","ギュ":"gyu","ギョ":"gyo",
    "ジャ":"ja","ジュ":"ju","ジョ":"jo","ビャ":"bya","ビュ":"byu","ビョ":"byo",
    "ピャ":"pya","ピュ":"pyu","ピョ":"pyo",
}

# =========================================================
#  FUNGSI BANTU
# =========================================================
@st.cache_data(show_spinner=False)
def dapatkan_kanjivg_paths(char):
    """Ambil path data dari KanjiVG untuk SATU karakter."""
    if len(char) != 1:
        return []
    codepoint = f"{ord(char):05x}"
    url = f"https://cdn.jsdelivr.net/gh/KanjiVG/kanjivg@master/kanji/{codepoint}.svg"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            svg_data = resp.read().decode("utf-8")
        doc = minidom.parseString(svg_data)
        path_nodes = doc.getElementsByTagName('path')
        paths = []
        for node in path_nodes:
            d = node.getAttribute('d')
            if d:
                paths.append(d)
        doc.unlink()
        return paths
    except Exception:
        return []


def dapatkan_kanjivg_paths_multi(teks):
    """Ambil path KanjiVG untuk teks 1 atau 2+ karakter."""
    hasil = []
    n = len(teks)
    for i, ch in enumerate(teks):
        paths = dapatkan_kanjivg_paths(ch)
        offset_x = 0.0 if n == 1 else i * 75.0
        hasil.append((ch, paths, offset_x))
    return hasil


def ambil_pool(aksara, level):
    pool = {}
    if aksara in ("Hiragana", "Campuran"):
        if level in ("Basic", "Semua"):
            pool.update(HIRAGANA_BASIC)
        if level in ("Varian", "Semua"):
            pool.update(HIRAGANA_VARIAN)
        if level in ("Kombinasi", "Semua"):
            pool.update(HIRAGANA_KOMBINASI)
    if aksara in ("Katakana", "Campuran"):
        if level in ("Basic", "Semua"):
            pool.update(KATAKANA_BASIC)
        if level in ("Varian", "Semua"):
            pool.update(KATAKANA_VARIAN)
        if level in ("Kombinasi", "Semua"):
            pool.update(KATAKANA_KOMBINASI)
    if not pool:
        pool = HIRAGANA_BASIC
    return pool


def build_svg_html(huruf, tampilkan_urutan=False):
    """Bangun HTML SVG dari KanjiVG path.
    Kalau tampilkan_urutan=True, gambar juga goresan berwarna + nomor urut."""
    kandidat = dapatkan_kanjivg_paths_multi(huruf)
    kandidat_valid = [(ch, ps, ox) for (ch, ps, ox) in kandidat if ps]

    if not kandidat_valid:
        # Fallback: pakai font
        return f"""
        <div style="width:100%;height:100%;display:flex;align-items:center;
                    justify-content:center;background:white;
                    font-size:min(60vh,60vw);font-family:'Noto Sans CJK JP',
                    'Yu Gothic','Meiryo',sans-serif;color:black;">{huruf}</div>
        """

    # Hitung bounding box
    min_x, min_y = 999, 999
    max_x, max_y = -999, -999
    for (ch, paths, offset_x) in kandidat_valid:
        for path_str in paths:
            try:
                path = parse_path(path_str)
                for seg in path:
                    for pt in (seg.start, seg.end):
                        px = pt.real + offset_x
                        py = pt.imag
                        if px < min_x: min_x = px
                        if py < min_y: min_y = py
                        if px > max_x: max_x = px
                        if py > max_y: max_y = py
            except Exception:
                pass

    if min_x >= max_x or min_y >= max_y:
        min_x, min_y, max_x, max_y = 0, 0, 109, 109

    bbox_w = max_x - min_x
    bbox_h = max_y - min_y
    margin = 0.10
    skala = min(100 * (1 - 2 * margin) / bbox_w,
                100 * (1 - 2 * margin) / bbox_h)
    offset_canvas_x = (100 - bbox_w * skala) / 2 - min_x * skala
    offset_canvas_y = (100 - bbox_h * skala) / 2 - min_y * skala

    def to_svg(px, py):
        return offset_canvas_x + px * skala, offset_canvas_y + py * skala

    # Lebar garis
    if tampilkan_urutan:
        lebar_huruf = max(1.5, 1.2 * skala)
        lebar_goresan = max(0.4, 0.35 * skala)
    else:
        lebar_huruf = max(0.8, 0.7 * skala)
        lebar_goresan = 0

    # Konversi path ke polyline points
    def path_to_points(path_str, offset_x):
        points = []
        try:
            path = parse_path(path_str)
            for seg in path:
                start = (seg.start.real + offset_x, seg.start.imag)
                if not points or points[-1] != start:
                    points.append(start)
                try:
                    seg_len = seg.length(error=1e-3)
                except Exception:
                    seg_len = 0
                n = max(6, int(seg_len / 1.5))
                for j in range(1, n + 1):
                    t = j / n
                    pt = seg.point(t)
                    points.append((pt.real + offset_x, pt.imag))
        except Exception:
            return []
        return points

    svg_parts = []
    svg_parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 100 100" '
        f'style="width:100%;height:100%;background:white;'
        f'border-radius:8px;">'
    )

    # Huruf hitam
    for (ch, paths, offset_x) in kandidat_valid:
        for path_str in paths:
            pts = path_to_points(path_str, offset_x)
            if len(pts) < 2:
                continue
            pts_svg = " ".join(
                f"{to_svg(px, py)[0]:.2f},{to_svg(px, py)[1]:.2f}"
                for (px, py) in pts
            )
            svg_parts.append(
                f'<polyline points="{pts_svg}" '
                f'fill="none" stroke="black" '
                f'stroke-width="{lebar_huruf:.2f}" '
                f'stroke-linecap="round" stroke-linejoin="round"/>'
            )

    # Overlay goresan warna + nomor
    if tampilkan_urutan:
        palet = ["#1e66f5", "#e64553", "#40a02b", "#df8e1d",
                 "#8839ef", "#04a5e5", "#fe640b", "#d20f39"]
        idx_warna = 0
        nomor = 1
        for (ch, paths, offset_x) in kandidat_valid:
            for path_str in paths:
                pts = path_to_points(path_str, offset_x)
                if len(pts) < 2:
                    continue
                pts_svg = " ".join(
                    f"{to_svg(px, py)[0]:.2f},{to_svg(px, py)[1]:.2f}"
                    for (px, py) in pts
                )
                warna = palet[idx_warna % len(palet)]
                idx_warna += 1
                svg_parts.append(
                    f'<polyline points="{pts_svg}" '
                    f'fill="none" stroke="{warna}" '
                    f'stroke-width="{lebar_goresan:.2f}" '
                    f'stroke-linecap="round" stroke-linejoin="round" '
                    f'opacity="0.85"/>'
                )
                # Nomor + panah
                try:
                    path = parse_path(path_str)
                    start = path[0].start
                    sx, sy = to_svg(start.real + offset_x, start.imag)
                    seg_awal = path[0]
                    if hasattr(seg_awal, 'point'):
                        p0 = seg_awal.point(0.0)
                        p1 = seg_awal.point(min(0.3, 1.0))
                        dx = p1.real - p0.real
                        dy = p1.imag - p0.imag
                        panjang = max(0.001, (dx**2 + dy**2) ** 0.5)
                        dx /= panjang
                        dy /= panjang
                    else:
                        dx, dy = 1, 0
                    r_svg = 3.2
                    ex = sx + dx * (r_svg * 2.2)
                    ey = sy + dy * (r_svg * 2.2)
                    svg_parts.append(
                        f'<line x1="{sx:.2f}" y1="{sy:.2f}" '
                        f'x2="{ex:.2f}" y2="{ey:.2f}" '
                        f'stroke="#1e1e2e" stroke-width="0.6" '
                        f'marker-end="url(#arrowhead)"/>'
                    )
                    svg_parts.append(
                        f'<circle cx="{sx:.2f}" cy="{sy:.2f}" r="{r_svg}" '
                        f'fill="#89b4fa" stroke="#1e66f5" stroke-width="0.5"/>'
                    )
                    svg_parts.append(
                        f'<text x="{sx:.2f}" y="{sy + 1.1:.2f}" '
                        f'font-size="4" font-weight="bold" '
                        f'text-anchor="middle" fill="#1e1e2e">{nomor}</text>'
                    )
                    nomor += 1
                except Exception:
                    pass

    # Definisi marker arrow
    svg_parts.append(
        '<defs><marker id="arrowhead" markerWidth="6" markerHeight="6" '
        'refX="4" refY="3" orient="auto">'
        '<polygon points="0 0, 6 3, 0 6" fill="#1e1e2e"/></marker></defs>'
    )
    svg_parts.append("</svg>")

    return "".join(svg_parts)


# =========================================================
#  SESSION STATE
# =========================================================
def init_state():
    defaults = {
        "app_mode": "kuis",
        "aksara": "Hiragana",
        "level": "Basic",
        "queue": [],
        "history": [],
        "huruf_benar": None,
        "romaji_soal": None,
        "total_keluar": 0,
        "jawaban_tersembunyi": True,
        "gambar_tersembunyi": False,
        "tampilkan_urutan": True,
        "pool_sig": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_state()


def isi_queue(pool):
    items = list(pool.items())
    hist = st.session_state.history
    if hist and len(items) > 3:
        baru = [x for x in items if x not in hist]
        lama = [x for x in items if x in hist]
        random.shuffle(baru)
        random.shuffle(lama)
        items = baru + lama
    else:
        random.shuffle(items)
    st.session_state.queue = items
    st.session_state.pool_sig = (st.session_state.aksara,
                                 st.session_state.level)


def soal_baru():
    pool = ambil_pool(st.session_state.aksara, st.session_state.level)
    sig = (st.session_state.aksara, st.session_state.level)
    if st.session_state.pool_sig != sig:
        st.session_state.history = []
        isi_queue(pool)
    if not st.session_state.queue:
        isi_queue(pool)
    h, r = st.session_state.queue.pop(0)
    st.session_state.huruf_benar = h
    st.session_state.romaji_soal = r
    st.session_state.total_keluar += 1
    hist = st.session_state.history + [(h, r)]
    st.session_state.history = hist[-3:]
    st.session_state.jawaban_tersembunyi = (
        st.session_state.app_mode == "belajar"
    )


# =========================================================
#  SIDEBAR
# =========================================================
with st.sidebar:
    st.header("⚙️ Pengaturan")

    st.session_state.app_mode = st.radio(
        "Mode:",
        ["kuis", "belajar"],
        index=0 if st.session_state.app_mode == "kuis" else 1,
        horizontal=True
    )

    aksara_baru = st.selectbox(
        "Aksara:",
        ["Hiragana", "Katakana", "Campuran"],
        index=["Hiragana", "Katakana", "Campuran"].index(
            st.session_state.aksara)
    )
    level_baru = st.selectbox(
        "Level:",
        ["Basic", "Varian", "Kombinasi", "Semua"],
        index=["Basic", "Varian", "Kombinasi", "Semua"].index(
            st.session_state.level)
    )

    if aksara_baru != st.session_state.aksara or level_baru != st.session_state.level:
        st.session_state.aksara = aksara_baru
        st.session_state.level = level_baru
        st.session_state.pool_sig = None
        st.session_state.history = []
        soal_baru()

    if st.button("🔀 Acak Ulang", use_container_width=True):
        pool = ambil_pool(st.session_state.aksara, st.session_state.level)
        st.session_state.history = []
        isi_queue(pool)
        soal_baru()
        st.rerun()

    if st.session_state.app_mode == "belajar":
        st.session_state.tampilkan_urutan = st.checkbox(
            "🔢 Tampilkan Urutan Goresan",
            value=st.session_state.tampilkan_urutan
        )

    st.divider()
    st.caption(f"🎲 Soal ke-{st.session_state.total_keluar + 1}")
    st.caption(f"📦 Sisa di antrian: {len(st.session_state.queue)}")
    st.caption(f"📚 Pool: {len(ambil_pool(st.session_state.aksara, st.session_state.level))} huruf")


# =========================================================
#  MAIN AREA
# =========================================================
st.markdown(
    "<h1 style='text-align:center; color:#C62828;'>"
    "🎌 Kuis Menggambar Hiragana & Katakana 🎌</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<p style='text-align:center; color:#7f849c; font-style:italic;'>"
    "(Goresan akurat dari data KanjiVG — CC BY-SA 3.0)</p>",
    unsafe_allow_html=True
)

if st.session_state.huruf_benar is None:
    soal_baru()

huruf = st.session_state.huruf_benar
romaji = st.session_state.romaji_soal
mode = st.session_state.app_mode

# =========================================================
#  SOAL
# =========================================================
st.markdown(
    "<p style='text-align:center; font-weight:bold; color:#F9A825;'>"
    "📢 GAMBAR HURUF INI:</p>",
    unsafe_allow_html=True
)

if mode == "belajar" and st.session_state.jawaban_tersembunyi:
    st.markdown(
        "<h2 style='text-align:center; font-size:3rem; color:#888;'>"
        "\"?\"</h2>",
        unsafe_allow_html=True
    )
else:
    st.markdown(
        f"<h2 style='text-align:center; font-size:3rem; color:#F5C2E7;'>"
        f"\"{romaji}\"</h2>",
        unsafe_allow_html=True
    )

col_tengah1, col_tengah2, col_tengah3 = st.columns([1, 2, 1])
with col_tengah2:
    if mode == "belajar":
        if st.button("👁 Lihat Romaji" if st.session_state.jawaban_tersembunyi
                     else "🙈 Sembunyikan Romaji",
                     use_container_width=True):
            st.session_state.jawaban_tersembunyi = not st.session_state.jawaban_tersembunyi
            st.rerun()

st.divider()

# =========================================================
#  KANVAS: CONTOH (kiri) & GAMBAR USER (kanan)
# =========================================================
col_kiri, col_kanan = st.columns(2)

with col_kiri:
    st.markdown(
        "<p style='text-align:center; font-weight:bold; color:#F9A825;'>"
        "👁 CONTOH HURUF</p>",
        unsafe_allow_html=True
    )

    tampil_urutan = (
        mode == "belajar" and st.session_state.tampilkan_urutan
    )

    if mode == "belajar" and st.session_state.gambar_tersembunyi:
        st.markdown(
            "<div style='background:white; height:400px; display:flex; "
            "align-items:center; justify-content:center; border-radius:8px; "
            "border:3px solid #cba6f7;'>"
            "<span style='font-size:6rem; color:#ddd;'>?</span></div>",
            unsafe_allow_html=True
        )
    else:
        svg_html = build_svg_html(huruf, tampilkan_urutan=tampil_urutan)
        st.markdown(
            f"<div style='background:white; height:400px; "
            f"display:flex; align-items:center; justify-content:center; "
            f"border-radius:8px; border:3px solid #f5c2e7;'>"
            f"<div style='width:100%; height:100%; padding:10px; "
            f"box-sizing:border-box;'>{svg_html}</div></div>",
            unsafe_allow_html=True
        )

    if mode == "belajar":
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🖼 Lihat Gambar" if st.session_state.gambar_tersembunyi
                         else "🙈 Sembunyikan Gambar",
                         use_container_width=True):
                st.session_state.gambar_tersembunyi = not st.session_state.gambar_tersembunyi
                st.rerun()
        with col_b:
            if st.button("🔢 Urutan" if not st.session_state.tampilkan_urutan
                         else "🔢 Sembunyikan Urutan",
                         use_container_width=True):
                st.session_state.tampilkan_urutan = not st.session_state.tampilkan_urutan
                st.rerun()

with col_kanan:
    st.markdown(
        "<p style='text-align:center; font-weight:bold; color:#F9A825;'>"
        "✍️ GAMBAR DI SINI</p>",
        unsafe_allow_html=True
    )

    # Kanvas HTML5 untuk menggambar
    canvas_html = """
    <div style="position:relative; width:100%; height:400px;">
        <canvas id="drawingCanvas"
                style="width:100%; height:100%; background:white;
                       border-radius:8px; border:3px solid #89b4fa;
                       cursor:crosshair; touch-action:none;"></canvas>
        <div style="position:absolute; top:8px; right:8px; display:flex;
                    gap:6px; align-items:center; background:rgba(255,255,255,0.9);
                    padding:6px 10px; border-radius:8px;">
            <label style="font-size:12px; font-weight:bold;">Warna:</label>
            <input type="color" id="colorPicker" value="#000000"
                   style="width:35px; height:28px; border:none; cursor:pointer;">
            <label style="font-size:12px; font-weight:bold; margin-left:8px;">
                Ukuran:</label>
            <input type="range" id="sizeSlider" min="1" max="30" value="6"
                   style="width:80px;">
            <span id="sizeLabel" style="font-size:12px; width:25px;">6</span>
        </div>
        <div style="position:absolute; bottom:8px; right:8px; display:flex; gap:6px;">
            <button id="undoBtn" style="padding:6px 12px; border:none;
                    background:#f9e2af; border-radius:6px; cursor:pointer;
                    font-weight:bold;">↶ Undo</button>
            <button id="clearBtn" style="padding:6px 12px; border:none;
                    background:#f38ba8; border-radius:6px; cursor:pointer;
                    font-weight:bold;">🗑 Hapus</button>
        </div>
    </div>

    <script>
    (function() {
        const canvas = document.getElementById('drawingCanvas');
        const ctx = canvas.getContext('2d');
        const colorPicker = document.getElementById('colorPicker');
        const sizeSlider = document.getElementById('sizeSlider');
        const sizeLabel = document.getElementById('sizeLabel');
        let drawing = false;
        let lastX = 0, lastY = 0;
        let undoStack = [];
        let currentPath = [];

        function resizeCanvas() {
            const rect = canvas.getBoundingClientRect();
            const savedImage = canvas.width > 0
                ? ctx.getImageData(0, 0, canvas.width, canvas.height)
                : null;
            canvas.width = rect.width;
            canvas.height = rect.height;
            ctx.lineCap = 'round';
            ctx.lineJoin = 'round';
            if (savedImage) {
                ctx.putImageData(savedImage, 0, 0);
            }
        }

        function saveState() {
            undoStack.push(canvas.toDataURL());
            if (undoStack.length > 50) undoStack.shift();
        }

        canvas.addEventListener('mousedown', e => {
            drawing = true;
            saveState();
            const rect = canvas.getBoundingClientRect();
            lastX = e.clientX - rect.left;
            lastY = e.clientY - rect.top;
        });

        canvas.addEventListener('mousemove', e => {
            if (!drawing) return;
            const rect = canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            ctx.strokeStyle = colorPicker.value;
            ctx.lineWidth = parseInt(sizeSlider.value);
            ctx.beginPath();
            ctx.moveTo(lastX, lastY);
            ctx.lineTo(x, y);
            ctx.stroke();
            lastX = x;
            lastY = y;
        });

        canvas.addEventListener('mouseup', () => drawing = false);
        canvas.addEventListener('mouseleave', () => drawing = false);

        canvas.addEventListener('touchstart', e => {
            e.preventDefault();
            const touch = e.touches[0];
            const rect = canvas.getBoundingClientRect();
            drawing = true;
            saveState();
            lastX = touch.clientX - rect.left;
            lastY = touch.clientY - rect.top;
        });

        canvas.addEventListener('touchmove', e => {
            e.preventDefault();
            if (!drawing) return;
            const touch = e.touches[0];
            const rect = canvas.getBoundingClientRect();
            const x = touch.clientX - rect.left;
            const y = touch.clientY - rect.top;
            ctx.strokeStyle = colorPicker.value;
            ctx.lineWidth = parseInt(sizeSlider.value);
            ctx.beginPath();
            ctx.moveTo(lastX, lastY);
            ctx.lineTo(x, y);
            ctx.stroke();
            lastX = x;
            lastY = y;
        });

        canvas.addEventListener('touchend', () => drawing = false);

        sizeSlider.addEventListener('input', () => {
            sizeLabel.textContent = sizeSlider.value;
        });

        document.getElementById('undoBtn').addEventListener('click', () => {
            if (undoStack.length > 0) {
                const dataURL = undoStack.pop();
                const img = new Image();
                img.onload = () => {
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                    ctx.drawImage(img, 0, 0);
                };
                img.src = dataURL;
            }
        });

        document.getElementById('clearBtn').addEventListener('click', () => {
            saveState();
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        });

        window.addEventListener('resize', resizeCanvas);
        setTimeout(resizeCanvas, 100);
    })();
    </script>
    """
    components.html(canvas_html, height=440)

st.divider()

# Tombol Lanjut
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("⏭ LANJUT KE SOAL BERIKUTNYA",
                 type="primary", use_container_width=True):
        soal_baru()
        st.rerun()
