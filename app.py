# -*- coding: utf-8 -*-
# DAP ATLAS — PORT SAR KPIs (MAVIPE SaaS) • v3
# Layout: SAR à esquerda + painel à direita com KPIs e 3 gráficos.
# Correções: cores do matplotlib em 0–1; carregamento robusto de imagem; export PNG/PDF.

import streamlit as st
from pathlib import Path
from datetime import datetime, timedelta
from io import BytesIO
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps
from PIL import UnidentifiedImageError
import matplotlib.image as mpimg

# ----------------------------- Tema MAVIPE
BG      = (11, 18, 33)    # #0b1221
CARD    = (16, 24, 43)    # #10182b
BORDER  = (29, 41, 66)    # #1d2942
TEXT    = (230, 238, 252) # #E6EEFC
MUTED   = (159, 176, 201) # #9fb0c9
PRIMARY = (0, 227, 165)   # #00E3A5
GREEN   = (122,222,122)
RED     = (255, 90, 74)
CYAN    = (140,200,255)
YELLOW  = (255,210,77)

def font(bold=False, size=20):
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", size)
    except Exception:
        return ImageFont.load_default()

st.set_page_config(page_title="DAP ATLAS — Port SAR KPIs (MAVIPE)", page_icon="🛰️", layout="wide")
st.markdown("""
<style>
html, body, .stApp { background:#0b1221; color:#E6EEFC; font-family:Inter, Segoe UI, Roboto, Arial, sans-serif; }
.block-container { padding-top: .6rem; max-width: 1500px; }
</style>
""", unsafe_allow_html=True)

st.markdown("## 🛰️ DAP ATLAS — **PORT SAR KPIs**")
st.caption("SAR como base • Overlays simulados • Painel MAVIPE • Export PNG/PDF")

# ----------------------------- Controles
with st.expander("⚙️ Configurações", expanded=True):
    c1,c2,c3,c4 = st.columns([1.4,1.4,1,1])
    AOI = c1.text_input("AOI ID", "AOI CN-LN-DAL-PORT-2025-01")
    TITLE = c2.text_input("Título", "DAP ATLAS — PORT SAR KPIs")
    SUBTITLE = c3.text_input("Subtítulo", "SAR-based observables • ISR / C2 Support")
    BADGE = c4.text_input("Badge", "Live 24/7")

    c5,c6,c7 = st.columns(3)
    GRID = c5.slider("Granularidade (↓ = mais fino)", 12, 64, 24, 4)
    THR_BRIGHT = c6.slider("Brilho (metálico)", 100, 255, 210, 5)
    THR_WATER  = c7.slider("Água (escuro)", 10, 120, 40, 5)

    c8,c9,c10,c11 = st.columns(4)
    SEED = c8.number_input("Seed", 0, 9999, 7)
    CAP_V = c9.slider("Máx. vessels", 20, 400, 160, 10)
    CAP_T = c10.slider("Máx. tanks", 20, 300, 140, 10)
    CAP_P = c11.slider("Máx. píeres", 2, 40, 16, 1)

    c12,c13,c14,c15 = st.columns(4)
    SHOW_V = c12.checkbox("Mostrar Vessels", True)
    SHOW_D = c13.checkbox("Destacar Dark Ships", True)
    SHOW_P = c14.checkbox("Mostrar Píeres", True)
    SHOW_T = c15.checkbox("Mostrar Tanques", True)

    DEMO = st.checkbox("Travar KPIs (160 / 25% / 79% / 14)", True)

    st.write("### Fonte SAR")
    uploaded = st.file_uploader("Imagem SAR (PNG/JPG/TIFF)", type=["png","jpg","jpeg","tif","tiff"])

# ----------------------------- Loader de imagem robusto
def load_sar(src):
    try:
        img = Image.open(src); img.load()
    except UnidentifiedImageError:
        arr = mpimg.imread(src if isinstance(src,(str,Path)) else src)
        if arr.ndim == 3:
            arr = (0.2989*arr[...,0] + 0.5870*arr[...,1] + 0.1140*arr[...,2])
        if arr.dtype != np.uint8:
            arr = (255*(arr/(arr.max() if arr.max() else 1))).astype(np.uint8)
        img = Image.fromarray(arr)
    return img.convert("L")

