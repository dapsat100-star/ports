# -*- coding: utf-8 -*-
# DAP ATLAS — PORT SITREP (Poster 1920x1080, estilo MAVIPE) — Streamlit
# Preview na página + download PNG/PDF (para PowerPoint)

import streamlit as st
from pathlib import Path
from datetime import datetime, timedelta
from io import BytesIO

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont, ImageOps

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ======= Tema MAVIPE
BG      = (11, 18, 33)    # #0b1221
CARD    = (16, 24, 43)    # #10182b
BORDER  = (29, 41, 66)    # #1d2942
TEXT    = (230, 238, 252) # #E6EEFC
MUTED   = (159, 176, 201) # #9fb0c9
PRIMARY = (0, 227, 165)   # #00E3A5
BLUE    = (61, 163, 255)
ORANGE  = (255, 105, 74)

def rgb(c): return tuple(v/255 for v in c)

def draw_text(d, xy, txt, size=28, fill=TEXT, bold=False):
    try:
        f = ImageFont.truetype("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", size)
    except Exception:
        f = ImageFont.load_default()
    d.text(xy, txt, fill=fill, font=f)

def draw_centered(d: ImageDraw.ImageDraw, box, txt, size=24, fill=TEXT, bold=False):
    """Centraliza texto dentro de 'box' = [x0,y0,x1,y1]."""
    try:
        f = ImageFont.truetype("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", size)
    except Exception:
        f = ImageFont.load_default()
    x0,y0,x1,y1 = box
    # largura aproximada do texto
    try:
        w = d.textlength(txt, font=f)
        h = f.getbbox("Ag")[3]  # altura aproximada
    except Exception:
        w, h = len(txt)*size*0.6, size
    x = x0 + (x1-x0 - w)/2
    y = y0 + (y1-y0 - h)/2
    d.text((x,y), txt, fill=fill, font=f)

def make_axes(figsize=(4.6, 2.2)):
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(rgb(BG))
    ax.set_facecolor(rgb(CARD))
    for s in ax.spines.values(): s.set_color('#1d2942')
    ax.tick_params(colors='#E6EEFC', labelsize=8)
    ax.grid(True, color="#22304f", alpha=.35, linestyle="--", linewidth=.6)
    return fig, ax

def fig_to_img(fig):
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=160, bbox_inches="tight", facecolor=rgb(BG))
    buf.seek(0)
    return Image.open(buf)

# ======= Página
st.set_page_config(page_title="DAP ATLAS — Port SITREP (Poster)", page_icon="🛰️", layout="wide")
st.markdown("""
<style>
html, body, .stApp { background:#0b1221; color:#E6EEFC; font-family:Inter, Segoe UI, Roboto, Arial, sans-serif; }
.block-container { padding-top: 1rem; max-width: 1300px; }
</style>
""", unsafe_allow_html=True)

st.markdown("## 🛰️ DAP ATLAS — **Port SITREP Poster**")
st.caption("Mapa à esquerda • Painel de inteligência à direita • Export pronto para PowerPoint")

# ======= Dados (mock; troque pelos seus)
np.random.seed(7)
today  = datetime(2024, 9, 7)
dates  = pd.date_range(start=today - timedelta(days=15), end=today, freq="D")
oil    = (18 + np.sin(np.linspace(0,3,len(dates)))*5 + np.random.uniform(-1,1,len(dates))).round(2)
wait_h = (np.random.uniform(10,42,len(dates))).round(1)
ships  = (15 + np.random.randint(-6,8,len(dates))).clip(6)
dark   = (np.random.binomial(n=3,p=0.35,size=len(dates))).astype(int)
fdates = pd.date_range(end=today+timedelta(days=15), periods=15)
fores  = (18 + np.sin(np.linspace(1.2,2.8,len(fdates)))*4 + np.random.uniform(-1,1,len(fdates))).round(2)

peak_oil   = float(oil.max())
avg_wait   = float(wait_h.mean().round(1))
dark_share = float((dark.sum()/ships.sum()*100).round(1))

AOI    = "AOI CN-LN-DAL-PORT-2025-01"
SOURCE = "Optical (30 cm) + SAR (Spot) • Multi-vendor"
GEN    = datetime.now().strftime("%d/%m/%Y %H:%M")

