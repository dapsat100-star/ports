# -*- coding: utf-8 -*-
# DAP ATLAS — PORT SAR KPIs (MAVIPE SaaS)
# Fonte: imagem SAR 'fon.png' (na pasta). Simula KPIs e sobreposições automaticamente.
# Saídas: preview em tela + download PNG (1920x1080) e PDF (A4 paisagem).

import streamlit as st
from pathlib import Path
from datetime import datetime
from io import BytesIO
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

# ======= Tema MAVIPE
BG      = (11, 18, 33)    # #0b1221
CARD    = (16, 24, 43)    # #10182b
BORDER  = (29, 41, 66)    # #1d2942
TEXT    = (230, 238, 252) # #E6EEFC
MUTED   = (159, 176, 201) # #9fb0c9
PRIMARY = (0, 227, 165)   # #00E3A5
BLUE    = (61, 163, 255)
ORANGE  = (255, 105, 74)
YELLOW  = (255, 210, 77)

def rgb(c): return tuple(v/255 for v in c)

def font(bold=False, size=20):
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", size)
    except:  # fallback
        return ImageFont.load_default()

# ======= Streamlit setup
st.set_page_config(page_title="DAP ATLAS — Port SAR KPIs (MAVIPE SaaS)", page_icon="🛰️", layout="wide")
st.markdown("""
<style>
html, body, .stApp { background:#0b1221; color:#E6EEFC; font-family:Inter, Segoe UI, Roboto, Arial, sans-serif; }
.block-container { padding-top: 1rem; max-width: 1500px; }
.card { background:#10182b; border:1px solid #1d2942; border-radius:12px; padding:12px; box-shadow:0 14px 32px rgba(0,0,0,.35); }
.kchip { background:#0d1526; border:1px solid #1d2942; border-radius:12px; padding:10px 14px; display:inline-block; margin-right:8px; }
</style>
""", unsafe_allow_html=True)

st.markdown("## 🛰️ DAP ATLAS — **Port SAR KPIs (SaaS)**")
st.caption("Imagem SAR como base • Sobreposições simuladas • Painel lateral com KPIs • Export PNG/PDF")

# ======= Carrega imagem SAR
sar_path = Path("fon.png")
if not sar_path.exists():
    st.error("Não encontrei `fon.png` na pasta. Coloque a imagem SAR com esse nome ao lado do app.")
    st.stop()

SAR_RAW = Image.open(sar_path).convert("L")  # grayscale
W0, H0 = SAR_RAW.size

