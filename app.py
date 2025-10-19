# DAP ATLAS — Port SaaS (robust version)
# Works with Streamlit + offline fallback
from datetime import datetime
import streamlit as st

st.set_page_config(page_title="DAP ATLAS — Port SaaS", page_icon="🛰️", layout="wide")

AOI_ID = "AOI CN-LN-DAL-PORT-2025-01"
NOW = datetime.now().strftime("%d/%m %H:%M")

html = f"""
<!doctype html>
<html><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Port SaaS — DAP ATLAS</title>
<style>
:root {{
  --bg:#0b1221; --card:#10182b; --text:#E6EEFC; --muted:#9fb0c9;
  --border:rgba(255,255,255,.12); --primary:#00E3A5;
}}
*{{box-sizing:border-box}}
body,html{{margin:0;padding:0;height:100%;background:var(--bg);color:var(--text);
  font-family:Inter,Roboto,Segoe UI,Arial,sans-serif}}
.stage{{display:flex;justify-content:center;align-items:stretch;min-height:100vh;
  padding:24px;gap:18px}}
.panel{{flex:0 0 560px;background:var(--card);border:1px solid var(--border);
  border-radius:18px;padding:16px;box-shadow:0 18px 44px rgba(0,0,0,.55);
  display:flex;flex-direction:column}}
.header{{display:flex;justify-content:space-between;align-items:center}}
.badge{{background:rgba(0,227,165,.12);color:var(--primary);
  border:1px solid rgba(0,227,165,.25);padding:6px 10px;
  border-radius:999px;font-weight:800;font-size:.85rem}}
.kpis{{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-top:12px}}
.kpi{{background:rgba(255,255,255,.04);border:1px solid var(--border);
  border-radius:14px;padding:12px}}
.kpi .k{{font-weight:800}} .kpi .l{{font-size:.85rem;color:var(--muted)}}
.box{{margin-top:12px;border:1px solid var(--border);
  border-radius:12px;padding:12px}}
ul{{margin:0;padding-left:1.1rem}} li{{margin:8px 0}}
.hint{{font-size:.8rem;color:var(--muted);margin-top:auto;text-align:right}}
.alert{{background:#222;color:#E6EEFC;padding:8px 10px;border-left:4px solid #f87171;
  font-size:.9rem;margin-bottom:10px;border-radius:8px}}
</style></head>
<body>
  <div class="stage">
    <div class="panel" id="panel">
      <div class="header">
        <div>
          <div style="font-weight:900">DAP ATLAS — Port SaaS</div>
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

      <div class="box" id="chartWrap">
        <div style="font-weight:800;margin-bottom:6px">Vehicle Trend — Last 14 Days</div>
        <canvas id="vehChart" height="130"></canvas>
      </div>

      <div class="hint">Shortcuts: S (SVG) • P (PDF) • G (PNG)<br>Generated {NOW}</div>
    </div>
  </div>

  <!-- Robust Script Loading -->
  <script>
    function safeLoad(url, cb){{
      var s=document.createElement('script'); s.src=url; s.onload=cb;
      s.onerror=function(){{console.warn('⚠️ CDN failed:',url);}};
      document.head.appendChild(s);
    }}
    safeLoad("https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js", function(){{
      try {{
        const ctx=document.getElementById('vehChart').getContext('2d');
        const chart=new Chart(ctx, {{
          type:'line',
          data:{{
            labels:['Oct-05','Oct-06','Oct-07','Oct-08','Oct-09','Oct-10','Oct-11','Oct-12','Oct-13','Oct-14','Oct-15','Oct-16','Oct-17','Oct-18'],
            datasets:[{{data:[812,818,827,835,842,851,860,869,874,881,888,893,900,907],
              borderColor:'#00E3A5',backgroundColor:'rgba(0,227,165,.2)',tension:0.25,fill:true}}]
          }},
          options:{{
            plugins:{{legend:{{display:false}}}},
            scales:{{
              x:{{ticks:{{color:'#9fb0c9'}}}},
              y:{{ticks:{{color:'#9fb0c9'}}}}
            }}
          }}
        }});
      }} catch(e) {{
        document.getElementById('chartWrap').innerHTML="<div class='alert'>⚠️ Chart library failed to load — fallback mode.</div>";
      }}
    }});

    // Export helpers (SVG/PNG/PDF)
    safeLoad("https://cdn.jsdelivr.net/npm/dom-to-image-more@2.8.0/dist/dom-to-image-more.min.js");
    safeLoad("https://cdn.jsdelivr.net/npm/jspdf@2.5.1/dist/jspdf.umd.min.js");
    safeLoad("https://cdn.jsdelivr.net/npm/svg2pdf.js@2.2.3/dist/svg2pdf.umd.min.js");

    async function exportPNG(){{
      try {{
        const dataUrl=await domtoimage.toPng(document.getElementById('panel'),{{bgcolor:'#10182b'}});
        const a=document.createElement('a'); a.href=dataUrl; a.download='PORT_SaaS.png'; a.click();
      }} catch(e){{alert('PNG export failed');}}
    }}
    async function exportPDF(){{
      try {{
        const svgUrl=await domtoimage.toSvg(document.getElementById('panel'),{{bgcolor:'#10182b'}});
        const text=await (await fetch(svgUrl)).text();
        const {{ jsPDF }} = window.jspdf; const pdf=new jsPDF({{unit:'pt',format:'a4'}});
        const svgDoc=new DOMParser().parseFromString(text,'image/svg+xml');
        const svgEl=svgDoc.documentElement;
        window.svg2pdf(svgEl,pdf,{{x:20,y:20,scale:0.8}});
        pdf.save('PORT_SaaS.pdf');
      }} catch(e){{alert('PDF export failed');}}
    }}
    document.addEventListener('keydown', e=>{{
      if(e.key==='p'||e.key==='P') exportPDF();
      if(e.key==='g'||e.key==='G') exportPNG();
    }});
  </script>
</body></html>
"""

st.components.v1.html(html, height=850, scrolling=False)
