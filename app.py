# ================== SITREP — Dark Ships Panel (with PNG/SVG/PDF export) ==================
from datetime import datetime
from base64 import b64encode
from pathlib import Path
import streamlit.components.v1 as components

PRIMARY   = "#00E3A5"
ACCENT    = "#34d399"
BG_DARK   = "#0b1221"
CARD_DARK = "#10182b"
TEXT      = "#E6EEFC"
MUTED     = "#9fb0c9"
BORDER    = "rgba(255,255,255,.12)"

# (optional) map image
map_img_uri = ""
pmap = Path("darkships_map.png")  # replace with your file
if pmap.exists() and pmap.stat().st_size > 0:
    map_img_uri = "data:image/png;base64," + b64encode(pmap.read_bytes()).decode("ascii")

# logo
logo_uri = ""
plogo = Path("dapatlas_whitebg.png")
if plogo.exists() and plogo.stat().st_size > 0:
    logo_uri = "data:image/png;base64," + b64encode(plogo.read_bytes()).decode("ascii")

# Main target data
AOI_ID         = "AOI BR-PA-2025-01"
TARGET_ID      = "UNK-09F4"
LAST_CONTACT   = "07/06/2025 09:25Z"
POS_LATLON     = "00°52.1'S, 046°36.9'W"
HEADING        = "250°"
SPEED          = "11.2 kn"
CPA            = "2.1 NM"
ETA_BORDER     = "55 min"
ETA_ANCHORAGE  = "108 min"
RISK_SCORE     = 82    # 0–100
CONFIDENCE     = 95    # %
SEA_STATE      = "3"
CONDITIONS     = "Night • Low Clouds"
SENSOR         = "SAR (ScanSAR) + AIS + RF"
PROVIDER       = "BlackSky • RF Fusion"
NOW_LOCAL      = datetime.now().strftime("%d/%m %H:%M")

# Nearby targets
nearby = [
    {"id":"MOO-211","type":"Moored","ais":"on","spd":"0.2","hdg":"—","rng":"1.3 NM"},
    {"id":"UNK-9AB","type":"Moving","ais":"off","spd":"9.6","hdg":"243°","rng":"3.8 NM"},
    {"id":"VES-581","type":"Moving","ais":"on","spd":"12.1","hdg":"247°","rng":"4.5 NM"},
]

