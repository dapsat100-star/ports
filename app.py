# -*- coding: utf-8 -*-
# DAP ATLAS — PORT SAR KPIs (MAVIPE SaaS) • versão com controles
# UI: painel MAVIPE, KPI Bar, overlays com toggles, export PNG/PDF
# Fonte: upload ou "fon.png" (SAR). Detecções simuladas por heurística leve.

import streamlit as st
from pathlib import Path
from datetime import datetime
from io import BytesIO
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps
from PIL import UnidentifiedImageError
import matplotlib.image as mpimg  # fallback para TIFF/PNGs complexos

# ========== Tema MAVIPE
BG      = (11, 18, 33)    # #0b1221
CARD    = (16, 24, 43)    # #10182b
BORDER  = (29, 41, 66)    # #1d2942
TEXT    = (230, 238, 252) # #E6EEFC
MUTED   = (159, 176, 201) # #9fb0c9
PRIMARY = (0, 227, 165)   # #00E3A5

GREEN   = (122, 222, 122) # vessels
RED     = (255, 90, 74)   # dark ships
CYAN    = (140, 200, 255) # piers
YELLOW  = (255, 210, 77)  # tanks

def font(bold=False, size=20):
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", size)
    except Exception:
        return ImageFont.load_default()

# ========== Página
st.set_page_config(page_title="DAP ATLAS — Port SAR KPIs (MAVIPE SaaS)", page_icon="🛰️", layout="wide")
st.markdown("""
<style>
html, body, .stApp { background:#0b1221; color:#E6EEFC; font-family:Inter, Segoe UI, Roboto, Arial, sans-serif; }
.block-container { padding-top: 0.75rem; max-width: 1500px; }
.card { background:#10182b; border:1px solid #1d2942; border-radius:12px; padding:12px; box-shadow:0 14px 32px rgba(0,0,0,.35); }
.kchip { background:#0d1526; border:1px solid #1d2942; border-radius:12px; padding:10px 14px; display:inline-block; margin-right:8px; }
</style>
""", unsafe_allow_html=True)

st.markdown("## 🛰️ DAP ATLAS — **Port SAR KPIs (SaaS)**")
st.caption("SAR como base • Overlays simulados • Painel MAVIPE • Controles • Export PNG/PDF")

# ========== Painel de controles
with st.expander("⚙️ Configurações & Entrada", expanded=True):
    c1, c2, c3, c4 = st.columns([1.2, 1.2, 1, 1])
    aoi = c1.text_input("AOI ID", value="AOI CN-LN-DAL-PORT-2025-01")
    title = c2.text_input("Título", value="DAP ATLAS — PORT SAR KPIs")
    subtitle = c3.text_input("Subtítulo", value="SAR-based observables • ISR / C2 Support")
    live_badge = c4.text_input("Badge", value="Live 24/7")

    c5, c6, c7 = st.columns(3)
    grid = c5.slider("Granularidade da grade (↓ = mais fino)", min_value=12, max_value=64, value=24, step=4)
    thr_bright = c6.slider("Limite de brilho (alvos metálicos)", min_value=100, max_value=255, value=210, step=5)
    thr_water = c7.slider("Limite de água (fundo escuro)", min_value=10, max_value=120, value=40, step=5)

    c8, c9, c10, c11 = st.columns(4)
    seed = c8.number_input("Seed (aleatoriedade)", min_value=0, max_value=9999, value=7)
    max_v = c9.slider("Máx. vessels em overlay", 20, 400, 160, 10)
    max_t = c10.slider("Máx. tanks em overlay", 20, 300, 140, 10)
    max_p = c11.slider("Máx. piers em overlay", 2, 40, 16, 1)

    st.write("### Fonte da imagem SAR")
    uploaded = st.file_uploader("Selecione a imagem SAR (PNG/JPG/TIF)", type=["png","jpg","jpeg","tif","tiff"], accept_multiple_files=False)

    o1, o2, o3, o4 = st.columns(4)
    show_vessels = o1.checkbox("Mostrar Vessels", value=True)
    show_dark    = o2.checkbox("Destacar Dark Ships", value=True)
    show_piers   = o3.checkbox("Mostrar Píeres", value=True)
    show_tanks   = o4.checkbox("Mostrar Tanques", value=True)

