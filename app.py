# -*- coding: utf-8 -*-
# DAP ATLAS — Port SaaS (Universal Edition)
# Funciona 100% em qualquer ambiente Streamlit, sem dependência de HTML/JS
# Exibe KPIs, gráfico temporal e permite exportar PNG e PDF com segurança

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# ==================== CONFIGURAÇÃO ====================
st.set_page_config(
    page_title="DAP ATLAS — Port SaaS",
    page_icon="🛰️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

PRIMARY   = "#00E3A5"
BG_DARK   = "#0b1221"
TEXT      = "#E6EEFC"
MUTED     = "#9fb0c9"

st.markdown(
    f"""
    <style>
    body {{
        background-color: {BG_DARK};
        color: {TEXT};
    }}
    .stApp {{
        background-color: {BG_DARK};
        color: {TEXT};
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ==================== DADOS SIMULADOS ====================
AOI_ID = "AOI CN-LN-DAL-PORT-2025-01"
NOW = datetime.now().strftime("%d/%m %H:%M")

dias = pd.date_range(end=datetime.now(), periods=14).strftime("%b %d")
valores = [812, 818, 827, 835, 842, 851, 860, 869, 874, 881, 888, 893, 900, 907]
df = pd.DataFrame({"Date": dias, "Vehicles": valores})

# ==================== HEADER ====================
st.markdown(f"### 🛰️ DAP ATLAS — Port SaaS")
st.markdown(f"#### **Automatic Vehicle Yard Counting**  \n**AOI:** {AOI_ID}  \n**Generated:** {NOW}")

st.divider()

# ==================== KPIs ====================
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)
col5, col6 = st.columns(2)

col1.metric("Vehicles (estimate)", "897 ±10%")
col2.metric("Confidence", "95%")
col3.metric("Processing Time", "10 s")
col4.metric("Analyzed Area", "0.24 km²")
col5.metric("Resolution", "30 cm")
col6.metric("Source", "BlackSky Global-16")

st.divider()

# ==================== ACHADOS ====================
st.markdown("#### Key Findings")
st.markdown("""
- Vehicle estimate derived by AI with local sampling supervision.  
- Two sectors above **85 % occupancy** (attention threshold).  
- **+7 % weekly trend** in yard stock (last 14 days).  
- Processing time: **10 seconds**, fully automated pipeline.
""")

# ==================== GRÁFICO ====================
st.markdown("#### Vehicle Trend — Last 14 Days")

fig, ax = plt.subplots(figsize=(7,3))
ax.plot(df["Date"], df["Vehicles"], color=PRIMARY, linewidth=2)
ax.fill_between(df["Date"], df["Vehicles"], color=PRIMARY, alpha=0.15)
ax.set_facecolor(BG_DARK)
fig.patch.set_facecolor(BG_DARK)
ax.tick_params(colors=TEXT, labelrotation=45)
ax.spines[:].set_color(MUTED)
ax.set_xlabel("")
ax.set_ylabel("Vehicles", color=TEXT)
st.pyplot(fig, transparent=True)

# ==================== EXPORTAÇÕES ====================
st.divider()
st.markdown("### Export Options")

def export_png():
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=300, bbox_inches="tight", facecolor=BG_DARK)
    st.download_button(
        "📸 Download PNG",
        data=buf.getvalue(),
        file_name="Port_SaaS.png",
        mime="image/png",
    )

def export_pdf():
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("<b>DAP ATLAS — Port SaaS Report</b>", styles["Title"]),
        Spacer(1, 12),
        Paragraph(f"<b>AOI:</b> {AOI_ID}", styles["Normal"]),
        Paragraph(f"<b>Generated:</b> {NOW}", styles["Normal"]),
        Spacer(1, 12),
        Paragraph("<b>Key Findings:</b>", styles["Heading2"]),
        Paragraph("Vehicle estimate derived by AI with local sampling supervision.", styles["Normal"]),
        Paragraph("Two sectors above 85% occupancy (attention threshold).", styles["Normal"]),
        Paragraph("+7% weekly trend in yard stock (last 14 days).", styles["Normal"]),
        Paragraph("Processing time: 10 s (no human intervention).", styles["Normal"]),
    ]
    doc.build(story)
    st.download_button(
        "📄 Download PDF",
        data=buf.getvalue(),
        file_name="Port_SaaS_Report.pdf",
        mime="application/pdf",
    )

colA, colB = st.columns(2)
with colA:
    export_png()
with colB:
    export_pdf()

st.caption("© 2025 MAVIPE Sistemas Espaciais — Universal Streamlit Version")

