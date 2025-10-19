# -*- coding: utf-8 -*-
# DAP ATLAS — PORT SITREP (Static Poster 1920x1080, MAVIPE style)
# Output: PNG + PDF for PowerPoint

from pathlib import Path
from datetime import datetime, timedelta
from io import BytesIO
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont, ImageOps
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------- THEME (MAVIPE)
BG      = (11, 18, 33)
CARD    = (16, 24, 43)
BORDER  = (29, 41, 66)
TEXT    = (230, 238, 252)
MUTED   = (159, 176, 201)
PRIMARY = (0, 227, 165)
BLUE    = (61, 163, 255)
ORANGE  = (255, 105, 74)

def rgb(c): return tuple(v / 255 for v in c)

# ---------- CANVAS
W, H = 1920, 1080
LEFT_W = int(W * 0.60)
RIGHT_W = W - LEFT_W

# ---------- TEXT HELPER
def draw_text(d: ImageDraw.Draw, xy, txt, size=28, fill=TEXT, bold=False):
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", size)
    except:
        font = ImageFont.load_default()
    d.text(xy, txt, fill=fill, font=font)

# ---------- CHART HELPER
def make_axes(figsize=(4.4, 2.2)):
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(rgb(BG))
    ax.set_facecolor(rgb(CARD))
    for s in ax.spines.values(): s.set_color('#1d2942')
    ax.tick_params(colors='#E6EEFC', labelsize=8)
    ax.grid(True, color="#22304f", alpha=.35, linestyle="--", linewidth=.6)
    return fig, ax

def fig_to_img(fig, bg=BG):
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=160, bbox_inches="tight", facecolor=rgb(bg))
    buf.seek(0)
    return Image.open(buf)

# ---------- MOCK DATA
np.random.seed(7)
today = datetime(2024, 9, 7)
dates = pd.date_range(start=today - timedelta(days=15), end=today, freq="D")
oil = (18 + np.sin(np.linspace(0, 3, len(dates))) * 5 + np.random.uniform(-1, 1, len(dates))).round(2)
wait_h = (np.random.uniform(10, 42, len(dates))).round(1)
ships = (15 + np.random.randint(-6, 8, len(dates))).clip(6)
dark = (np.random.binomial(n=3, p=0.35, size=len(dates))).astype(int)
fdates = pd.date_range(end=today + timedelta(days=15), periods=15)
fores = (18 + np.sin(np.linspace(1.2, 2.8, len(fdates))) * 4 + np.random.uniform(-1, 1, len(fdates))).round(2)

peak_oil = oil.max()
avg_wait = wait_h.mean().round(1)
dark_share = (dark.sum() / ships.sum() * 100).round(1)

AOI = "AOI CN-LN-DAL-PORT-2025-01"
SOURCE = "Optical (30 cm) + SAR (Spot) • Multi-vendor"
GEN = datetime.now().strftime("%d/%m/%Y %H:%M")

# ---------- CANVAS BASE
canvas = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(canvas)

# ---------- LEFT SIDE (MAP)
map_path = Path("port_sat.png")
if map_path.exists():
    img = Image.open(map_path).convert("RGB")
    img = ImageOps.fit(img, (LEFT_W, H), Image.LANCZOS)
else:
    img = Image.new("RGB", (LEFT_W, H), (20, 30, 50))
canvas.paste(img, (0, 0))
draw.line([(LEFT_W, 0), (LEFT_W, H)], fill=BORDER, width=2)

# ---------- RIGHT PANEL
panel = Image.new("RGB", (RIGHT_W, H), BG)
pdraw = ImageDraw.Draw(panel)

# HEADER
head = Image.new("RGB", (RIGHT_W - 32, 110), CARD)
hdraw = ImageDraw.Draw(head)
logo_path = Path("dapatlas_whitebg.png")
if logo_path.exists():
    logo = Image.open(logo_path).convert("RGBA")
    logo = ImageOps.contain(logo, (84, 84), Image.LANCZOS)
    head.paste(logo, (16, 13), logo)
draw_text(hdraw, (120, 18), "DAP ATLAS — PORT SITREP", 28, TEXT, True)
draw_text(hdraw, (120, 56), "Satellite-derived KPIs • C2 Support", 20, MUTED)
draw_text(hdraw, (120, 84), f"Source: {SOURCE}  •  Generated: {GEN}", 16, MUTED)
panel.paste(head, (16, 16))