# ========== Loader robusto (upload ou "fon.png")
def load_sar_image(src):
    """Abre com Pillow ou fallback com matplotlib. Retorna PIL.Image em 'L'."""
    try:
        img = Image.open(src); img.load()
    except UnidentifiedImageError:
        try:
            arr = mpimg.imread(src if isinstance(src, (str, Path)) else src)
            if arr.ndim == 2:
                pass
            elif arr.ndim == 3:
                arr = arr[..., :3]
                arr = (0.2989*arr[...,0] + 0.5870*arr[...,1] + 0.1140*arr[...,2])
            if arr.dtype != np.uint8:
                arr = (255 * (arr / (arr.max() if arr.max() else 1))).astype(np.uint8)
            img = Image.fromarray(arr)
        except Exception as e2:
            raise UnidentifiedImageError(f"Não foi possível decodificar a imagem ({e2}).")
    if img.mode != "L":
        img = img.convert("L")
    return img

sar_path = Path("fon.png")
if uploaded is not None:
    try:
        SAR_RAW = load_sar_image(uploaded)
        st.caption(f"Imagem carregada: {uploaded.name}")
    except UnidentifiedImageError as e:
        st.error(f"Falha ao abrir a imagem enviada. {e}")
        SAR_RAW = None
else:
    if sar_path.exists():
        try:
            SAR_RAW = load_sar_image(str(sar_path))
            st.caption("Imagem carregada: fon.png (local)")
        except UnidentifiedImageError as e:
            st.error(f"Falha ao abrir `fon.png`. {e}")
            SAR_RAW = None
    else:
        SAR_RAW = None

# Placeholder se nada carregou
if SAR_RAW is None:
    SAR_RAW = Image.new("L", (1920, 1080), 40)
    dph = ImageDraw.Draw(SAR_RAW.convert("RGB"))
    dph.rectangle([24,24,1896,1056], outline=(90,110,140), width=2)
    dph.text((40,40), "Placeholder — imagem SAR não carregada", fill=(200,210,230), font=font(False, 24))

W0, H0 = SAR_RAW.size

