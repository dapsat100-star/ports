# -*- coding: utf-8 -*-
# DAP ATLAS — PORT SITREP (Static Poster 1920x1080, MAVIPE style)
# Output: PNG + PDF for PowerPoint
#
# Optional assets in the working folder:
#  - port_sat.png               (map/satellite background, left side)
#  - dapatlas_whitebg.png       (logo, panel header)

from pathlib import Path
from datetime import datetime, timedelta
from io import BytesIO

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont, ImageOps

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ------------------ Theme (MAVIPE)
BG      = (11, 18, 33)        # #0b1221
CARD    = (16, 24, 43)        # #10182b
BORDER  = (29, 41, 66)        # #1d2942
TEXT    = (230, 238, 252)     # #E6EEFC
MUTED   = (159, 176, 201)     # #9fb0c9
PRIMARY = (0, 227, 165)       # #00E3A5
BLUE    = (61, 163, 255)
ORANGE  = (255, 105, 74)

# ------------------ Canvas
W, H = 1920, 1080
LEFT_W = int(W * 0.60)   # mapa
RIGHT_W = W - LEFT_W     # painel

# ------------------ Helper: text
def draw_text(d: ImageDraw.Draw, xy, txt, size=28, fill=TEXT, bold=False):
    try:
        # tenta fontes do sistema (opcional)
        fontname = "Inter-Bold.ttf" if bold else "Inter-Regular.ttf"
        f = ImageFont.truetype(fontname, size)
    except Exception:
        f = ImageFont.load_default()
    d.text(xy, txt, fill=fill, font=f)

# ------------------ Helper: chart -> PIL Image
def fig_to_img(fig, bg=BG):
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=160, bbox_inches="tight", facecolor=np.array(bg)/255.0)
    buf.seek(0)
    return Image.open(buf)

def make_axes(figsize=(4.4,2.2)):
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(np.array(BG)/255.0)
    ax.set_facecolor(np.array(CARD)/255.0)
    for s in ['bottom','top','left','right']:
        ax.spines[s].set_color('#1d2942')
    ax.tick_params(colors='#E6EEFC', labelsize=8)
    ax.grid(True, color="#22304f", alpha=.35, linestyle="--", linewidth=.6)
    return fig, ax

# ------------------ Mock data (substitua pelos seus)
np.random.seed(7)
today = datetime(2024, 9, 7)
dates = pd.date_range(start=today - timedelta(days=15), end=today, freq="D")
oil = (18 + np.sin(np.linspace(0,3,len(dates)))*5 + np.random.uniform(-1,1,len(dates))).round(2)
wait_h = (np.random.uniform(10,42,len(dates))).round(1)
ships = (15 + np.random.randint(-6,8,len(dates))).clip(6)
dark  = (np.random.binomial(n=3,p=0.35,size=len(dates))).astype(int)
fdates = pd.date_range(end=today+timedelta(days=15), periods=15)
fores  = (18 + np.sin(np.linspace(1.2,2.8,len(fdates)))*4 + np.random.uniform(-1,1,len(fdates))).round(2)

peak_oil = oil.max()
avg_wait = wait_h.mean().round(1)
dark_share = (dark.sum()/ships.sum()*100).round(1)

AOI     = "AOI CN-LN-DAL-PORT-2025-01"
SOURCE  = "Optical (30 cm) + SAR (Spot) • Multi-vendor"
GEN     = datetime.now().strftime("%d/%m/%Y %H:%M")

# ------------------ Base canvas
canvas = Image.new("RGB", (W, H), BG)
draw   = ImageDraw.Draw(canvas)

# ------------------ LEFT: Map
left = Image.new("RGB", (LEFT_W, H), BG)
map_p = Path("port_sat.png")
if map_p.exists():
    img = Image.open(map_p).convert("RGB")
    img = ImageOps.fit(img, (LEFT_W, H), Image.LANCZOS)
    left.paste(img, (0,0))
else:
    # placeholder quadriculado
    tile = Image.new("RGB", (64,64), (20,30,50))
    d2 = ImageDraw.Draw(tile)
    d2.rectangle([0,0,63,63], outline=(35,50,80))
    patt = Image.new("RGB", (LEFT_W, H), (12,19,34))
    for y in range(0, H, 64):
        for x in range(0, LEFT_W, 64):
            patt.paste(tile, (x,y))
    left = patt