def build_poster():
    # ===== Canvas
    W, H = 1920, 1080
    LEFT_W = int(W*0.60)
    RIGHT_W = W - LEFT_W

    canvas = Image.new("RGB", (W,H), BG)
    draw   = ImageDraw.Draw(canvas)

    # ===== Lado esquerdo (mapa)
    map_path = Path("port_sat.png")
    if map_path.exists():
        m = Image.open(map_path).convert("RGB")
        m = ImageOps.fit(m, (LEFT_W, H), Image.LANCZOS)
    else:
        # placeholder
        m = Image.new("RGB", (LEFT_W, H), (20,30,50))
        g = ImageDraw.Draw(m); g.rectangle([24,24,LEFT_W-24,H-24], outline=(40,60,90), width=2)
        draw_text(g, (40,40), "port_sat.png not found", 24, (200,210,230))
    canvas.paste(m, (0,0))
    draw.line([(LEFT_W,0),(LEFT_W,H)], fill=BORDER, width=2)

    # ===== Painel direito
    panel = Image.new("RGB", (RIGHT_W, H), BG)
    pdraw = ImageDraw.Draw(panel)

    # Header
    head = Image.new("RGB", (RIGHT_W-32, 110), CARD)
    hdraw = ImageDraw.Draw(head)
    logo_path = Path("dapatlas_whitebg.png")
    if logo_path.exists():
        lg = Image.open(logo_path).convert("RGBA")
        lg = ImageOps.contain(lg, (84,84), Image.LANCZOS)
        head.paste(lg, (16,13), lg)
    draw_text(hdraw, (120,18), "DAP ATLAS — PORT SITREP", 28, TEXT, True)
    draw_text(hdraw, (120,56), "Satellite-derived KPIs • C2 Support", 20, MUTED)
    draw_text(hdraw, (120,84), f"Source: {SOURCE}  •  Generated: {GEN}", 16, MUTED)
    panel.paste(head, (16,16))

    # ===== KPI BAR ancorado (3 KPIs)
    kpi_y = 136
    kpi_h = 92
    card_w = RIGHT_W - 32
    kpi_bg = (13, 20, 36)

    kpi_bar = Image.new("RGB", (card_w, kpi_h), kpi_bg)
    kdraw = ImageDraw.Draw(kpi_bar)
    kdraw.rectangle([0,0,card_w-1,kpi_h-1], outline=BORDER, width=2)

    cols = 3
    col_w = card_w // cols
    labels = ["Peak Oil Storage", "Avg Waiting Time", "Ships in Anchorage"]
    values = [f"{peak_oil:.2f} M bbl", f"{avg_wait} h", f"{int(ships[-1])}"]

    for i in range(cols):
        x0 = i*col_w
        x1 = (i+1)*col_w if i < cols-1 else card_w
        draw_centered(kdraw, [x0, 6, x1, 50], values[i], size=28, fill=TEXT, bold=True)
        draw_centered(kdraw, [x0, 50, x1, kpi_h-8], labels[i], size=15, fill=MUTED, bold=False)
        if i < cols-1:
            kdraw.line([(x1, 12), (x1, kpi_h-12)], fill="#22304f", width=1)

    panel.paste(kpi_bar, (16, kpi_y))
    grid_y = kpi_y + kpi_h + 16

    # ===== Gráficos (4 cards empilhados)
    card_w = RIGHT_W - 32
    row_h  = 235

    def chart_card(title, fig):
        img = fig_to_img(fig)
        card = Image.new("RGB", (card_w, row_h), CARD)
        c = ImageDraw.Draw(card)
        c.rectangle([0,0,card_w-1,row_h-1], outline=BORDER)
        draw_text(c,(12,8), title, 20, TEXT, True)
        chart = ImageOps.contain(img, (card_w-24, row_h-36))
        card.paste(chart, (12, 28))
        return card

    # Oil storage
    fig1, ax1 = make_axes((6.3, 1.9))
    ax1.plot(dates, oil, color=rgb(PRIMARY), linewidth=2)
    ax1.fill_between(dates, oil, color=rgb(PRIMARY), alpha=.18)
    ax1.set_ylabel("Million Barrels", color="#E6EEFC", fontsize=9)
    ax1.set_xlabel("Acquisition Date", color="#E6EEFC", fontsize=9)

    # Waiting time
    fig2, ax2 = make_axes((6.3, 1.9))
    ax2.bar(dates, wait_h, color=rgb(BLUE), width=0.75)
    ax2.set_ylabel("Avg Time (hours)", color="#E6EEFC", fontsize=9)
    ax2.set_xlabel("Acquisition Date", color="#E6EEFC", fontsize=9)

    # Ships vs No-AIS
    fig3, ax3 = make_axes((6.3, 1.9))
    ax3.plot(dates, ships, color=rgb(BLUE), linewidth=2, label="Anchorage")
    ax3.plot(dates, dark,  color=rgb(ORANGE), linewidth=2, label="No AIS")
    leg = ax3.legend(facecolor=rgb(CARD), edgecolor="#1d2942", fontsize=8)
    for t in leg.get_texts(): t.set_color("#E6EEFC")
    ax3.set_ylabel("Ships", color="#E6EEFC", fontsize=9)
    ax3.set_xlabel("Acquisition Date", color="#E6EEFC", fontsize=9)

    # 15-day Forecast
    fig4, ax4 = make_axes((6.3, 1.9))
    ax4.plot(fdates, fores, color=rgb(PRIMARY), linewidth=2)
    ax4.fill_between(fdates, fores, color=rgb(PRIMARY), alpha=.18)
    ax4.set_ylabel("Million Barrels", color="#E6EEFC", fontsize=9)
    ax4.set_xlabel("Date", color="#E6EEFC", fontsize=9)

    cards = [
        chart_card("Oil Storage Volume by Date", fig1),
        chart_card("Waiting Time in Anchorage Zone", fig2),
        chart_card("Ships in Anchorage vs Not Reporting AIS", fig3),
        chart_card("15-day Forecast — Oil Storage", fig4),
    ]
    for i, c in enumerate(cards):
        panel.paste(c, (16, grid_y + i*(row_h + 12)))

    # ===== Sitrep (texto curto)
    sit_h = 138
    sit = Image.new("RGB", (card_w, sit_h), CARD)
    sdrw = ImageDraw.Draw(sit)
    sdrw.rectangle([0,0,card_w-1,sit_h-1], outline=BORDER)
    draw_text(sdrw, (12, 8), "Situational Report", 20, TEXT, True)
    lines = [
        f"Storage variability; peak {peak_oil:.2f} M bbl on {dates[oil.argmax()].strftime('%d %b %Y')}.",
        f"Average waiting time {avg_wait} h (spikes under fog/storm).",
        f"No-AIS share across period: {dark_share}%.",
        "15-day outlook suggests decreasing activity.",
        "Alerts: raise when No-AIS > 15% or waiting > 36 h."
    ]
    y = 36
    for t in lines:
        draw_text(sdrw, (12, y), "• " + t, 18, TEXT); y += 22
    # posiciona sitrep acima do primeiro gráfico
    panel.paste(sit, (16, grid_y - (sit_h + 12)))

    # Footer
    draw_text(pdraw, (16, H-30), "© 2025 MAVIPE Space Systems — DAP ATLAS", 16, MUTED)

    # monta poster
    canvas.paste(panel, (LEFT_W, 0))

    # retorna PNG buffer + PIL
    png = BytesIO(); canvas.save(png, "PNG"); png.seek(0)
    return canvas, png

