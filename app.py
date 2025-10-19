# ================== DAP ATLAS — Port Yard Counting SaaS ==================
from datetime import datetime
from base64 import b64encode
from pathlib import Path
import streamlit.components.v1 as components

# ===== Theme
PRIMARY   = "#00E3A5"
ACCENT    = "#34d399"
BG_DARK   = "#0b1221"
CARD_DARK = "#10182b"
TEXT      = "#E6EEFC"
MUTED     = "#9fb0c9"
BORDER    = "rgba(255,255,255,.12)"

# ===== Optional assets
map_img_uri = ""
pmap = Path("yard_map.png")
if pmap.exists() and pmap.stat().st_size > 0:
    map_img_uri = "data:image/png;base64," + b64encode(pmap.read_bytes()).decode("ascii")

logo_uri = ""
plogo = Path("dapatlas_whitebg.png")
if plogo.exists() and plogo.stat().st_size > 0:
    logo_uri = "data:image/png;base64," + b64encode(plogo.read_bytes()).decode("ascii")

# ===== Data (edit freely)
AOI_ID        = "AOI CN-LN-DAL-PORT-2025-01"
COLLECTION    = "2025-07-01 12:31 UTC"
SOURCE        = "BlackSky Global-16 • 30 cm"
AREA_KM2      = "0.24 km²"
RESOLUTION    = "30 cm"
PROCESS_TIME  = "10 s"
CONFIDENCE    = 95
VEHICLES_EST  = "897 ± 10%"

SECTORS = [
    {"id":"A1","vehicles": 352,"occup":"88%","status":"High","note":"Close to threshold"},
    {"id":"B3","vehicles": 298,"occup":"83%","status":"Medium","note":"Normal dispersion"},
    {"id":"C2","vehicles": 189,"occup":"74%","status":"Medium","note":"Slight shadows"},
    {"id":"D4","vehicles": 58 ,"occup":"41%","status":"Low","note":"Partial occlusion by ship"},
]

TIMELINE = [
    {"t":"+00:00","ev":"Image acquired (nadir ~15°)."},
    {"t":"+00:06","ev":"AI inference complete — count & QA checks."},
    {"t":"+00:08","ev":"Sectors consolidated; anomalies flagged (A1)."},
    {"t":"+00:10","ev":"Report shared with Port Ops (API webhook)."},
]

FINDINGS = [
    "Automatic vehicle yard counting with local sampling supervision.",
    "Two sectors above 85% average occupancy (attention threshold).",
    "Week-over-week trend: +7% in stock (last 14 days).",
    "Full pipeline under 10 seconds — no human intervention.",
]