# pequena faixa de legenda (opcional)
leg = Image.new("RGBA", (320,120), (0,0,0,120))
dleg = ImageDraw.Draw(leg)
draw_text(dleg, (12,8), "PORT MONITORING", 20, TEXT, True)
draw_text(dleg, (12,40), "Anchorage / Yard / Storage areas", 16, MUTED)
left.paste(leg, (16, H-136), leg)

canvas.paste(left, (0,0))

# divisória
draw.line([(LEFT_W,0),(LEFT_W,H)], fill=BORDER, width=2)

# ------------------ RIGHT: Intelligence Panel
panel = Image.new("RGB", (RIGHT_W, H), BG)
pdraw = ImageDraw.Draw(panel)

# Header block
header_h = 110
head = Image.new("RGB", (RIGHT_W-32, header_h), CARD)
hdraw = ImageDraw.Draw(head)

# logo
logo_p = Path("dapatlas_whitebg.png")
if logo_p.exists():
    logo = Image.open(logo_p).convert("RGBA")
    logo = ImageOps.contain(logo, (84,84), Image.LANCZOS)
else:
    # fallback
    logo = Image.new("RGBA", (84,84), (255,255,255,255))
    d3 = ImageDraw.Draw(logo); d3.text((18,28), "DA", fill=(0,0,0), font=ImageFont.load_default())

head.paste(logo, (16,13), logo)
draw_text(hdraw, (120,18), "DAP ATLAS — PORT SITREP", 28, TEXT, True)
draw_text(hdraw, (120,56), "Satellite-derived KPIs • C2 Support", 20, MUTED)
# badge
badge = Image.new("RGBA", (RIGHT_W-480, 34), (0,0,0,0))
bdrw = ImageDraw.Draw(badge)
bdrw.rounded_rectangle([0,0,badge.width-1,33], radius=16, outline=(0,227,165,255), width=2, fill=(0,227,165,30))
draw_text(bdrw, (12,7), f"{AOI} • Live 24/7", 18, (0,227,165), True)
head.paste(badge, (RIGHT_W-32-badge.width-8, 36), badge)

# small footer of header
draw_text(hdraw, (120,84), f"Source: {SOURCE}  •  Generated: {GEN}", 16, MUTED)

# mount header
panel.paste(head, (16,16))