# Upcoming passes
passes = [
    {"src":"SAR","t":"+ 42 min","inc":"34°","res":"0.5 m"},
    {"src":"Optical","t":"+ 2h 15m","inc":"11°","res":"0.3 m"},
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

.stage{{min-height:100vh;display:flex;gap:18px;align-items:stretch;justify-content:center;padding:28px}}
.mapwrap{{flex:1 1 60%;border-radius:18px;overflow:hidden;border:1px solid var(--border);
  background:linear-gradient(180deg, rgba(255,255,255,.03), rgba(255,255,255,.02)),
             radial-gradient(900px 600px at 30% 40%, rgba(255,255,255,.04), transparent 60%),
             #0a111f; box-shadow:0 18px 44px rgba(0,0,0,.55); position:relative}}
.mapimg{{position:absolute; inset:0; width:100%; height:100%; object-fit:cover; opacity:.9}}
.alert{{position:absolute; left:16px; top:16px; background:#ff4242; color:#fff; font-weight:800;
  padding:8px 12px; border-radius:10px; box-shadow:0 8px 24px rgba(0,0,0,.35); letter-spacing:.2px}}
.legend{{position:absolute; left:16px; bottom:16px; background:rgba(0,0,0,.45); backdrop-filter: blur(6px) saturate(140%);
  border:1px solid var(--border); color:#dfe7ff; padding:10px 12px; border-radius:12px; font-size:.9rem; line-height:1.2}}
.legend .row{{display:flex; align-items:center; gap:8px; margin:6px 0}}
.legend .k{{width:14px;height:14px;border-radius:50%; display:inline-block; background:#7ade7a; box-shadow:0 0 0 2px rgba(0,0,0,.25)}}
.legend .k.square{{border-radius:3px; background:#f7b267}}
.legend .k.border{{background:transparent; border:2px dashed #ffd166}}
.scale{{position:absolute; left:16px; bottom:16px; color:#cbd6f2; font-size:.85rem; letter-spacing:.3px}}

.panel{{flex:0 0 540px; display:flex; flex-direction:column; gap:12px; padding:16px;
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

.hr{{height:1px; background:var(--border); margin:4px 0}}
.toprow{{display:grid; grid-template-columns:1fr auto; gap:10px; align-items:center}}
.card{{background:rgba(255,255,255,.04); border:1px solid var(--border); border-radius:14px; padding:12px}}
.card h4{{margin:0 0 6px 0; font-size:.92rem; color:#dfe7ff; letter-spacing:.3px}}
.kv{{display:flex; gap:8px; flex-wrap:wrap; color:#E6EEFC; font-size:.95rem}}
.kv .key{{color:var(--muted)}}

.gaugewrap{{display:flex; gap:10px; align-items:center}}
.gauge{{--v: {RISK_SCORE}; width:82px; height:82px; border-radius:50%;
  background: conic-gradient(#ff5a5a calc(var(--v)*1%), rgba(255,255,255,.10) 0);
  display:grid; place-items:center; border:2px solid rgba(255,255,255,.12); box-shadow:inset 0 0 12px rgba(0,0,0,.35)}}
.gauge span{{font-weight:900; font-size:1.05rem}}
.confbar{{height:10px; border-radius:999px; background:rgba(255,255,255,.08); border:1px solid var(--border); overflow:hidden}}
.confbar > i{{display:block; height:100%; width:{CONFIDENCE}%; background:linear-gradient(90deg, #18d8b6, #00E3A5)}}
.statuschips{{display:flex; gap:8px; flex-wrap:wrap}}
.chip{{display:inline-flex; align-items:center; gap:6px; padding:6px 10px; border-radius:999px; border:1px solid var(--border);
  background:rgba(255,255,255,.04); color:#dfe7ff; font-weight:700; font-size:.8rem}}
.chip svg{{width:14px; height:14px}}

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
.btn.primary{{background:var(--primary); color:#08121f; border:1px solid var(--primary)}}
.btn.ghost{{background:rgba(255,255,255,.04); color:#E6EEFC; border:1px solid var(--border)}}
.btn svg{{width:16px; height:16px}}

.footer{{margin-top:8px; display:flex; justify-content:space-between; align-items:center; gap:8px; flex-wrap:wrap}}
.small{{font-size:.85rem; color:{MUTED}}}
.hint{{font-size:.8rem; color:{MUTED}}}
.btnbar{{display:flex; gap:8px; flex-wrap:wrap}}

@keyframes blink {{ 0%,100%{{opacity:1}} 50%{{opacity:.35}} }}
.alert{{animation:blink 1.8s infinite}}

.warn{{display:none; background:#222; color:#E6EEFC; border-left:4px solid #f59e0b; padding:8px 10px; border-radius:8px; margin-top:6px; font-size:.9rem}}
</style>
</head>
<body>
  <div class="stage">
    <div class="mapwrap">
      {"<img class='mapimg' src='"+map_img_uri+"' alt='map'/>" if map_img_uri else ""}
      <div class="alert">ALERT — Potentially Non-Cooperative Vessel</div>
      <div class="legend">
        <div class="row"><span class="k"></span> Moored</div>
        <div class="row"><span class="k square"></span> Moving (AIS off)</div>
        <div class="row"><span class="k" style="background:#5ea8ff"></span> Moving (AIS on)</div>
        <div class="row"><span class="k border"></span> Maritime Border</div>
      </div>
      <div class="scale">0 — 5 — 10 NM</div>
    </div>

    <div class="panel" id="panel">
      <div class="header">
        <div class="brand">
          <div class="logo">{("<img src='"+logo_uri+"' alt='DAP ATLAS'/>" if logo_uri else "<div style='color:#000;font-weight:900'>DA</div>")}</div>
          <div>
            <div class="ttl">DAP ATLAS — SITREP</div>
            <div class="sub">ISR Platform (C2 Support)</div>
          </div>
        </div>
        <div class="badge">{AOI_ID} • Live 24/7</div>
      </div>

      <div class="toprow">
        <div class="card">
          <h4>Target Summary</h4>
          <div class="kv">
            <div><span class="key">ID:</span> <b>{TARGET_ID}</b></div>
            <div><span class="key">Position:</span> {POS_LATLON}</div>
            <div><span class="key">Last Contact:</span> {LAST_CONTACT}</div>
            <div><span class="key">Source:</span> {SENSOR}</div>
          </div>
          <div class="actions">
            <a class="btn primary" href="#" onclick="notify('task','Patrol assigned');return false;">
              <svg viewBox="0 0 24 24" fill="none"><path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.64 5.64l2.12 2.12M16.24 16.24l2.12 2.12M16.24 7.76l2.12-2.12M5.64 18.36l2.12-2.12" stroke="#08121f" stroke-width="2"/></svg>
              Assign Patrol
            </a>
            <a class="btn ghost" href="#" onclick="notify('mail','MRCC notified');return false;">
              <svg viewBox="0 0 24 24" fill="none"><path d="M4 6h16v12H4z" stroke="#E6EEFC" stroke-width="2"/><path d="M4 7l8 6 8-6" stroke="#E6EEFC" stroke-width="2"/></svg>
              Notify MRCC
            </a>
          </div>
        </div>
        <div class="card">
          <h4>Risk Level</h4>
          <div class="gaugewrap">
            <div class="gauge"><span>{RISK_SCORE}</span></div>
            <div style="flex:1">
              <div style="display:flex;justify-content:space-between;font-weight:800;font-size:.9rem">
                <span>Confidence</span><span>{CONFIDENCE}%</span>
              </div>
              <div class="confbar"><i></i></div>
              <div class="statuschips" style="margin-top:8px">
                <span class="chip">
                  <svg viewBox="0 0 24 24" fill="none"><path d="M12 3l9 7-9 7-9-7 9-7z" stroke="#dfe7ff" stroke-width="1.6"/></svg>
                  AIS: <b>Off</b>
                </span>
                <span class="chip">
                  <svg viewBox="0 0 24 24" fill="none"><path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z" stroke="#dfe7ff" stroke-width="1.6"/></svg>
                  {CONDITIONS}
                </span>
                <span class="chip">
                  <svg viewBox="0 0 24 24" fill="none"><path d="M3 12c2 0 2-2 4-2s2 2 4 2 2-2 4-2 2 2 4 2" stroke="#dfe7ff" stroke-width="1.6"/></svg>
                  Sea State {SEA_STATE}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="metrics">
        <div class="metric"><div class="k">{HEADING}</div><div class="l">Heading</div></div>
        <div class="metric"><div class="k">{SPEED}</div><div class="l">Speed</div></div>
        <div class="metric"><div class="k">{CPA}</div><div class="l">CPA</div></div>
        <div class="metric"><div class="k">{ETA_BORDER}</div><div class="l">ETA Border</div></div>
        <div class="metric"><div class="k">{ETA_ANCHORAGE}</div><div class="l">ETA Anchorage</div></div>
        <div class="metric"><div class="k">{PROVIDER}</div><div class="l">Providers</div></div>
      </div>

      <div class="tabs">
        <input type="radio" name="t" id="t1" checked><label for="t1">Findings</label>
        <input type="radio" name="t" id="t2"><label for="t2">Nearby Vessels</label>
        <input type="radio" name="t" id="t3"><label for="t3">Passes</label>
        <input type="radio" name="t" id="t4"><label for="t4">Timeline</label>

        <div class="tabbox" id="c1">
          <ul class="bullets">
            <li>Track consistent with approach to international border.</li>
            <li>AIS transponder switched off for &gt; 3h, maintaining steady speed (&gt; 10 kn).</li>
            <li>Positive RF correlation with sporadic emissions (VHF/MF).</li>
            <li>Extrapolation indicates ETA {ETA_BORDER} to the border; {ETA_ANCHORAGE} to anchorage.</li>
          </ul>
        </div>

        <div class="tabbox" id="c2" style="display:none">
          <table class="tbl">
            <thead><tr><th>ID</th><th>Type</th><th>AIS</th><th>SPD</th><th>HDG</th><th>Range</th></tr></thead>
            <tbody>
              {"".join(f"<tr><td>{r['id']}</td><td>{r['type']}</td><td>{r['ais']}</td><td>{r['spd']} kn</td><td>{r['hdg']}</td><td>{r['rng']}</td></tr>" for r in nearby)}
            </tbody>
          </table>
        </div>

        <div class="tabbox" id="c3" style="display:none">
          <table class="tbl">
            <thead><tr><th>Sensor</th><th>T (ETA)</th><th>Inc.</th><th>Resolution</th></tr></thead>
            <tbody>
              {"".join(f"<tr><td>{r['src']}</td><td>{r['t']}</td><td>{r['inc']}</td><td>{r['res']}</td></tr>" for r in passes)}
            </tbody>
          </table>
          <div class="actions" style="margin-top:10px">
            <a class="btn primary" href="#" onclick="notify('task','New SAR collection requested');return false;">
              <svg viewBox="0 0 24 24" fill="none"><path d="M12 20a8 8 0 108-8" stroke="#08121f" stroke-width="2"/><path d="M12 12l8-8" stroke="#08121f" stroke-width="2"/></svg>
              Task SAR
            </a>
            <a class="btn ghost" href="#" onclick="notify('task','Optical collection requested');return false;">
              <svg viewBox="0 0 24 24" fill="none"><path d="M4 8h16v10H4z" stroke="#E6EEFC" stroke-width="2"/><circle cx="12" cy="13" r="3.5" stroke="#E6EEFC" stroke-width="2"/></svg>
              Task Optical
            </a>
          </div>
        </div>

        <div class="tabbox" id="c4" style="display:none">
          <ul class="bullets">
            <li>{LAST_CONTACT}: SAR hull detection with heading {HEADING} and speed {SPEED}.</li>
            <li>{NOW_LOCAL}: Position extrapolation and ETA update.</li>
            <li>+3 min: intermittent RF ping (VHF). Current confidence {CONFIDENCE}%.</li>
          </ul>
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

      <div id="cdnWarn" class="warn">⚠️ Export libraries failed to load (network blocked). Keyboard exports and buttons may not work on this network.</div>
    </div>
  </div>

  <!-- export libs -->
  <script>
    // Warn if a <script> fails (e.g., CDN blocked)
    window.addEventListener('error', function(e){{
      if ((e.target||{{}}).tagName==='SCRIPT') {{
        var el=document.getElementById('cdnWarn'); if(el) el.style.display='block';
      }}
    }}, true);
  </script>
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

    // Simple toast/notify
    function notify(kind,msg){{
      const n=document.createElement('div');
      n.textContent=msg;
      n.style.cssText='position:fixed;right:24px;bottom:24px;background:#10182b;color:#E6EEFC;border:1px solid rgba(255,255,255,.12);padding:10px 12px;border-radius:10px;box-shadow:0 10px 24px rgba(0,0,0,.4);font-weight:700;z-index:9999';
      document.body.appendChild(n);
      setTimeout(()=>n.remove(), 2200);
    }}

    // Export helpers
    const PANEL = document.getElementById('panel');
    function trigger(url,filename){{
      try{{ const a=document.createElement('a'); a.href=url; a.download=filename; a.rel='noopener'; a.target='_blank'; document.body.appendChild(a); a.click(); a.remove(); }}
      catch(e){{ window.open(url,'_blank','noopener'); }}
    }}

    async function exportPNG(){{
      try {{
        const dataUrl=await domtoimage.toPng(PANEL,{{bgcolor:'{CARD_DARK}',quality:1}});
        trigger(dataUrl,'SITREP_Panel.png');
      }} catch(e) {{ notify('err','PNG export failed'); }}
    }}
    async function exportSVG(){{
      try {{
        const dataUrl = await domtoimage.toSvg(PANEL, {{ bgcolor: '{CARD_DARK}', quality: 1 }});
        trigger(dataUrl,'SITREP_Panel.svg');
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
        const blob = pdf.output('blob'); const url = URL.createObjectURL(blob); trigger(url,'SITREP_Panel.pdf');
      }} catch(e) {{ notify('err','PDF export failed'); }}
    }}

    // Keyboard shortcuts
    document.addEventListener('keydown', e=>{{ 
      if(e.key==='g'||e.key==='G') exportPNG();
      if(e.key==='s'||e.key==='S') exportSVG(); 
      if(e.key==='p'||e.key==='P') exportPDF(); 
    }});
  </script>
</body></html>
"""

components.html(html, height=1200, scrolling=True)