sar_path = Path("fon.png")
if uploaded is not None:
    SAR_RAW = load_sar(uploaded)
    st.caption(f"Imagem carregada: {uploaded.name}")
elif sar_path.exists():
    SAR_RAW = load_sar(str(sar_path))
    st.caption("Imagem carregada: fon.png (local)")
else:
    SAR_RAW = Image.new("L", (1920,1080), 40)
    d = ImageDraw.Draw(SAR_RAW.convert("RGB"))
    d.text((40,40), "Placeholder — envie uma imagem SAR", fill=(210,220,235), font=font(False,22))

W0,H0 = SAR_RAW.size

# ----------------------------- Pseudo-detector (heurística leve)
def detect(img, grid, thr_bright, thr_water, seed, cap_v, cap_t, cap_p):
    np.random.seed(seed)
    a = np.array(img, dtype=np.uint8)
    h,w = a.shape
    gx = max(1, w//grid); gy = max(1, h//grid)
    vessels,tanks,piers = [],[],[]

    for y in range(0,h,gy):
        for x in range(0,w,gx):
            tile = a[y:y+gy, x:x+gx]
            if tile.size == 0: continue
            mean = float(tile.mean())
            bright = (tile > thr_bright).mean()
            if mean < thr_water and bright > 0.01:
                vessels.append((x+gx//2, y+gy//2))
            if mean > 90 and bright > 0.03:
                r = max(3,int(0.35*min(gx,gy))); tanks.append((x+gx//2, y+gy//2, r))

    band_h = max(6, gy//2)
    for y in range(0,h,band_h):
        band = a[y:y+band_h,:]
        if band.size == 0: continue
        if (band > thr_bright-10).mean() > 0.08 and (band.mean() > 70):
            piers.append((12, y+band_h//2-2, w-12, y+band_h//2+2))

    if len(vessels) > cap_v: vessels = list(np.array(vessels)[np.random.choice(len(vessels), cap_v, False)])
    if len(tanks)   > cap_t: tanks   = list(np.array(tanks  )[np.random.choice(len(tanks),   cap_t, False)])
    if len(piers)   > cap_p: piers   = list(np.array(piers  )[np.random.choice(len(piers),   cap_p, False)])
    return vessels,tanks,piers

vessels,tanks,piers = detect(SAR_RAW, GRID, THR_BRIGHT, THR_WATER, SEED, CAP_V, CAP_T, CAP_P)

# subset dark
rng = np.random.default_rng(SEED)
dark_ratio = 0.18 + 0.12*rng.random()
dark_n = int(len(vessels)*dark_ratio)
dark_idx = set(rng.choice(len(vessels), dark_n, replace=False)) if len(vessels) else set()

# KPIs dinâmicos ou travados (demo)
kpi_vessels = len(vessels)
kpi_dark_pct = round(100.0*(dark_n/max(1,kpi_vessels)),1)
kpi_pier_occ = min(100, int(35+50*rng.random()))
kpi_tanks = len(tanks)
if DEMO:
    kpi_vessels = 160
    kpi_dark_pct = 25.0
    kpi_pier_occ = 79
    kpi_tanks = 14

# ----------------------------- Séries simuladas (para gráficos)
def simulate_series(n=14, seed=101):
    rng = np.random.default_rng(seed)
    dates = [ (datetime.utcnow()-timedelta(days=(n-1-i))).strftime("%b %d") for i in range(n) ]
    oil  = np.clip(18 + np.cumsum(rng.normal(0,0.4,size=n)), 15, 24)
    wait = np.clip(12 + rng.normal(0,7,size=n), 6, 40)           # horas
    ships = rng.integers(12, 26, size=n)
    noais = (ships * rng.uniform(0.05, 0.18, size=n)).round().astype(int)
    return dates, oil, wait, ships, noais

dates, oil_series, wait_series, ships_series, noais_series = simulate_series(n=14, seed=SEED+21)

# ----------------------------- Plot helper (cores 0–1 p/ matplotlib)
def plot_to_img(title, xlab, ylab, series_list, size, legend=False):
    import matplotlib.pyplot as plt
    # cores 0–1
    TEXT_MPL   = tuple([c/255 for c in TEXT])
    MUTED_MPL  = tuple([c/255 for c in MUTED])
    CARD_MPL   = tuple([c/255 for c in CARD])
    BG_MPL     = tuple([c/255 for c in BG])
    BORDER_MPL = tuple([c/255 for c in BORDER])

    plt.style.use("default")
    fig = plt.figure(figsize=(size[0]/100, size[1]/100), dpi=100, facecolor=BG_MPL)
    ax = plt.axes(facecolor=CARD_MPL)

    x = np.arange(len(dates))
    for s in series_list:
        y = s["y"]
        if s.get("type","line")=="bar":
            ax.bar(x, y, alpha=.88, label=s.get("label"))
        else:
            ax.plot(x, y, linewidth=2.2, marker="o", label=s.get("label"))

    ax.set_title(title, color=TEXT_MPL, fontsize=11, pad=8, weight="bold")
    ax.set_xlabel(xlab, color=MUTED_MPL, fontsize=9)
    ax.set_ylabel(ylab, color=MUTED_MPL, fontsize=9)
    ax.set_xticks(x); ax.set_xticklabels(dates, fontsize=8, color=TEXT_MPL)
    ax.tick_params(axis='y', colors=TEXT_MPL, labelsize=8)

    for sp in ax.spines.values():
        sp.set_color(BORDER_MPL)

    ax.grid(color=(0.18, 0.24, 0.38), alpha=.35, linewidth=.8)

    if legend:
        leg = ax.legend(loc="upper left", fontsize=8, frameon=True)
        leg.get_frame().set_facecolor(CARD_MPL)
        leg.get_frame().set_edgecolor(BORDER_MPL)

    buf = BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png", dpi=100, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig); buf.seek(0)
    return Image.open(buf).convert("RGB")

# ----------------------------- Render composto
def render():
    CAN_W, CAN_H = 1920, 1080
    LEFT_W = int(CAN_W*0.60)
    RIGHT_W = CAN_W - LEFT_W

    # SAR à esquerda
    sar = SAR_RAW.convert("RGB")
    sar = ImageOps.fit(sar, (LEFT_W, CAN_H), Image.LANCZOS)
    dL = ImageDraw.Draw(sar); sx,sy = LEFT_W/W0, CAN_H/H0
    if SHOW_P:
        for (x0,y0,x1,y1) in piers:
            dL.rectangle([x0*sx,y0*sy,x1*sx,y1*sy], outline=CYAN, width=2)
    if SHOW_V or SHOW_D:
        for i,(cx,cy) in enumerate(vessels):
            r=6; is_dark=i in dark_idx
            if is_dark and SHOW_D: dL.ellipse([cx*sx-r,cy*sy-r,cx*sx+r,cy*sy+r], outline=RED, width=2)
            elif (not is_dark) and SHOW_V: dL.ellipse([cx*sx-r,cy*sy-r,cx*sx+r,cy*sy+r], outline=GREEN, width=2)
    if SHOW_T:
        for (cx,cy,r0) in tanks:
            r=int(r0*(sx+sy)/2)
            dL.ellipse([cx*sx-r,cy*sy-r,cx*sx+r,cy*sy+r], outline=YELLOW, width=2)

    # Painel à direita
    panel = Image.new("RGB",(RIGHT_W,CAN_H), BG)
    p = ImageDraw.Draw(panel)

    # Header
    head = Image.new("RGB",(RIGHT_W-32,110), CARD); h=ImageDraw.Draw(head)
    logo = Path("dapatlas_whitebg.png")
    if logo.exists():
        lg = Image.open(logo).convert("RGBA"); lg = ImageOps.contain(lg,(84,84), Image.LANCZOS); head.paste(lg,(16,13),lg)
    h.text((120,18), TITLE, fill=TEXT, font=font(True,28))
    h.text((120,56), SUBTITLE, fill=MUTED, font=font(False,20))
    h.text((120,84), f"AOI {AOI}  •  Generated: {datetime.now().strftime('%d/%m/%Y %H:%M')}  •  {BADGE}",
           fill=MUTED, font=font(False,16))
    panel.paste(head,(16,16))

    # KPI bar
    kpi_y=136; kpi_h=92; card_w=RIGHT_W-32
    kbar = Image.new("RGB",(card_w,kpi_h),(13,20,36)); kd=ImageDraw.Draw(kbar)
    kd.rectangle([0,0,card_w-1,kpi_h-1], outline=BORDER, width=2)
    labels = ["Vessels Detected","Dark Ships (%)","Pier Occupancy","Tanks Identified"]
    values = [str(kpi_vessels), f"{kpi_dark_pct} %", f"{kpi_pier_occ} %", str(kpi_tanks)]
    col_w = card_w//4
    for i in range(4):
        x0=i*col_w; x1=(i+1)*col_w if i<3 else card_w
        v=values[i]; fv=font(True,28); w=kd.textlength(v,font=fv)
        kd.text((x0+(col_w-w)/2,10), v, fill=TEXT, font=fv)
        l=labels[i]; fl=font(False,15); w2=kd.textlength(l,font=fl)
        kd.text((x0+(col_w-w2)/2,52), l, fill=MUTED, font=fl)
        if i<3: kd.line([(x1,12),(x1,kpi_h-12)], fill="#22304f", width=1)
    panel.paste(kbar,(16,kpi_y))
    gy = kpi_y + kpi_h + 16

    # Gráfico 1 — Oil Storage
    chart1 = plot_to_img("Oil Storage Volume by Date", "Acquisition Date", "Million Barrels",
                         [ {"y":oil_series, "label":"Oil Storage"} ], (RIGHT_W-32,250), legend=False)
    panel.paste(chart1,(16,gy)); gy += chart1.size[1] + 12

    # Gráfico 2 — Waiting Time (Anchorage)
    chart2 = plot_to_img("Waiting Time in Anchorage Zone", "Acquisition Date", "Avg Time (hours)",
                         [ {"y":wait_series, "label":"Waiting Time", "type":"bar"} ],
                         (RIGHT_W-32,250), legend=False)
    panel.paste(chart2,(16,gy)); gy += chart2.size[1] + 12

    # Gráfico 3 — Ships vs No AIS
    chart3 = plot_to_img("Ships in Anchorage vs Not Reporting AIS", "Acquisition Date", "Ships",
                         [ {"y":ships_series, "label":"Anchorage"},
                           {"y":noais_series, "label":"No AIS"} ],
                         (RIGHT_W-32,250), legend=True)
    panel.paste(chart3,(16,gy)); gy += chart3.size[1] + 10

    # Compose final
    canvas = Image.new("RGB",(1920,1080), BG)
    canvas.paste(sar,(0,0))
    canvas.paste(panel,(int(1920*0.60),0))
    buf = BytesIO(); canvas.save(buf,"PNG"); buf.seek(0)
    return canvas, buf

with st.spinner("Gerando painel…"):
    composite_img, composite_png = render()

st.image(composite_img, caption="Preview (1920×1080) — SAR + Painel MAVIPE", use_column_width=True)

c1,c2 = st.columns(2)
with c1:
    st.download_button("📸 PNG (1920×1080)", data=composite_png.getvalue(),
                       file_name="DAP_ATLAS_PORT_SAR_KPIs.png", mime="image/png")
with c2:
    try:
        from reportlab.lib.pagesizes import landscape, A4
        from reportlab.pdfgen import canvas as pdfcanvas
        from reportlab.lib.utils import ImageReader
        pdf = BytesIO()
        c = pdfcanvas.Canvas(pdf, pagesize=landscape(A4))
        Wp,Hp = landscape(A4); margin=18
        c.drawImage(ImageReader(BytesIO(composite_png.getvalue())), margin, margin,
                    width=Wp-2*margin, height=Hp-2*margin, mask='auto')
        c.showPage(); c.save(); pdf.seek(0)
        st.download_button("📄 PDF (A4 landscape)", data=pdf.getvalue(),
                           file_name="DAP_ATLAS_PORT_SAR_KPIs.pdf", mime="application/pdf")
    except Exception as e:
        st.info(f"PDF opcional indisponível ({e}). Instale reportlab para habilitar.")