# KPI chips
kpi_y = 146
chip_w, chip_h, gap = 206, 76, 12
kpis = [
    (f"{peak_oil:.2f} M bbl", "Peak Oil Storage"),
    (f"{avg_wait} h",         "Avg Waiting Time"),
    (f"{ships[-1]}",          "Ships in Anchorage"),
    (f"{dark[-1]}",           "Ships w/o AIS (today)"),
    (f"{dark_share} %",       "No-AIS Share"),
    (dates[-1].strftime("%d %b %Y"), "Last Acquisition"),
]
for i,(k,v) in enumerate(kpis):
    x = 16 + (i%3)*(chip_w+gap)
    y = kpi_y + (i//3)*(chip_h+gap)
    chip = Image.new("RGB", (chip_w, chip_h), CARD)
    cdrw = ImageDraw.Draw(chip)
    cdrw.rectangle([0,0,chip_w-1,chip_h-1], outline=BORDER, width=1)
    draw_text(cdrw, (12,10), k, 22, TEXT, True)
    draw_text(cdrw, (12,44), v, 16, MUTED)
    panel.paste(chip,(x,y))

# Chart cards (2x2)
card_w = RIGHT_W-32
row_h  = 260
grid_y = kpi_y + 2*(chip_h+gap) + 12

def chart_card(title, fig):
    img = fig_to_img(fig)
    card = Image.new("RGB", (card_w, row_h), CARD)
    c = ImageDraw.Draw(card)
    c.rectangle([0,0,card_w-1,row_h-1], outline=BORDER, width=1)
    draw_text(c, (12,8), title, 20, TEXT, True)
    # paste chart
    chart = ImageOps.contain(img, (card_w-24, row_h-36), Image.LANCZOS)
    card.paste(chart, (12, 28))
    return card

# Oil storage (line/area)
fig1, ax1 = make_axes((6.2,2.1))
ax1.plot(dates, oil, color=np.array(PRIMARY)/255.0, linewidth=2)
ax1.fill_between(dates, oil, color=np.array(PRIMARY)/255.0, alpha=.18)
ax1.set_ylabel("Million Barrels", color="#E6EEFC", fontsize=9)
ax1.set_xlabel("Acquisition Date", color="#E6EEFC", fontsize=9)

# Waiting (bars)
fig2, ax2 = make_axes((6.2,2.1))
ax2.bar(dates, wait_h, color=np.array(BLUE)/255.0, width=0.75)
ax2.set_ylabel("Avg Time (hours)", color="#E6EEFC", fontsize=9)
ax2.set_xlabel("Acquisition Date", color="#E6EEFC", fontsize=9)

# Ships vs No-AIS (lines)
fig3, ax3 = make_axes((6.2,2.1))
ax3.plot(dates, ships, color=np.array(BLUE)/255.0, linewidth=2, label="Anchorage")
ax3.plot(dates, dark,  color=np.array(ORANGE)/255.0, linewidth=2, label="No AIS")
ax3.legend(facecolor=np.array(CARD)/255.0, edgecolor="#1d2942", labelcolor="#E6EEFC", fontsize=8)
ax3.set_ylabel("Ships", color="#E6EEFC", fontsize=9)
ax3.set_xlabel("Acquisition Date", color="#E6EEFC", fontsize=9)

# Forecast (line/area)
fig4, ax4 = make_axes((6.2,2.1))
ax4.plot(fdates, fores, color=np.array(PRIMARY)/255.0, linewidth=2)
ax4.fill_between(fdates, fores, color=np.array(PRIMARY)/255.0, alpha=.18)
ax4.set_ylabel("Million Barrels", color="#E6EEFC", fontsize=9)
ax4.set_xlabel("Date", color="#E6EEFC", fontsize=9)

# mount 2x2 grid
c1 = chart_card("Oil Storage Volume by Date", fig1)
c2 = chart_card("Waiting Time in Anchorage Zone", fig2)
c3 = chart_card("Ships in Anchorage vs Not Reporting AIS", fig3)
c4 = chart_card("15-day Forecast — Oil Storage", fig4)

panel.paste(c1, (16, grid_y))
panel.paste(c2, (16, grid_y + row_h + 12))
panel.paste(c3, (16, grid_y + 2*(row_h + 12)))
# c4 ocupa metade da altura restante: ajusta para caber sobre o mapa? Mantemos dentro do painel:
panel.paste(c4, (16, grid_y + 3*(row_h + 12)))

# Sitrep box (texto curto) — opcional: trocar pelo seu texto
sit = Image.new("RGB", (card_w, 140), CARD)
sdrw = ImageDraw.Draw(sit)
sdrw.rectangle([0,0,card_w-1,139], outline=BORDER, width=1)
draw_text(sdrw, (12,8), "Situational Report", 20, TEXT, True)
lines = [
    f"Storage variability; peak {peak_oil:.2f} M bbl on {dates[oil.argmax()].strftime('%d %b %Y')}.",
    f"Average waiting time {avg_wait} h (spikes under fog/storm).",
    f"No-AIS share across period: {dark_share}%.",
    "15-day outlook suggests decreasing activity.",
    "Alerts: raise when No-AIS > 15% or waiting > 36 h."
]
y = 36
for t in lines:
    draw_text(sdrw, (12,y), "• " + t, 18, TEXT); y += 24

# cola o sitrep logo abaixo do header (antes dos charts)
panel.paste(sit, (16, grid_y - (140 + 12)))

# Footer
draw_text(pdraw, (16, H-30), "© 2025 MAVIPE Space Systems — DAP ATLAS", 16, MUTED)

# paste panel to canvas
canvas.paste(panel, (LEFT_W, 0))

# ------------------ Save PNG
out_png = "DAP_ATLAS_PORT_SITREP.png"
canvas.save(out_png, format="PNG")
print(f"[OK] PNG salvo: {out_png}")

# ------------------ Save PDF (one page, landscape A4)
try:
    from reportlab.lib.pagesizes import landscape, A4
    from reportlab.pdfgen import canvas as pdfcanvas
    from reportlab.lib.utils import ImageReader
    pdf_buf = BytesIO()
    c = pdfcanvas.Canvas("DAP_ATLAS_PORT_SITREP.pdf", pagesize=landscape(A4))
    Wp, Hp = landscape(A4)
    img_reader = ImageReader(out_png)
    margin = 18
    c.drawImage(img_reader, margin, margin, width=Wp-2*margin, height=Hp-2*margin, mask='auto')
    c.showPage(); c.save()
    print("[OK] PDF salvo: DAP_ATLAS_PORT_SITREP.pdf")
except Exception as e:
    print(f"[WARN] PDF opcional não gerado: {e}")