with st.spinner("Gerando pôster..."):
    poster_img, poster_png = build_poster()

st.image(poster_img, caption="Pré-visualização (1920×1080)", use_column_width=True)

col1, col2 = st.columns(2)
with col1:
    st.download_button("📸 Download PNG (1920×1080)",
                       data=poster_png.getvalue(),
                       file_name="DAP_ATLAS_PORT_SITREP.png",
                       mime="image/png")

with col2:
    # PDF (A4 landscape) via ReportLab
    try:
        from reportlab.lib.pagesizes import landscape, A4
        from reportlab.pdfgen import canvas as pdfcanvas
        from reportlab.lib.utils import ImageReader
        buf = BytesIO()
        c = pdfcanvas.Canvas(buf, pagesize=landscape(A4))
        Wp, Hp = landscape(A4)
        img_reader = ImageReader(BytesIO(poster_png.getvalue()))
        margin = 18
        c.drawImage(img_reader, margin, margin, width=Wp-2*margin, height=Hp-2*margin, mask='auto')
        c.showPage(); c.save(); buf.seek(0)
        st.download_button("📄 Download PDF (A4 landscape)",
                           data=buf.getvalue(),
                           file_name="DAP_ATLAS_PORT_SITREP.pdf",
                           mime="application/pdf")
    except Exception as e:
        st.info(f"PDF opcional indisponível ({e}). Instale reportlab para habilitar.")
