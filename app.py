# -*- coding: utf-8 -*-
# DAP ATLAS — Port Monitoring from Satellite Imagery (MAVIPE SaaS — Compact One-Screen)
# Mostra tudo em uma única tela (grade 2x3), com export do quadro em PNG/PDF.

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from datetime import datetime, timedelta
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw

# ---------------------- THEME ----------------------
PRIMARY   = "#00E3A5"
BG_DARK   = "#0b1221"
CARD      = "#10182b"
TEXT      = "#E6EEFC"
MUTED     = "#9fb0c9"
BORDER    = "#1d2942"

st.set_page_config(page_title="DAP ATLAS — Port Monitoring (Compact)", page_icon="🛰️", layout="wide")

# CSS: reduzir paddings e esconder menu/rodapé
st.markdown(f"""
<style>
:root {{
  --bg:{BG_DARK}; --card:{CARD}; --text:{TEXT}; --muted:{MUTED}; --border:{BORDER}; --primary:{PRIMARY};
}}
html, body, .stApp {{ background: var(--bg); color: var(--text); font-family: Inter, Segoe UI, Roboto, Arial, sans-serif; }}
.block-container {{ padding-top: .5rem; padding-bottom: .5rem; max-width: 1400px; }}
#MainMenu {{visibility:hidden}} footer {{visibility:hidden}} header {{visibility:hidden}}

.card {{
  background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 8px;
  box-shadow: 0 14px 32px rgba(0,0,0,.35);
}}
.card h4 {{ margin: 0 0 4px 0; font-size: .95rem; color: {TEXT}; }}
.small {{ color: var(--muted); font-size: .85rem; }}
.kpi {{ display:grid; grid-template-columns: repeat(6,minmax(0,1fr)); gap:8px; }}
.kpi .box{{ background:rgba(255,255,255,.04); border:1px solid var(--border); border-radius:10px; padding:8px }}
.kpi .k {{ font-weight: 800; font-size: .98rem; }}
.kpi .l {{ color: var(--muted); font-size:.78rem }}
hr {{ border: none; height: 1px; background: var(--border); margin: 6px 0 }}
.table-wrap .dataframe td, .table-wrap .dataframe th {{ color:{TEXT}; border-color: {BORDER}; font-size:.82rem; }}
h2, h3 {{ margin: 0 0 6px 0; }}
</style>
""", unsafe_allow_html=True)

# ---------------------- DATA (mock) ----------------------
np.random.seed(7)
today = datetime(2024, 9, 7)
dates = pd.date_range(start=today- timedelta(days=15), end=today, freq="D")

weather = ["Clear","Fog","Storm","Rain"]
status  = ["Increase","Decrease"]
sched = pd.DataFrame({
    "Year": dates.year,
    "Quarter": ["Qtr 3"]*len(dates),
    "Month": dates.strftime("%B"),
    "Day": dates.day,
    "Weather Conditions": np.random.choice(weather, len(dates), p=[.45,.25,.2,.10]),
    "Port Activity Status": np.random.choice(status, len(dates))
})

oil_vol = (18 + np.sin(np.linspace(0,3,len(dates)))*5 + np.random.uniform(-1,1,len(dates))).round(2)  # M bbl
wait_hours = (np.random.uniform(10,42,len(dates))).round(1)
ships_total = (15 + np.random.randint(-6,8,len(dates))).clip(6)  # ancorados
ships_dark  = (np.random.binomial(n=3,p=0.35,size=len(dates))).astype(int)
forecast_dates = pd.date_range(end=today+timedelta(days=15), periods=15)
forecast_vals  = (18 + np.sin(np.linspace(1.2,2.8,len(forecast_dates)))*4 + np.random.uniform(-1,1,len(forecast_dates))).round(2)

kpi_oil_peak = oil_vol.max()
kpi_wait_avg = wait_hours.mean().round(1)
kpi_dark_pct = (ships_dark.sum()/ships_total.sum()*100).round(1)

AOI = "AOI CN-LN-DAL-PORT-2025-01"
SOURCE = "Optical (30 cm) + SAR (Spot) • Multi-vendor"
GENERATED = datetime.now().strftime("%d/%m/%Y %H:%M")

# ---------------------- HEADER COMPACTO ----------------------
left, right = st.columns([0.8, 0.2])
with left:
    st.markdown("## 🛰️ DAP ATLAS — **Port Monitoring Indexes** (Compact)")
    st.caption(f"**AOI:** {AOI} • **Source:** {SOURCE} • **Generated:** {GENERATED}")
