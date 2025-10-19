 # -*- coding: utf-8 -*-
# DAP ATLAS — Port Monitoring from Satellite Imagery (MAVIPE SaaS Dashboard)
# 100% offline: matplotlib + reportlab. Export: PNG (dashboard colado) e PDF.

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from datetime import datetime, timedelta
from PIL import Image, ImageOps
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from pathlib import Path

# ---------------------- THEME ----------------------
PRIMARY   = "#00E3A5"
BG_DARK   = "#0b1221"
CARD      = "#10182b"
TEXT      = "#E6EEFC"
MUTED     = "#9fb0c9"
BORDER    = "#1d2942"

st.set_page_config(page_title="DAP ATLAS — Port Monitoring (SaaS)", page_icon="🛰️", layout="wide")

st.markdown(f"""
<style>
:root {{
  --bg:{BG_DARK}; --card:{CARD}; --text:{TEXT}; --muted:{MUTED}; --border:{BORDER}; --primary:{PRIMARY};
}}
html, body, .stApp {{
  background: var(--bg);
  color: var(--text);
  font-family: Inter, Segoe UI, Roboto, Arial, sans-serif;
}}
.block-container {{ padding-top: 1rem; }}
.card {{
  background: var(--card); border: 1px solid var(--border); border-radius: 14px; padding: 12px;
  box-shadow: 0 18px 44px rgba(0,0,0,.45);
}}
.card h4 {{ margin: 0 0 6px 0; font-size: 1rem; color: {TEXT}; }}
.small {{ color: var(--muted); font-size: .9rem; }}
.kpi {{ display:grid; grid-template-columns: repeat(6,minmax(0,1fr)); gap:10px; }}
.kpi .box{{ background:rgba(255,255,255,.04); border:1px solid var(--border); border-radius:12px; padding:12px }}
.kpi .k {{ font-weight: 800 }}
.kpi .l {{ color: var(--muted); font-size:.85rem }}
hr {{ border: none; height: 1px; background: var(--border); margin: 12px 0 }}
.badge {{ background: rgba(0,227,165,.12); color: {PRIMARY}; border:1px solid rgba(0,227,165,.25);
  padding:6px 10px; border-radius:999px; font-weight:800; font-size:.85rem; }}
.table-wrap .dataframe td, .table-wrap .dataframe th {{ color:{TEXT}; border-color: {BORDER}; }}
</style>
""", unsafe_allow_html=True)

# ---------------------- SAMPLE DATA ----------------------
np.random.seed(7)
today = datetime(2024, 9, 7)  # para ficar parecido com seu mock
dates = pd.date_range(start=today- timedelta(days=15), end=today, freq="D")

# Tabela de schedule
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

# Séries
oil_vol = (18 + np.sin(np.linspace(0,3,len(dates)))*5 + np.random.uniform(-1,1,len(dates))).round(2)  # milhões bbl
wait_hours = (np.random.uniform(10,42,len(dates))).round(1)
ships_total = (15 + np.random.randint(-6,8,len(dates))).clip(6)  # ancorados
ships_dark  = (np.random.binomial(n=3,p=0.35,size=len(dates))).astype(int)  # sem AIS
forecast_dates = pd.date_range(end=today+timedelta(days=15), periods=15)
forecast_vals  = (18 + np.sin(np.linspace(1.2,2.8,len(forecast_dates)))*4 + np.random.uniform(-1,1,len(forecast_dates))).round(2)

# KPIs artificiais (último ponto)
kpi_oil_peak = oil_vol.max()
kpi_wait_avg = wait_hours.mean().round(1)
kpi_dark_pct = (ships_dark.sum()/ships_total.sum()*100).round(1)

AOI = "AOI CN-LN-DAL-PORT-2025-01"
SOURCE = "Optical (30 cm) + SAR (Spot) • Multi-vendor"
GENERATED = datetime.now().strftime("%d/%m/%Y %H:%M")

# ---------------------- HEADER ----------------------
colh1, colh2 = st.columns([0.75,0.25])
with colh1:
    st.markdown("## 🛰️ DAP ATLAS — **Port Monitoring Indexes** (SaaS)")
    st.caption(f"**AOI:** {AOI} • **Source:** {SOURCE} • **Generated:** {GENERATED}")
with colh2:
    logo_p = Path("dapatlas_whitebg.png")
    if logo_p.exists():
        st.image(str(logo_p), width=120)