# KPI CHIPS
kpi_y, chip_w, chip_h, gap = 146, 206, 76, 12
kpis = [
    (f"{peak_oil:.2f} M bbl", "Peak Oil Storage"),
    (f"{avg_wait} h", "Avg Waiting Time"),
    (f"{ships[-1]}", "Ships in Anchorage"),
    (f"{dark[-1]}", "Ships w/o AIS (today)"),
    (f"{dark_share} %", "No-AIS Share"),
    (dates[-1].strftime('%d %b %Y'), "Last Acquisition"),
]
for i, (k, v) in enumerate(kpis):
    x = 16 + (i % 3) * (chip_w + gap)
    y = kpi_y + (i // 3) * (chip_h + gap)
    chip = Image.new("RGB", (chip_w, chip_h), CARD)
    cdrw = ImageDraw.Draw(chip)
    cdrw.rectangle([0, 0, chip_w - 1, chip_h - 1], outline=BORDER)
    draw_text(cdrw, (12, 10), k, 22, TEXT, True)
    draw_text(cdrw, (12, 44), v, 16, MUTED)
    panel.paste(chip, (x, y))

# CHARTS
card_w, row_h = RIGHT_W - 32, 260
grid_y = kpi_y + 2 * (chip_h + gap) + 12

def chart_card(title, fig):
    img = fig_to_img(fig)
    card = Image.new("RGB", (card_w, row_h), CARD)
    c = ImageDraw.Draw(card)
    c.rectangle([0, 0, card_w - 1, row_h - 1], outline=BORDER)
    draw_text(c, (12, 8), title, 20, TEXT, True)
    chart = ImageOps.contain(img, (card_w - 24, row_h - 36))
    card.paste(chart, (12, 28))
    return card

# Oil Storage
fig1, ax1 = make_axes((6.2, 2.1))
ax1.plot(dates, oil, color=rgb(PRIMARY), linewidth=2)
ax1.fill_between(dates, oil, color=rgb(PRIMARY), alpha=.18)
ax1.set_ylabel("Million Barrels", color="#E6EEFC", fontsize=9)
ax1.set_xlabel("Acquisition Date", color="#E6EEFC", fontsize=9)

# Waiting
fig2, ax2 = make_axes((6.2, 2.1))
ax2.bar(dates, wait_h, color=rgb(BLUE), width=0.75)
ax2.set_ylabel("Avg Time (hours)", color="#E6EEFC", fontsize=9)
ax2.set_xlabel("Acquisition Date", color="#E6EEFC", fontsize=9)

# Ships vs No-AIS
fig3, ax3 = make_axes((6.2, 2.1))
ax3.plot(dates, ships, color=rgb(BLUE), linewidth=2, label="Anchorage")
ax3.plot(dates, dark, color=rgb(ORANGE), linewidth=2, label="No AIS")
leg = ax3.legend(facecolor=rgb(CARD), edgecolor="#1d2942", fontsize=8)
for t in leg.get_texts(): t.set_color("#E6EEFC")
ax3.set_ylabel("Ships", color="#E6EEFC", fontsize=9)
ax3.set_xlabel("Acquisition Date", color="#E6EEFC", fontsize=9)

# Forecast
fig4, ax4 = make_axes((6.2, 2.1))
ax4.plot(fdates, fores, color=rgb(PRIMARY), linewidth=2)
ax4.fill_between(fdates, fores, color=rgb(PRIMARY), alpha=.18)
ax4.set_ylabel("Million Barrels", color="#E6EEFC", fontsize=9)
ax4.set_xlabel("Date", color="#E6EEFC", fontsize=9)

# Combine
cards = [
    chart_card("Oil Storage Volume by Date", fig1),
    chart_card("Waiting Time in Anchorage Zone", fig2),
    chart_card("Ships in Anchorage vs Not Reporting AIS", fig3),
    chart_card("15-day Forecast — Oil Storage", fig4)
]
for i, c in enumerate(cards):
    panel.paste(c, (16, grid_y + i * (row_h + 12)))

# SITREP TEXT
sit = Image.new("RGB", (card_w, 140), CARD)
sdrw = ImageDraw.Draw(sit)
sdrw.rectangle([0, 0, card_w - 1, 139], outline=BORDER)
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
    draw_text(sdrw, (12, y), "• " + t, 18, TEXT); y += 24
panel.paste(sit, (16, grid_y - 152))

# FOOTER
draw_text(pdraw, (16, H - 30), "© 2025 MAVIPE Space Systems — DAP ATLAS", 16, MUTED)
canvas.paste(panel, (LEFT_W, 0))

# SAVE
out_png = "DAP_ATLAS_PORT_SITREP.png"
canvas.save(out_png, "PNG")
print(f"[OK] PNG saved → {out_png}")

try:
    from reportlab.lib.pagesizes import landscape, A4
    from reportlab.pdfgen import canvas as pdfcanvas
    from reportlab.lib.utils import ImageReader
    c = pdfcanvas.Canvas("DAP_ATLAS_PORT_SITREP.pdf", pagesize=landscape(A4))
    Wp, Hp = landscape(A4)
    img_reader = ImageReader(out_png)
    margin = 18
    c.drawImage(img_reader, margin, margin, width=Wp - 2 * margin, height=Hp - 2 * margin, mask='auto')
    c.showPage(); c.save()
    print("[OK] PDF saved → DAP_ATLAS_PORT_SITREP.pdf")
except Exception as e:
    print(f"[WARN] PDF not generated: {e}")