with right:
    logo_p = Path("dapatlas_whitebg.png")
    if logo_p.exists():
        st.image(str(logo_p), width=110)

# ---------------------- KPIs FINOS ----------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="kpi">', unsafe_allow_html=True)
st.markdown(f'<div class="box"><div class="k">{kpi_oil_peak:.2f} M bbl</div><div class="l">Peak Oil Storage</div></div>', unsafe_allow_html=True)
st.markdown(f'<div class="box"><div class="k">{kpi_wait_avg} h</div><div class="l">Avg Waiting Time</div></div>', unsafe_allow_html=True)
st.markdown(f'<div class="box"><div class="k">{ships_total[-1]}</div><div class="l">Ships in Anchorage</div></div>', unsafe_allow_html=True)
st.markdown(f'<div class="box"><div class="k">{ships_dark[-1]}</div><div class="l">Ships w/o AIS (today)</div></div>', unsafe_allow_html=True)
st.markdown(f'<div class="box"><div class="k">{kpi_dark_pct}%</div><div class="l">No-AIS Share</div></div>', unsafe_allow_html=True)
st.markdown(f'<div class="box"><div class="k">{dates[-1].strftime("%d %b %Y")}</div><div class="l">Last Acquisition</div></div>', unsafe_allow_html=True)
st.markdown('</div></div>', unsafe_allow_html=True)

# helper p/ figuras slim no padrão MAVIPE
def make_fig(figsize=(5.8,2.6), labelsize=8):
    fig, ax = plt.subplots(figsize=figsize)
    fig.subplots_adjust(left=0.08, right=0.98, top=0.85, bottom=0.22)
    fig.patch.set_facecolor(BG_DARK)
    ax.set_facecolor(CARD)
    for s in ['bottom','top','left','right']:
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=TEXT, labelsize=labelsize)
    ax.grid(True, color="#22304f", alpha=.35, linestyle="--", linewidth=.6)
    return fig, ax

# ---------------------- GRADE 2x3 (sem scroll) ----------------------
# Linha 1: Schedule | Oil | Waiting
r1c1, r1c2, r1c3 = st.columns([0.36, 0.32, 0.32])