# ---------------------- KPIs ----------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="kpi">', unsafe_allow_html=True)
st.markdown(f'<div class="box"><div class="k">{kpi_oil_peak:.2f} M bbl</div><div class="l">Peak Oil Storage (period)</div></div>', unsafe_allow_html=True)
st.markdown(f'<div class="box"><div class="k">{kpi_wait_avg} h</div><div class="l">Avg Waiting Time</div></div>', unsafe_allow_html=True)
st.markdown(f'<div class="box"><div class="k">{ships_total[-1]}</div><div class="l">Ships in Anchorage</div></div>', unsafe_allow_html=True)
st.markdown(f'<div class="box"><div class="k">{ships_dark[-1]}</div><div class="l">Ships w/o AIS (today)</div></div>', unsafe_allow_html=True)
st.markdown(f'<div class="box"><div class="k">{kpi_dark_pct}%</div><div class="l">No-AIS Share (period)</div></div>', unsafe_allow_html=True)
st.markdown(f'<div class="box"><div class="k">{dates[-1].strftime("%d %b %Y")}</div><div class="l">Last Acquisition Date</div></div>', unsafe_allow_html=True)
st.markdown('</div></div>', unsafe_allow_html=True)

st.write("")  # spacing

# ---------------------- GRID (2 colunas x 3 linhas) ----------------------
c1, c2 = st.columns([0.48, 0.52])

# --- (1) Schedule table
with c1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("#### Satellite Imagery Acquisition Schedule")
    st.dataframe(
        sched.reset_index(drop=True),
        height=230,
        use_container_width=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)

# helper para figuras com visual MAVIPE
def make_fig(figsize=(6,3)):
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(BG_DARK)
    ax.set_facecolor(CARD)
    ax.spines['bottom'].set_color(MUTED)
    ax.spines['top'].set_color(MUTED)
    ax.spines['left'].set_color(MUTED)
    ax.spines['right'].set_color(MUTED)
    ax.tick_params(colors=TEXT, labelsize=9)
    ax.grid(True, color="#22304f", alpha=.35, linestyle="--", linewidth=.7)
    return fig, ax

