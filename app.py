# app_offline.py — DAP ATLAS • Port SaaS (OFFLINE)
# - Sem dependência de CDN (Chart, export implementados à mão)
# - Export: PNG (G), SVG (S), Print/PDF (P)

from datetime import datetime
import streamlit as st

st.set_page_config(page_title="DAP ATLAS — Port SaaS (Offline)", page_icon="🛰️", layout="wide")

AOI_ID = "AOI CN-LN-DAL-PORT-2025-01"
NOW = datetime.now().strftime("%d/%m %H:%M")

# Série temporal (14 dias)
labels = ['Oct-05','Oct-06','Oct-07','Oct-08','Oct-09','Oct-10','Oct-11','Oct-12','Oct-13','Oct-14','Oct-15','Oct-16','Oct-17','Oct-18']
values = [812, 818, 827, 835, 842, 851, 860, 869, 874, 881, 888, 893, 900, 907]

# Embala arrays em JS
labels_js = "[" + ",".join(f"'{x}'" for x in labels) + "]"
values_js = "[" + ",".join(str(v) for v in values) + "]"

html = f"""
<!doctype html>
<html><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>DAP ATLAS — Port SaaS (Offline)</title>
<style>
:root {{
  --bg:#0b1221; --card:#10182b; --text:#E6EEFC; --muted:#9fb0c9; --border:rgba(255,255,255,.12);
  --primary:#00E3A5;
}}
*{{box-sizing:border-box}}
html,body{{margin:0;height:100%;background:var(--bg);color:var(--text);
  font-family:Inter,Roboto,Segoe UI,Arial,sans-serif}}
.stage{{min-height:100vh;display:flex;justify-content:center;align-items:stretch;gap:18px;padding:24px}}
.panel{{flex:0 0 560px;background:var(--card);border:1px solid var(--border);border-radius:18px;padding:16px;
  box-shadow:0 18px 44px rgba(0,0,0,.55);display:flex;flex-direction:column}}
.header{{display:flex;justify-content:space-between;align-items:center}}
.badge{{background:rgba(0,227,165,.12);color:var(--primary);border:1px solid rgba(0,227,165,.25);
  padding:6px 10px;border-radius:999px;font-weight:800;font-size:.85rem}}
.kpis{{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-top:12px}}
.kpi{{background:rgba(255,255,255,.04);border:1px solid var(--border);border-radius:14px;padding:12px}}
.kpi .k{{font-weight:800}} .kpi .l{{font-size:.85rem;color:var(--muted)}}
.box{{margin-top:12px;border:1px solid var(--border);border-radius:12px;padding:12px}}
ul{{margin:0;padding-left:1.1rem}} li{{margin:8px 0}}
.hint{{font-size:.8rem;color:var(--muted);margin-top:auto;text-align:right}}
.controls{{display:flex;gap:8px;flex-wrap:wrap;margin-top:8px}}
.btn{{display:inline-flex;align-items:center;gap:8px;padding:9px 12px;border-radius:10px;font-weight:800;font-size:.9rem;
  cursor:pointer;text-decoration:none;border:1px solid var(--border);background:rgba(255,255,255,.04);color:var(--text)}}
.btn.primary{{background:var(--primary);color:#08121f;border-color:var(--primary)}}

/* print-friendly */
@media print {{
  body {{ background:white; color:black }}
  .panel {{ border:none; box-shadow:none; width:100%; }}
  .btn, .hint {{ display:none }}
}}
</style>
</head>
<body>
  <div class="stage">
    <div class="panel" id="panel">
      <div class="header">
        <div>
          <div style="font-weight:900">DAP ATLAS — Port SaaS (Offline)</div>
          <div style="color:var(--muted);font-size:.9rem">Automatic Vehicle Yard Counting</div>
        </div>
        <div class="badge">{AOI_ID} • Live 24/7</div>
      </div>

      <div class="kpis">
        <div class="kpi"><div class="k">897 ±10%</div><div class="l">Vehicles (estimate)</div></div>
        <div class="kpi"><div class="k">95%</div><div class="l">Confidence</div></div>
        <div class="kpi"><div class="k">10 s</div><div class="l">Processing Time</div></div>
        <div class="kpi"><div class="k">0.24 km²</div><div class="l">Analyzed Area</div></div>
        <div class="kpi"><div class="k">30 cm</div><div class="l">Resolution</div></div>
        <div class="kpi"><div class="k">BlackSky Global-16</div><div class="l">Source</div></div>
      </div>

      <div class="box">
        <div style="font-weight:800;margin-bottom:6px">Key Findings</div>
        <ul>
          <li>Vehicle estimate derived by AI with local sampling supervision.</li>
          <li>Two sectors above 85% occupancy (attention threshold).</li>
          <li>+7% weekly trend in yard stock (last 14 days).</li>
          <li>Processing time: 10 s (no human intervention).</li>
        </ul>
      </div>

      <div class="box">
        <div style="font-weight:800;margin-bottom:8px">Vehicle Trend — Last 14 Days</div>
        <!-- Chart container (SVG) -->
        <div id="chartBox" style="width:100%;height:160px;border:1px solid var(--border);border-radius:10px;padding:6px"></div>
        <div class="controls">
          <button class="btn" onclick="savePNG()">Export PNG (G)</button>
          <button class="btn" onclick="saveSVG()">Export SVG (S)</button>
          <button class="btn" onclick="window.print()">Print / PDF (P)</button>
        </div>
      </div>

      <div class="hint">Shortcuts: G (PNG) • S (SVG) • P (Print/PDF)<br/>Generated {NOW}</div>
    </div>
  </div>

<script>
/* ===== Mini chart (pure SVG) ===== */
const labels = {labels_js};
const values = {values_js};
(function renderSparkline(){{
  const box = document.getElementById('chartBox');
  const W = box.clientWidth - 12, H = box.clientHeight - 12; // inner area
  const min = Math.min(...values), max = Math.max(...values);
  const padL=32, padR=12, padT=10, padB=22;
  const w = Math.max(10, W - padL - padR), h = Math.max(10, H - padT - padB);
  const n = values.length;
  const x = i => padL + (w * i)/(n-1);
  const y = v => padT + h - ( (v - min) / (max - min || 1) ) * h;

  let d = "";
  for (let i=0;i<n;i++) {{
    const X = x(i), Y = y(values[i]);
    d += (i===0?`M ${X} ${Y}`:` L ${X} ${Y}`);
  }}

  // area fill
  let dFill = d + ` L ${x(n-1)} ${padT+h} L ${x(0)} ${padT+h} Z`;

  const svg = `
  <svg width="100%" height="100%" viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" style="background:transparent">
    <defs>
      <linearGradient id="g1" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#00E3A5" stop-opacity="0.35"/>
        <stop offset="100%" stop-color="#00E3A5" stop-opacity="0.05"/>
      </linearGradient>
    </defs>

    <!-- grid -->
    <g stroke="rgba(255,255,255,.08)" stroke-width="1">
      <line x1="${padL}" y1="${padT}" x2="${padL}" y2="${padT+h}"/>
      <line x1="${padL}" y1="${padT+h}" x2="${padL+w}" y2="${padT+h}"/>
    </g>

    <!-- area -->
    <path d="${dFill}" fill="url(#g1)" stroke="none"></path>
    <!-- line -->
    <path d="${d}" fill="none" stroke="#00E3A5" stroke-width="2"></path>

    <!-- last point -->
    <circle cx="${x(n-1)}" cy="${y(values[n-1])}" r="3" fill="#00E3A5"/>

    <!-- axes labels -->
    <g font-size="10" fill="#9fb0c9">
      <text x="${padL}" y="${padT-2}" >Max ${max}</text>
      <text x="${padL}" y="${padT+h+14}" >Min ${min}</text>
      <text x="${padL+w-40}" y="${padT+h+14}" >${labels[n-1]}</text>
    </g>
  </svg>`;
  box.innerHTML = svg;
}})();

/* ===== Export (offline): foreignObject → Canvas → PNG / SVG ===== */

function inlinePanelSVG() {{
  // Serializa estilos essenciais + painel dentro de foreignObject (funciona offline)
  const panel = document.getElementById('panel');
  const clone = panel.cloneNode(true);
  // largura alvo
  const W = panel.offsetWidth, H = panel.offsetHeight;

  // CSS inline (espelha as variáveis)
  const css = `
    :root {{
      --bg:#0b1221; --card:#10182b; --text:#E6EEFC; --muted:#9fb0c9; --border:rgba(255,255,255,.12); --primary:#00E3A5;
    }}
    *{{box-sizing:border-box}}
    body{{margin:0;background:var(--card);color:var(--text);font-family:Inter,Roboto,Arial,sans-serif}}
  `;

  const html = `
    <svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}">
      <foreignObject width="100%" height="100%">
        <div xmlns="http://www.w3.org/1999/xhtml" style="width:${W}px;height:${H}px;background:#10182b;">
          <style>${css}</style>
          ${clone.outerHTML}
        </div>
      </foreignObject>
    </svg>`;
  return html;
}

function saveBlob(blob, filename){{
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = filename; document.body.appendChild(a); a.click(); a.remove();
  setTimeout(()=>URL.revokeObjectURL(url), 0);
}}

function saveSVG(){{
  const svgText = inlinePanelSVG();
  const blob = new Blob([svgText], {{type:'image/svg+xml'}});
  saveBlob(blob, 'PORT_SaaS.svg');
}}

function savePNG(){{
  const svgText = inlinePanelSVG();
  const svg = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svgText);
  const img = new Image();
  img.onload = function(){{
    const W = this.naturalWidth, H = this.naturalHeight;
    const canvas = document.createElement('canvas'); canvas.width = W; canvas.height = H;
    const ctx = canvas.getContext('2d');
    // fundo
    ctx.fillStyle = '#10182b'; ctx.fillRect(0,0,W,H);
    ctx.drawImage(this, 0, 0);
    canvas.toBlob(b => saveBlob(b, 'PORT_SaaS.png'));
  }};
  img.onerror = function(){{ alert('PNG export failed (foreignObject not supported by this browser).'); }};
  img.src = svg;
}}

// atalhos
document.addEventListener('keydown', e => {{
  if(e.key==='g'||e.key==='G') savePNG();
  if(e.key==='s'||e.key==='S') saveSVG();
  if(e.key==='p'||e.key==='P') window.print();
}});
</script>

</body></html>
"""

st.components.v1.html(html, height=880, scrolling=False)