# ======= Ferramentas de “detecção” simples (heurísticas por brilho)
def simulate_detections(img: Image.Image, grid=24, thr_bright=210, thr_water=40, seed=7):
    """
    Heurística leve (sem libs pesadas):
    - Divide em células; identifica células escuras (água) e pixels brilhantes (alvos metálicos).
    - Agrupa por célula -> pontos centrais viram marcadores.
    - Cria três camadas: vessels (água + branco), tanks (terra + brilhos), piers (linhas brilhantes).
    """
    np.random.seed(seed)
    a = np.array(img, dtype=np.uint8)
    h, w = a.shape
    # grade
    gx = max(1, w // grid)
    gy = max(1, h // grid)

    vessels = []   # (x, y)
    tanks   = []   # (x, y, r)
    piers   = []   # (x0,y0,x1,y1)

    for y in range(0, h, gy):
        for x in range(0, w, gx):
            tile = a[y:y+gy, x:x+gx]
            if tile.size == 0: continue
            mean = tile.mean()
            bright_mask = tile > thr_bright
            bright_ratio = bright_mask.mean() if tile.size else 0.0

            # água costuma ser escura; navios são “faíscas” brilhantes sobre água escura
            if mean < thr_water and bright_ratio > 0.01:
                cx = x + gx//2; cy = y + gy//2
                vessels.append((cx, cy))

            # tanques/casarias: bloco mais claro e com pontos brilhantes → marca círculo pequeno
            if mean > 90 and bright_ratio > 0.03:
                cx = x + gx//2; cy = y + gy//2
                r = max(3, int(0.35 * min(gx, gy)))
                tanks.append((cx, cy, r))

    # “piers” por linhas brilhantes: varredura de bandas horizontais
    band_h = max(6, gy // 2)
    for y in range(0, h, band_h):
        band = a[y:y+band_h, :]
        if band.size == 0: continue
        if (band > 200).mean() > 0.08 and (band.mean() > 70):
            x0, x1 = 12, w-12
            piers.append((x0, y + band_h//2 - 2, x1, y + band_h//2 + 2))

    # pós-processo: amostra um subconjunto para não poluir
    if len(vessels) > 140: vessels = list(np.array(vessels)[np.random.choice(len(vessels), 140, replace=False)])
    if len(tanks)   > 120: tanks   = list(np.array(tanks)[np.random.choice(len(tanks), 120, replace=False)])
    if len(piers)   > 14:  piers   = list(np.array(piers)[np.random.choice(len(piers), 14,  replace=False)])

    return vessels, tanks, piers

vessels, tanks, piers = simulate_detections(SAR_RAW)

# “Dark ships” (sem AIS): simulado como fração dos vessels
dark_ratio = 0.18 + 0.12*np.random.rand()     # 18–30%
dark_n = int(len(vessels) * dark_ratio)
dark_idx = set(np.random.choice(len(vessels), dark_n, replace=False))

# KPIs simulados
kpi_vessels = len(vessels)
kpi_dark_pct = round(100.0 * dark_n / max(1, kpi_vessels), 1)
kpi_pier_occ = min(100, int(35 + 50*np.random.rand()))  # %
kpi_tanks    = len(tanks)

# ======= Monta painel (composite) para export e preview
def render_composite():
    # canvas 1920x1080
    CAN_W, CAN_H = 1920, 1080
    LEFT_W = int(CAN_W*0.60)
    RIGHT_W = CAN_W - LEFT_W

    # esquerda: SAR + sobreposições
    sar = SAR_RAW.convert("RGB")
    sar = ImageOps.fit(sar, (LEFT_W, CAN_H), Image.LANCZOS)
    drawL = ImageDraw.Draw(sar)

    # desenha “piers”
    for (x0,y0,x1,y1) in piers:
        # escala coordenadas da imagem original para LEFT_W, CAN_H
        sx = LEFT_W / W0; sy = CAN_H / H0
        drawL.rectangle([x0*sx, y0*sy, x1*sx, y1*sy], outline=(140, 200, 255), width=2)

    # desenha “vessels”
    for i,(cx,cy) in enumerate(vessels):
        sx = LEFT_W / W0; sy = CAN_H / H0
        r = 6
        color = (255, 90, 74) if i in dark_idx else (122, 222, 122)
        drawL.ellipse([cx*sx-r, cy*sy-r, cx*sx+r, cy*sy+r], outline=color, width=2)

    # desenha “tanks”
    for (cx,cy,r0) in tanks:
        sx = LEFT_W / W0; sy = CAN_H / H0
        r = int(r0 * (sx+sy)/2)
        drawL.ellipse([cx*sx-r, cy*sy-r, cx*sx+r, cy*sy+r], outline=(255, 210, 77), width=2)

    # direita: painel SaaS
    panel = Image.new("RGB", (RIGHT_W, CAN_H), BG)
    pdraw = ImageDraw.Draw(panel)

    # header
    head = Image.new("RGB", (RIGHT_W-32, 110), CARD)
    hdraw = ImageDraw.Draw(head)
    logo_path = Path("dapatlas_whitebg.png")
    if logo_path.exists():
        lg = Image.open(logo_path).convert("RGBA")
        lg = ImageOps.contain(lg, (84,84), Image.LANCZOS)
        head.paste(lg, (16,13), lg)
    hdraw.text((120,18), "DAP ATLAS — PORT SAR KPIs", fill=TEXT, font=font(True, 28))
    hdraw.text((120,56), "SAR-based observables • ISR / C2 Support", fill=MUTED, font=font(False, 20))
    hdraw.text((120,84), f"Generated: {datetime.now().strftime('%d/%m/%Y %H:%M')}", fill=MUTED, font=font(False, 16))
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
        # valor
        v = values[i]
        w, h = kdraw.textlength(v, font=font(True, 28)), font(True, 28).getbbox("Ag")[3]
        kdraw.text((x0 + (col_w-w)/2, 10), v, fill=TEXT, font=font(True, 28))
        # label
        l = labels[i]
        w2, h2 = kdraw.textlength(l, font=font(False, 15)), font(False, 15).getbbox("Ag")[3]
        kdraw.text((x0 + (col_w-w2)/2, 52), l, fill=MUTED, font=font(False, 15))
        if i < cols-1:
            kdraw.line([(x1, 12), (x1, kpi_h-12)], fill="#22304f", width=1)

    panel.paste(kpi_bar, (16, kpi_y))
    grid_y = kpi_y + kpi_h + 16

    # “Findings”
    find_h = 170
    findings = Image.new("RGB", (card_w, find_h), CARD)
    fdrw = ImageDraw.Draw(findings)
    fdrw.rectangle([0,0,card_w-1,find_h-1], outline=BORDER)
    fdrw.text((12,8), "Key Findings", fill=TEXT, font=font(True, 20))
    bullets = [
        f"{kpi_vessels} vessels detected; {kpi_dark_pct}% estimated as dark (no AIS).",
        f"Pier occupancy ~ {kpi_pier_occ}% (bright linear structures along quays).",
        f"{kpi_tanks} circular structures consistent with storage tanks.",
        "Wake-like highlights indicate moving targets inside the basin.",
        "KPIs are auto-derived heuristics from SAR brightness and texture."
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
    # pontos
    ldrw.ellipse([14,42,14+16,42+16], outline=(122,222,122), width=3)
    ldrw.text((36,42), "Vessel (AIS on / generic)", fill=TEXT, font=font(False, 16))
    ldrw.ellipse([14,70,14+16,70+16], outline=(255,90,74), width=3)
    ldrw.text((36,70), "Dark Ship (no AIS)", fill=TEXT, font=font(False, 16))
    ldrw.rectangle([260,46,260+34,46+10], outline=(140,200,255), width=2)
    ldrw.text((302,42), "Pier / Active quay", fill=TEXT, font=font(False, 16))
    ldrw.ellipse([520,42,520+18,42+18], outline=(255,210,77), width=3)
    ldrw.text((546,42), "Storage tank", fill=TEXT, font=font(False, 16))
    panel.paste(legend, (16, grid_y))
    grid_y += leg_h + 12

    # Footer
    fdraw = ImageDraw.Draw(panel)
    fdraw.text((16, CAN_H-30), "© 2025 MAVIPE Space Systems — DAP ATLAS", fill=MUTED, font=font(False, 16))

    # compõe final
    composite = Image.new("RGB", (CAN_W, CAN_H), BG)
    composite.paste(sar, (0,0))
    composite.paste(panel, (LEFT_W,0))

    # buffers
    png = BytesIO(); composite.save(png, "PNG"); png.seek(0)
    return composite, png

# ======= UI — preview + downloads
with st.spinner("Processando SAR e gerando painel..."):
    composite_img, composite_png = render_composite()

# Layout responsivo: imagem grande
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