# --- (2) Oil storage (line/area)
with c2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("#### Volume of Oil Storage Site by Acquisition Date")
    fig1, ax1 = make_fig((6.8,3.2))
    ax1.plot(dates, oil_vol, linewidth=2, color=PRIMARY)
    ax1.fill_between(dates, oil_vol, color=PRIMARY, alpha=.18)
    ax1.set_ylabel("Million Barrels", color=TEXT)
    ax1.set_xlabel("Satellite Imagery Acquisition Date", color=TEXT)
    st.pyplot(fig1, transparent=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- (3) Waiting time (bars)
with c1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("#### Ships Waiting Time in Anchorage Zone")
    fig2, ax2 = make_fig((6.8,3.2))
    ax2.bar(dates, wait_hours, width=0.8, color="#3aa3ff")
    ax2.set_ylabel("Average Time (hours)", color=TEXT)
    ax2.set_xlabel("Satellite Imagery Acquisition Date", color=TEXT)
    st.pyplot(fig2, transparent=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- (4) Ships in Anchorage vs No AIS (lines)
with c2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("#### Ships in Anchorage Zone vs Not Reporting AIS")
    fig3, ax3 = make_fig((6.8,3.2))
    ax3.plot(dates, ships_total, linewidth=2, label="Ships in Anchorage", color="#4da3ff")
    ax3.plot(dates, ships_dark, linewidth=2, label="Ships Not Reporting AIS", color="#ff694a")
    ax3.legend(facecolor=CARD, labelcolor=TEXT, edgecolor=BORDER)
    ax3.set_ylabel("Number of Ships", color=TEXT)
    ax3.set_xlabel("Satellite Imagery Acquisition Date", color=TEXT)
    st.pyplot(fig3, transparent=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- (5) Forecast 15 days (line/area)
with c1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("#### Forecast of Oil Storage Volume — Next 15 Days")
    fig4, ax4 = make_fig((6.8,3.2))
    ax4.plot(forecast_dates, forecast_vals, linewidth=2, color=PRIMARY)
    ax4.fill_between(forecast_dates, forecast_vals, color=PRIMARY, alpha=.18)
    ax4.set_ylabel("Million Barrels", color=TEXT)
    ax4.set_xlabel("Date", color=TEXT)
    st.pyplot(fig4, transparent=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- (6) Situational Report
with c2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("#### Situational Report")
    peak_idx = int(np.argmax(oil_vol))
    trend_note = "decreasing" if forecast_vals[-1] < np.median(forecast_vals) else "increasing"
    report_txt = f"""
- Storage volume shows variability with a **peak of {kpi_oil_peak:.2f} M bbl** on **{dates[peak_idx].strftime('%d %b %Y')}**.  
- Anchorage waiting time averages **{kpi_wait_avg} hours**, with occasional spikes during **fog/storm** days.  
- Share of **non-reporting AIS** ships across the period: **{kpi_dark_pct}%**.  
- Forecast suggests **{trend_note}** activity in the next 15 days, which may affect berth allocation and tanker scheduling.  
- Recommendation: monitor **weather windows** and **AIS gaps**; set alerts when **No-AIS > 15%** and **waiting time > 36 h**.
"""
    st.markdown(report_txt)
    st.caption("Generated automatically from satellite-derived indicators (optical + SAR) and time-series analytics.")
    st.markdown('</div>', unsafe_allow_html=True)

st.write("")
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown(f'<span class="badge">Export</span>  ', unsafe_allow_html=True)

# ---------------------- EXPORT (Dashboard como PNG + PDF) ----------------------
def fig_to_png(fig):
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=220, bbox_inches="tight", facecolor=BG_DARK)
    buf.seek(0)
    return Image.open(buf)

# Renderiza as figuras novamente em memória para composição (garante resolução)
img1 = fig_to_png(fig1)
img2 = fig_to_png(fig2)
img3 = fig_to_png(fig3)
img4 = fig_to_png(fig4)

# Mini-colagem do dashboard (2 col x 2 lin) + cabeçalho
def compose_dashboard_png():
    # normaliza larguras
    w = max(img1.width, img2.width, img3.width, img4.width)
    pad = 20
    # linhas
    row1 = ImageOps.expand(Image.new("RGB", (w*2+pad, max(img1.height, img2.height)), (11,18,33)), border=0)
    row1.paste(img1, (0,0))
    row1.paste(img2, (img1.width+pad,0))
    row2 = ImageOps.expand(Image.new("RGB", (w*2+pad, max(img3.height, img4.height)), (11,18,33)), border=0)
    row2.paste(img3, (0,0))
    row2.paste(img4, (img3.width+pad,0))
    # header
    head_h = 80
    header = Image.new("RGB", (row1.width, head_h), (11,18,33))
    # texto simples no header
    try:
        from PIL import ImageDraw, ImageFont
        d = ImageDraw.Draw(header)
        d.text((18,18), "DAP ATLAS — Port Monitoring Indexes (SaaS)", fill=(230,238,252), anchor=None)
        d.text((18,45), f"AOI: {AOI} • Source: {SOURCE} • Generated: {GENERATED}", fill=(159,176,201))
    except Exception:
        pass
    # final
    canvas_img = Image.new("RGB", (row1.width, head_h + row1.height + pad + row2.height), (11,18,33))
    canvas_img.paste(header, (0,0))
    canvas_img.paste(row1, (0,head_h))
    canvas_img.paste(row2, (0,head_h + row1.height + pad))
    return canvas_img

dash_png = compose_dashboard_png()
buf_dash = BytesIO()
dash_png.save(buf_dash, format="PNG")
buf_dash.seek(0)

colE1, colE2 = st.columns(2)
with colE1:
    st.download_button("📸 Download Dashboard (PNG)", data=buf_dash.getvalue(),
                       file_name="DAP_ATLAS_Port_Dashboard.png", mime="image/png")

def export_pdf_from_png(png_bytes: bytes):
    buf_pdf = BytesIO()
    c = canvas.Canvas(buf_pdf, pagesize=landscape(A4))
    width, height = landscape(A4)
    image = ImageReader(BytesIO(png_bytes))
    # margem
    margin = 20
    c.drawImage(image, margin, margin, width=width-2*margin, height=height-2*margin, mask='auto')
    c.showPage()
    c.save()
    buf_pdf.seek(0)
    return buf_pdf

with colE2:
    pdf_buf = export_pdf_from_png(buf_dash.getvalue())
    st.download_button("📄 Download Dashboard (PDF)", data=pdf_buf.getvalue(),
                       file_name="DAP_ATLAS_Port_Dashboard.pdf", mime="application/pdf")

st.markdown('</div>', unsafe_allow_html=True)

st.caption("© 2025 MAVIPE Space Systems — MAVIPE SaaS theme (dark). Todos os gráficos e exportações funcionam offline.")