with r1c1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("#### Satellite Imagery Acquisition Schedule")
    st.dataframe(sched.reset_index(drop=True), height=210, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with r1c2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("#### Oil Storage Volume by Date")
    fig1, ax1 = make_fig()
    ax1.plot(dates, oil_vol, linewidth=2, color=PRIMARY)
    ax1.fill_between(dates, oil_vol, color=PRIMARY, alpha=.18)
    ax1.set_ylabel("Million Barrels", color=TEXT, fontsize=9)
    ax1.set_xlabel("Acquisition Date", color=TEXT, fontsize=9)
    st.pyplot(fig1, transparent=True)
    st.markdown('</div>', unsafe_allow_html=True)

with r1c3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("#### Waiting Time in Anchorage Zone")
    fig2, ax2 = make_fig()
    ax2.bar(dates, wait_hours, width=0.75, color="#3aa3ff")
    ax2.set_ylabel("Avg Time (hours)", color=TEXT, fontsize=9)
    ax2.set_xlabel("Acquisition Date", color=TEXT, fontsize=9)
    st.pyplot(fig2, transparent=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Linha 2: Ships vs No-AIS | Forecast | Sitrep
r2c1, r2c2, r2c3 = st.columns([0.36, 0.32, 0.32])

with r2c1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("#### Ships in Anchorage vs Not Reporting AIS")
    fig3, ax3 = make_fig()
    ax3.plot(dates, ships_total, linewidth=2, label="Anchorage", color="#4da3ff")
    ax3.plot(dates, ships_dark, linewidth=2, label="No AIS", color="#ff694a")
    leg = ax3.legend(facecolor=CARD, labelcolor=TEXT, edgecolor=BORDER, fontsize=8)
    ax3.set_ylabel("Ships", color=TEXT, fontsize=9)
    ax3.set_xlabel("Acquisition Date", color=TEXT, fontsize=9)
    st.pyplot(fig3, transparent=True)
    st.markdown('</div>', unsafe_allow_html=True)

with r2c2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("#### 15-day Forecast — Oil Storage")
    fig4, ax4 = make_fig()
    ax4.plot(forecast_dates, forecast_vals, linewidth=2, color=PRIMARY)
    ax4.fill_between(forecast_dates, forecast_vals, color=PRIMARY, alpha=.18)
    ax4.set_ylabel("Million Barrels", color=TEXT, fontsize=9)
    ax4.set_xlabel("Date", color=TEXT, fontsize=9)
    st.pyplot(fig4, transparent=True)
    st.markdown('</div>', unsafe_allow_html=True)

with r2c3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("#### Situational Report")
    peak_idx = int(np.argmax(oil_vol))
    trend_note = "decreasing" if forecast_vals[-1] < np.median(forecast_vals) else "increasing"
    st.markdown(f"""
- Storage shows variability; **peak {kpi_oil_peak:.2f} M bbl** on **{dates[peak_idx].strftime('%d %b %Y')}**.  
- Avg waiting time **{kpi_wait_avg} h**; spikes under fog/storm.  
- **No-AIS share** across period: **{kpi_dark_pct}%**.  
- 15-day outlook suggests **{trend_note}** activity; adjust berth allocation and tanker scheduling.  
- Alerts: raise when **No-AIS > 15%** or **waiting > 36 h**.
""")
    st.caption("Auto-generated from satellite-derived indicators (optical + SAR).")
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------- EXPORT (QUADRO INTEIRO) ----------------------
st.divider()
st.write("**Export**")

def fig_to_png(fig):
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=220, bbox_inches="tight", facecolor=BG_DARK)
    buf.seek(0);  return Image.open(buf)

img1, img2, img3, img4 = map(fig_to_png, [fig1, fig2, fig3, fig4])

def compose_dashboard_png():
    # mosaico 2x2 dos gráficos + cabeçalho texto; tabela e sitrep como blocos raster
    # captura rápida: renderiza HTML simples dos blocos texto via PIL (labels)
    pad = 18
    # Linha 1 (Oil | Waiting)
    row1_h = max(img1.height, img2.height)
    row1 = Image.new("RGB", (img1.width + pad + img2.width, row1_h), (11,18,33))
    row1.paste(img1, (0, row1_h - img1.height))
    row1.paste(img2, (img1.width + pad, row1_h - img2.height))
    # Linha 2 (Ships | Forecast)
    row2_h = max(img3.height, img4.height)
    row2 = Image.new("RGB", (img3.width + pad + img4.width, row2_h), (11,18,33))
    row2.paste(img3, (0, row2_h - img3.height))
    row2.paste(img4, (img3.width + pad, row2_h - img4.height))
    # Cabeçalho
    W = max(row1.width, row2.width)
    header_h = 90
    header = Image.new("RGB", (W, header_h), (11,18,33))
    d = ImageDraw.Draw(header)
    d.text((12, 12), "DAP ATLAS — Port Monitoring Indexes (Compact)", fill=(230,238,252))
    d.text((12, 46), f"AOI: {AOI}  •  Source: {SOURCE}  •  Generated: {GENERATED}", fill=(159,176,201))
    # Compose
    canvas = Image.new("RGB", (W, header_h + row1.height + pad + row2.height), (11,18,33))
    canvas.paste(header, (0, 0))
    canvas.paste(row1, (0, header_h))
    canvas.paste(row2, (0, header_h + row1.height + pad))
    return canvas

dash_png = compose_dashboard_png()
buf_png = BytesIO(); dash_png.save(buf_png, format="PNG"); buf_png.seek(0)

col_dl1, col_dl2 = st.columns(2)
with col_dl1:
    st.download_button("📸 Download One-Screen Dashboard (PNG)", data=buf_png.getvalue(),
                       file_name="DAP_ATLAS_Port_Dashboard_Compact.png", mime="image/png")

def export_pdf(png_bytes: bytes):
    from reportlab.lib.pagesizes import landscape, A4
    from reportlab.pdfgen import canvas as pdfcanvas
    from reportlab.lib.utils import ImageReader
    from io import BytesIO
    buf = BytesIO()
    c = pdfcanvas.Canvas(buf, pagesize=landscape(A4))
    W, H = landscape(A4)
    img = ImageReader(BytesIO(png_bytes))
    margin = 18
    c.drawImage(img, margin, margin, width=W-2*margin, height=H-2*margin, mask='auto')
    c.showPage(); c.save(); buf.seek(0); return buf

with col_dl2:
    from reportlab.lib.pagesizes import A4, landscape
    pdf_buf = export_pdf(buf_png.getvalue())
    st.download_button("📄 Download One-Screen Dashboard (PDF)", data=pdf_buf.getvalue(),
                       file_name="DAP_ATLAS_Port_Dashboard_Compact.pdf", mime="application/pdf")

st.caption("© 2025 MAVIPE Space Systems — MAVIPE SaaS compact layout (fits 1366×768).")