html = f"""
<!doctype html>
<html><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<style>
:root {{
  --bg:{BG_DARK}; --card:{CARD_DARK}; --text:{TEXT}; --muted:{MUTED};
  --border:{BORDER}; --primary:{PRIMARY}; --accent:{ACCENT};
}}
*{{box-sizing:border-box}}
html,body{{height:100%;margin:0;background:var(--bg);color:var(--text);
  font-family: Inter, Roboto, Segoe UI, system-ui, -apple-system, Arial, sans-serif}}

/* Layout */
.stage{{min-height:100vh;display:flex;gap:18px;align-items:stretch;justify-content:center;padding:28px}}
.mapwrap{{flex:1 1 60%;border-radius:18px;overflow:hidden;border:1px solid var(--border);
  background:linear-gradient(180deg, rgba(255,255,255,.03), rgba(255,255,255,.02)),
             radial-gradient(900px 600px at 30% 40%, rgba(255,255,255,.04), transparent 60%),
             #0a111f; box-shadow:0 18px 44px rgba(0,0,0,.55); position:relative}}
.mapimg{{position:absolute; inset:0; width:100%; height:100%; object-fit:cover; opacity:.9}}
.overlay{{position:absolute; left:16px; top:16px; background:#0f172a; color:#dfe7ff; font-weight:800;
  padding:8px 12px; border-radius:10px; border:1px solid var(--border); box-shadow:0 8px 24px rgba(0,0,0,.35); letter-spacing:.2px}}
.legend{{position:absolute; left:16px; bottom:16px; background:rgba(0,0,0,.45); backdrop-filter: blur(6px) saturate(140%);
  border:1px solid var(--border); color:#dfe7ff; padding:10px 12px; border-radius:12px; font-size:.9rem; line-height:1.2}}
.legend .row{{display:flex; align-items:center; gap:8px; margin:6px 0}}
.legend .k{{width:14px; height:14px; border-radius:3px; background:#7ade7a; display:inline-block; box-shadow:0 0 0 2px rgba(0,0,0,.25)}}
.legend .k.warn{{background:#f7b267}} .legend .k.low{{background:#5ea8ff}}
.scale{{position:absolute; left:16px; bottom:16px; color:#cbd6f2; font-size:.85rem; letter-spacing:.3px}}

.panel{{flex:0 0 560px; display:flex; flex-direction:column; gap:12px; padding:16px;
  border:1px solid var(--border); border-radius:18px; background:var(--card);
  box-shadow:0 18px 44px rgba(0,0,0,.55); overflow:hidden}}
.header{{display:flex; align-items:center; justify-content:space-between; gap:16px}}
.brand{{display:flex; align-items:center; gap:14px}}
.logo{{width:74px;height:74px; border-radius:16px; overflow:hidden; background:#fff;
  border:1px solid var(--border); display:flex; align-items:center; justify-content:center}}
.logo img{{width:100%; height:100%; object-fit:contain; display:block}}
.ttl{{font-weight:900; font-size:1.05rem; letter-spacing:.2px}}
.sub{{color:var(--muted); font-size:.85rem; margin-top:2px}}
.badge{{background:rgba(0,227,165,.12); color:var(--primary); border:1px solid rgba(0,227,165,.25);
  padding:6px 10px; border-radius:999px; font-weight:800; font-size:.85rem; white-space:nowrap}}

.metrics{{display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px}}
.metric{{background:rgba(255,255,255,.04); border:1px solid var(--border); border-radius:14px; padding:12px}}
.metric .k{{font-size:1.1rem; font-weight:800}}
.metric .l{{font-size:.85rem; color:var(--muted)}}

.tabs{{margin-top:4px}}
.tabs input{{display:none}}
.tabs label{{
  display:inline-block; padding:8px 12px; margin-right:8px; border:1px solid var(--border);
  border-bottom:none; border-top-left-radius:10px; border-top-right-radius:10px;
  color:var(--muted); background:rgba(255,255,255,.02); cursor:pointer; font-weight:800; font-size:.9rem;
  transition:transform .12s ease;}}
.tabs label:hover{{transform:translateY(-1px)}}
.tabs input:checked + label{{color:#08121f; background:var(--primary); border-color:var(--primary)}}
.tabbox{{border:1px solid var(--border); border-radius:0 12px 12px 12px; padding:12px; margin-top:-1px}}

ul.bullets{{margin:6px 0 0 0; padding-left:1.2rem}} ul.bullets li{{margin:8px 0}}
.tbl{{width:100%; border-collapse:collapse}} .tbl th, .tbl td{{padding:9px 6px; border-bottom:1px solid var(--border); text-align:left; font-size:.95rem}}
.tbl th{{color:var(--muted); font-weight:700}}

.actions{{display:flex; gap:8px; flex-wrap:wrap; margin-top:6px}}
.btn{{display:inline-flex; align-items:center; gap:8px; padding:9px 12px; border-radius:10px; font-weight:800; font-size:.9rem; cursor:pointer; text-decoration:none}}
.btn.ghost{{background:rgba(255,255,255,.04); color:#E6EEFC; border:1px solid var(--border)}}
.footer{{margin-top:auto; display:flex; justify-content:space-between; align-items:center; gap:8px; flex-wrap:wrap}}
.small{{font-size:.85rem; color:{MUTED}}}
.hint{{font-size:.8rem; color:{MUTED}}}
.btnbar{{display:flex; gap:8px; flex-wrap:wrap}}

.warn{{display:none; background:#222; color:#E6EEFC; border-left:4px solid #f59e0b; padding:8px 10px; border-radius:8px; margin-top:6px; font-size:.9rem}}
</style>
</head>
<body>
  <div class="stage">
    <div class="mapwrap">
      {"<img class='mapimg' src='"+map_img_uri+"' alt='map'/>" if map_img_uri else ""}
      <div class="overlay">AI Vehicle Yard Counting</div>
      <div class="legend">
        <div class="row"><span class="k"></span> Sector — High Occupancy</div>
        <div class="row"><span class="k warn"></span> Sector — Medium</div>
        <div class="row"><span class="k low"></span> Sector — Low</div>
      </div>
      <div class="scale">0 — 100 — 200 m</div>
    </div>

    <div class="panel" id="panel">
      <div class="header">
        <div class="brand">
          <div class="logo">{("<img src='"+logo_uri+"' alt='DAP ATLAS'/>" if logo_uri else "<div style='color:#000;font-weight:900'>DA</div>")}</div>
          <div>
            <div class="ttl">DAP ATLAS — Port SaaS</div>
            <div class="sub">Automatic Vehicle Yard Counting</div>
          </div>
        </div>
        <div class="badge">{AOI_ID} • Live 24/7</div>
      </div>

      <!-- KPIs -->
      <div class="metrics">
        <div class="metric"><div class="k">{VEHICLES_EST}</div><div class="l">Vehicles (estimate)</div></div>
        <div class="metric"><div class="k">{CONFIDENCE}%</div><div class="l">Confidence</div></div>
        <div class="metric"><div class="k">{PROCESS_TIME}</div><div class="l">Processing Time</div></div>
        <div class="metric"><div class="k">{AREA_KM2}</div><div class="l">Analyzed Area</div></div>
        <div class="metric"><div class="k">{RESOLUTION}</div><div class="l">Resolution</div></div>
        <div class="metric"><div class="k">{SOURCE}</div><div class="l">Source</div></div>
      </div>

      <!-- Tabs -->
      <div class="tabs">
        <input type="radio" name="t" id="t1" checked><label for="t1">Findings</label>
        <input type="radio" name="t" id="t2"><label for="t2">Sectors</label>
        <input type="radio" name="t" id="t3"><label for="t3">Timeline</label>
        <input type="radio" name="t" id="t4"><label for="t4">Metadata</label>

        <div class="tabbox" id="c1">
          <ul class="bullets">
            {"".join(f"<li>{x}</li>" for x in FINDINGS)}
          </ul>
        </div>

        <div class="tabbox" id="c2" style="display:none">
          <table class="tbl">
            <thead><tr><th>Sector</th><th>Vehicles</th><th>Occupancy</th><th>Status</th><th>Notes</th></tr></thead>
            <tbody>
              {"".join(f"<tr><td>{r['id']}</td><td>{r['vehicles']}</td><td>{r['occup']}</td><td>{r['status']}</td><td>{r['note']}</td></tr>" for r in SECTORS)}
            </tbody>
          </table>
          <div class="actions">
            <a class="btn ghost" href="#" onclick="notify('ok','Sector A1 priority check queued');return false;">Queue QA — A1</a>
            <a class="btn ghost" href="#" onclick="notify('ok','Webhook sent to Port Ops');return false;">Send Webhook</a>
          </div>
        </div>

        <div class="tabbox" id="c3" style="display:none">
          <ul class="bullets">
            {"".join(f"<li><b>{r['t']}</b> — {r['ev']}</li>" for r in TIMELINE)}
          </ul>
        </div>

        <div class="tabbox" id="c4" style="display:none">
          <table class="tbl">
            <tr><th>Collection</th><td>{COLLECTION}</td></tr>
            <tr><th>AOI</th><td>{AOI_ID}</td></tr>
            <tr><th>Source</th><td>{SOURCE}</td></tr>
            <tr><th>Area</th><td>{AREA_KM2}</td></tr>
            <tr><th>Resolution</th><td>{RESOLUTION}</td></tr>
          </table>
        </div>
      </div>

      <div class="footer">
        <div class="small">© {datetime.now().year} MAVIPE Space Systems</div>
        <div class="btnbar">
          <a class="btn ghost" href="#" onclick="exportPNG();return false;">Export PNG</a>
          <a class="btn ghost" href="#" onclick="exportSVG();return false;">Export SVG</a>
          <a class="btn ghost" href="#" onclick="exportPDF();return false;">Export PDF</a>
        </div>
        <div class="hint">Shortcuts: <b>G</b> PNG • <b>S</b> SVG • <b>P</b> PDF</div>
      </div>

      <div id="cdnWarn" class="warn">⚠️ Export libraries failed to load (network blocked). Try another network or VPN.</div>
    </div>
  </div>

  <!-- CDN failure detector -->
  <script>
    window.addEventListener('error', function(e){{
      if ((e.target||{{}}).tagName==='SCRIPT') {{
        var el=document.getElementById('cdnWarn'); if(el) el.style.display='block';
      }}
    }}, true);
  </script>
  <!-- Export libs -->
  <script src="https://cdn.jsdelivr.net/npm/dom-to-image-more@2.8.0/dist/dom-to-image-more.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/jspdf@2.5.1/dist/jspdf.umd.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/svg2pdf.js@2.2.3/dist/svg2pdf.umd.min.js"></script>

  <script>
    // Tabs
    const c1=document.getElementById('c1'), c2=document.getElementById('c2'), c3=document.getElementById('c3'), c4=document.getElementById('c4');
    document.getElementById('t1').onchange=()=>{{c1.style.display='block'; c2.style.display='none'; c3.style.display='none'; c4.style.display='none';}};
    document.getElementById('t2').onchange=()=>{{c1.style.display='none'; c2.style.display='block'; c3.style.display='none'; c4.style.display='none';}};
    document.getElementById('t3').onchange=()=>{{c1.style.display='none'; c2.style.display='none'; c3.style.display='block'; c4.style.display='none';}};
    document.getElementById('t4').onchange=()=>{{c1.style.display='none'; c2.style.display='none'; c3.style.display='none'; c4.style.display='block';}};

    // Toast
    function notify(kind,msg){{
      const n=document.createElement('div');
      n.textContent=msg;
      n.style.cssText='position:fixed;right:24px;bottom:24px;background:#10182b;color:#E6EEFC;border:1px solid rgba(255,255,255,.12);padding:10px 12px;border-radius:10px;box-shadow:0 10px 24px rgba(0,0,0,.4);font-weight:700;z-index:9999';
      document.body.appendChild(n);
      setTimeout(()=>n.remove(), 2200);
    }}

    // Export
    const PANEL = document.getElementById('panel');
    function trigger(url,filename){{
      try{{ const a=document.createElement('a'); a.href=url; a.download=filename; a.rel='noopener'; a.target='_blank'; document.body.appendChild(a); a.click(); a.remove(); }}
      catch(e){{ window.open(url,'_blank','noopener'); }}
    }}
    async function exportPNG(){{
      try {{
        const dataUrl=await domtoimage.toPng(PANEL,{{bgcolor:'{CARD_DARK}',quality:1}});
        trigger(dataUrl,'PORT_SaaS.png');
      }} catch(e) {{ notify('err','PNG export failed'); }}
    }}
    async function exportSVG(){{
      try {{
        const dataUrl = await domtoimage.toSvg(PANEL, {{ bgcolor: '{CARD_DARK}', quality: 1 }});
        trigger(dataUrl,'PORT_SaaS.svg');
      }} catch(e) {{ notify('err','SVG export failed'); }}
    }}
    async function exportPDF(){{
      try {{
        const svgUrl  = await domtoimage.toSvg(PANEL, {{ bgcolor: '{CARD_DARK}', quality: 1 }});
        const svgText = await (await fetch(svgUrl)).text();
        const {{ jsPDF }} = window.jspdf; const pdf = new jsPDF({{ unit:'pt', format:'a4', orientation:'p' }});
        const parser = new DOMParser(); const svgDoc = parser.parseFromString(svgText,'image/svg+xml'); const svgEl = svgDoc.documentElement;
        const width  = parseFloat(svgEl.getAttribute('width'))  || PANEL.offsetWidth;
        const height = parseFloat(svgEl.getAttribute('height')) || PANEL.offsetHeight;
        const pageW = pdf.internal.pageSize.getWidth(), pageH = pdf.internal.pageSize.getHeight();
        const scale = Math.min(pageW/width, pageH/height);
        window.svg2pdf(svgEl, pdf, {{ x:(pageW-width*scale)/2, y:(pageH-height*scale)/2, scale }});
        const blob = pdf.output('blob'); const url = URL.createObjectURL(blob); trigger(url,'PORT_SaaS.pdf');
      }} catch(e) {{ notify('err','PDF export failed'); }}
    }}

    // Shortcuts
    document.addEventListener('keydown', e=>{{
      if(e.key==='g'||e.key==='G') exportPNG();
      if(e.key==='s'||e.key==='S') exportSVG();
      if(e.key==='p'||e.key==='P') exportPDF();
    }});
  </script>
</body></html>
"""

components.html(html, height=1100, scrolling=True)