# ========== Heurística de detecção (grid + brilho)
def simulate_detections(img: Image.Image, grid=24, thr_bright=210, thr_water=40, seed=7,
                        cap_v=160, cap_t=140, cap_p=16):
    np.random.seed(seed)
    a = np.array(img, dtype=np.uint8)
    h, w = a.shape
    gx = max(1, w // grid)
    gy = max(1, h // grid)

    vessels, tanks, piers = [], [], []

    for y in range(0, h, gy):
        for x in range(0, w, gx):
            tile = a[y:y+gy, x:x+gx]
            if tile.size == 0: continue
            mean = float(tile.mean())
            bright_mask = tile > thr_bright
            bright_ratio = float(bright_mask.mean()) if tile.size else 0.0

            # vessel = água escura + brilhos
            if mean < thr_water and bright_ratio > 0.01:
                vessels.append((x + gx//2, y + gy//2))

            # tanks = blocos claros + brilhos
            if mean > 90 and bright_ratio > 0.03:
                r = max(3, int(0.35 * min(gx, gy)))
                tanks.append((x + gx//2, y + gy//2, r))

    # piers: bandas horizontais brilhantes
    band_h = max(6, gy // 2)
    for y in range(0, h, band_h):
        band = a[y:y+band_h, :]
        if band.size == 0: continue
        if (band > thr_bright-10).mean() > 0.08 and (band.mean() > 70):
            piers.append((12, y + band_h//2 - 2, w-12, y + band_h//2 + 2))

    # caps
    if len(vessels) > cap_v:
        vessels = list(np.array(vessels)[np.random.choice(len(vessels), cap_v, replace=False)])
    if len(tanks) > cap_t:
        tanks = list(np.array(tanks)[np.random.choice(len(tanks), cap_t, replace=False)])
    if len(piers) > cap_p:
        piers = list(np.array(piers)[np.random.choice(len(piers), cap_p, replace=False)])

    return vessels, tanks, piers

vessels, tanks, piers = simulate_detections(
    SAR_RAW, grid=grid, thr_bright=thr_bright, thr_water=thr_water, seed=seed,
    cap_v=max_v, cap_t=max_t, cap_p=max_p
)

# dark ships (subconjunto de vessels)
rng = np.random.default_rng(seed)
dark_ratio = 0.18 + 0.12*rng.random()     # 18–30%
dark_n = int(len(vessels) * dark_ratio)
dark_idx = set(rng.choice(len(vessels), dark_n, replace=False)) if len(vessels) else set()

# KPIs
kpi_vessels   = len(vessels)
kpi_dark_pct  = round(100.0 * (dark_n / kpi_vessels), 1) if kpi_vessels else 0.0
kpi_pier_occ  = min(100, int(35 + 50*rng.random()))  # %
kpi_tanks     = len(tanks)

# ========== Render composto (mapa + painel) para preview/download
def render_composite():
    CAN_W, CAN_H = 1920, 1080
    LEFT_W = int(CAN_W*0.60)
    RIGHT_W = CAN_W - LEFT_W

    # Esquerda: SAR + overlays
    sar = SAR_RAW.convert("RGB")
    sar = ImageOps.fit(sar, (LEFT_W, CAN_H), Image.LANCZOS)
    drawL = ImageDraw.Draw(sar)

    sx = LEFT_W / W0
    sy = CAN_H / H0

    if show_piers:
        for (x0,y0,x1,y1) in piers:
            drawL.rectangle([x0*sx, y0*sy, x1*sx, y1*sy], outline=CYAN, width=2)

    if show_vessels or show_dark:
        for i,(cx,cy) in enumerate(vessels):
            r = 6
            is_dark = (i in dark_idx)
            if is_dark and show_dark:
                color = RED
            elif (not is_dark) and show_vessels:
                color = GREEN
            else:
                continue
            drawL.ellipse([cx*sx-r, cy*sy-r, cx*sx+r, cy*sy+r], outline=color, width=2)

    if show_tanks:
        for (cx,cy,r0) in tanks:
            r = int(r0 * (sx+sy)/2)
            drawL.ellipse([cx*sx-r, cy*sy-r, cx*sx+r, cy*sy+r], outline=YELLOW, width=2)

    # Direita: painel MAVIPE
    panel = Image.new("RGB", (RIGHT_W, CAN_H), BG)
    pdraw = ImageDraw.Draw(panel)

    # Header + Badge
    head = Image.new("RGB", (RIGHT_W-32, 110), CARD)
    hdraw = ImageDraw.Draw(head)
    # logo (opcional)
    logo_path = Path("dapatlas_whitebg.png")
    if logo_path.exists():
        lg = Image.open(logo_path).convert("RGBA")
        lg = ImageOps.contain(lg, (84,84), Image.LANCZOS)
        head.paste(lg, (16,13), lg)
    hdraw.text((120,18), title, fill=TEXT, font=font(True, 28))
    hdraw.text((120,56), subtitle, fill=MUTED, font=font(False, 20))
    hdraw.text((120,84), f"AOI {aoi}  •  Generated: {datetime.now().strftime('%d/%m/%Y %H:%M')}  •  {live_badge}",
               fill=MUTED, font=font(False, 16))
    panel.paste(head, (16,16))

    # KPI BAR (4 colunas)
    kpi_y = 136; kpi_h = 92; card_w = RIGHT_W - 32
    kpi_bar = Image.new("RGB", (card_w, kpi_h), (13,20,36))
    kdraw = ImageDraw.Draw(kpi_bar)
    kdraw.rectangle([0,0,card_w-1,kpi_h-1], outline=BORDER, width=2)

    cols = 4; col_w = card_w // cols
    labels = ["Vessels Detected", "Dark Ships (%)", "Pier Occupancy", "Tanks Identified"]
    values = [str(kpi_vessels), f"{kpi_dark_pct} %", f"{kpi_pier_occ} %", str(kpi_tanks)]

    for i in range(cols):
        x0 = i*col_w; x1 = (i+1)*col_w if i<cols-1 else card_w
        v = values[i]; fv = font(True, 28)
        w = kdraw.textlength(v, font=fv); h = fv.getbbox("Ag")[3]
        kdraw.text((x0 + (col_w-w)/2, 10), v, fill=TEXT, font=fv)
        l = labels[i]; fl = font(False, 15)
        w2 = kdraw.textlength(l, font=fl); h2 = fl.getbbox("Ag")[3]
        kdraw.text((x0 + (col_w-w2)/2, 52), l, fill=MUTED, font=fl)
        if i < cols-1:
            kdraw.line([(x1, 12), (x1, kpi_h-12)], fill="#22304f", width=1)

    panel.paste(kpi_bar, (16, kpi_y))
    grid_y = kpi_y + kpi_h + 16

    # Findings
    find_h = 170
    findings = Image.new("RGB", (card_w, find_h), CARD)
    fdrw = ImageDraw.Draw(findings)
    fdrw.rectangle([0,0,card_w-1,find_h-1], outline=BORDER)
    fdrw.text((12,8), "Key Findings", fill=TEXT, font=font(True, 20))
    bullets = [
        f"{kpi_vessels} vessels detected; {kpi_dark_pct}% estimated as dark (no AIS).",
        f"Pier occupancy ~ {kpi_pier_occ}% (bright linear structures along quays).",
        f"{kpi_tanks} circular structures consistent with storage tanks.",
        "Wake-like highlights suggest moving targets inside the basin.",
        f"Parameters → grid:{grid}, bright>{thr_bright}, water<{thr_water}, seed:{seed}.",
    ]
    yy = 38
    for b in bullets:
        fdrw.text((12, yy), "• " + b, fill=TEXT, font=font(False, 18)); yy += 24
    panel.paste(findings, (16, grid_y))
    grid_y += find_h + 12

    # Legenda
    leg_h = 120
    legend = Image.new("RGB", (card_w, leg_h), CARD)
    ldrw = ImageDraw.Draw(legend)
    ldrw.rectangle([0,0,card_w-1,leg_h-1], outline=BORDER)
    ldrw.text((12,8), "Legend", fill=TEXT, font=font(True, 20))
    ldrw.ellipse([14,42,14+16,42+16], outline=GREEN, width=3);   ldrw.text((36,42), "Vessel (generic)", fill=TEXT, font=font(False, 16))
    ldrw.ellipse([14,70,14+16,70+16], outline=RED, width=3);     ldrw.text((36,70), "Dark Ship (no AIS)", fill=TEXT, font=font(False, 16))
    ldrw.rectangle([260,46,260+34,46+10], outline=CYAN, width=2);ldrw.text((302,42), "Pier / Active quay", fill=TEXT, font=font(False, 16))
    ldrw.ellipse([520,42,520+18,42+18], outline=YELLOW, width=3);ldrw.text((546,42), "Storage tank", fill=TEXT, font=font(False, 16))
    panel.paste(legend, (16, grid_y))
    grid_y += leg_h + 12

    # Footer
    pdraw.text((16, CAN_H-30), "© 2025 MAVIPE Space Systems — DAP ATLAS", fill=MUTED, font=font(False, 16))

    # Compose final
    composite = Image.new("RGB", (CAN_W, CAN_H), BG)
    composite.paste(sar, (0,0))
    composite.paste(panel, (LEFT_W,0))

    png = BytesIO(); composite.save(png, "PNG"); png.seek(0)
    return composite, png

with st.spinner("Processando SAR e gerando painel..."):
    composite_img, composite_png = render_composite()

st.image(composite_img, caption="Preview (1920×1080) — SAR + Painel MAVIPE", use_column_width=True)

c1, c2 = st.columns(2)
with c1:
    st.download_button("📸 Download PNG (1920×1080)",
        data=composite_png.getvalue(), file_name="DAP_ATLAS_PORT_SAR_KPIs.png", mime="image/png")

with c2:
    try:
        from reportlab.lib.pagesizes import landscape, A4
        from reportlab.pdfgen import canvas as pdfcanvas
        from reportlab.lib.utils import ImageReader
        buf = BytesIO()
        c = pdfcanvas.Canvas(buf, pagesize=landscape(A4))
        Wp, Hp = landscape(A4)
        img_reader = ImageReader(BytesIO(composite_png.getvalue()))
        margin = 18
        c.drawImage(img_reader, margin, margin, width=Wp-2*margin, height=Hp-2*margin, mask='auto')
        c.showPage(); c.save(); buf.seek(0)
        st.download_button("📄 Download PDF (A4 landscape)",
            data=buf.getvalue(), file_name="DAP_ATLAS_PORT_SAR_KPIs.pdf", mime="application/pdf")
    except Exception as e:
        st.info(f"PDF opcional indisponível ({e}). Instale reportlab para habilitar.")
