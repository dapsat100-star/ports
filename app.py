# -*- coding: utf-8 -*-
# DAP ATLAS — Port SaaS (Vehicle Yard Count) • Bilingual PT/EN • Time-Series Chart • Export SVG/PDF/PNG

from datetime import datetime, timedelta
from base64 import b64encode
from pathlib import Path
import json
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="DAP ATLAS — Port SaaS", page_icon="🛰️", layout="wide")

# ========= Config =========
LANG = "en"  # "pt" or "en"

# ========= Theme =========
PRIMARY   = "#00E3A5"
ACCENT    = "#34d399"
BG_DARK   = "#0b1221"
CARD_DARK = "#10182b"
TEXT      = "#E6EEFC"
MUTED     = "#9fb0c9"
BORDER    = "rgba(255,255,255,.12)"

PANEL_W_PX   = 560
PANEL_GAP_PX = 24

# ========= Logo & Background (optional) =========
def to_data_uri(path: str) -> str:
    p = Path(path)
    if p.exists() and p.stat().st_size > 0:
        return "data:image/png;base64," + b64encode(p.read_bytes()).decode("ascii")
    return ""

logo_uri = to_data_uri("dapatlas_fundo_branco.png")
bg_img_uri = to_data_uri("porto_estacionamento.png")  # substitua por um print/cena sua

# ========= Data (example) =========
AOI_ID        = "AOI CN-LN-DAL-PORT-2025-01"
PORT_NAME_EN  = "Dalian Port — Vehicle Yard"
PORT_NAME_PT  = "Porto de Dalian — Pátio de Veículos"
SENSOR_EN     = "BlackSky Global-16 (Optical)"
SENSOR_PT     = "BlackSky Global-16 (Óptico)"
ACQ_DT        = "2025-06-07 11:28 UTC"
RES_EN        = "30 cm"
RES_PT        = "30 cm"
YARD_AREA_EN  = "0.24 km²"
YARD_AREA_PT  = "0,24 km²"
VEH_EST_EN    = "897 ± 10%"
VEH_EST_PT    = "897 ± 10%"
CONF_EN       = "95%"
CONF_PT       = "95%"
PROC_T_EN     = "10 s"
PROC_T_PT     = "10 s"
NOW_LABEL     = datetime.now().strftime("%d/%m %H:%M")

# time series (last 14 days; example data)
dates = [(datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(13, -1, -1)]
counts = [812, 818, 827, 835, 842, 851, 860, 869, 874, 881, 888, 893, 900, 907]  # +~7% trend

# sector table (example)
sectors = [
    {"sector":"Q1","area_en":"0.06 km²","area_pt":"0,06 km²","vehicles":"312","occ":"89%"},
    {"sector":"Q2","area_en":"0.05 km²","area_pt":"0,05 km²","vehicles":"268","occ":"86%"},
    {"sector":"Q3","area_en":"0.07 km²","area_pt":"0,07 km²","vehicles":"203","occ":"73%"},
    {"sector":"Q4","area_en":"0.06 km²","area_pt":"0,06 km²","vehicles":"114","occ":"61%"},
]

# ========= i18n =========
T = {
    "en": {
        "title": "DAP ATLAS — Port SaaS",
        "subtitle": "Automatic Vehicle Yard Counting",
        "badge_live": "Live 24/7",
        "kpi_vehicles": "Vehicles (estimate)",
        "kpi_conf": "Confidence",
        "kpi_proc": "Processing Time",
        "kpi_area": "Analyzed Area",
        "kpi_res": "Resolution",
        "kpi_source": "Source",
        "tab_findings": "Findings",
        "tab_meta": "Metadata",
        "tab_kpis": "KPIs & Sectors",
        "tab_actions": "SLA & Actions",
        "findings": [
            "Vehicle estimate: 897 ±10% (AI supervised with local samples).",
            "Average occupancy above 85% in 2 sectors (attention threshold).",
            "Weekly trend shows +7% increase in yard stock (last 14 days).",
            "Processing time: 10 s (no human intervention).",
            "Next optical collection window in ~2h; consider complementary sunset tasking (long shadows)."
        ],
        "meta_rows": [
            ("Port","{PORT}"),
            ("AOI","{AOI}"),
            ("Acquisition","{ACQ}"),
            ("Sensor","{SENSOR}"),
            ("Resolution","{RES}"),
            ("Analyzed area","{AREA}"),
            ("Generated","{GEN}"),
            ("System","DAP ATLAS — Port SaaS"),
        ],
        "tbl_sector_head": ["Sector","Area","Vehicles","Occupancy"],
        "chart_title": "Yard Vehicles — Last 14 Days",
        "sla_list": [
            "<b>DAP ATLAS SLA (yards):</b> T90 &lt; 30 s per AOI | Target relative error ≤ ±12% with local sampling.",
            "Exports: CSV (sector counts), GeoJSON (polygons), PDF report (SITREP).",
            "Recommendations: normalize collection time, avoid extreme angles and corridor shadowing."
        ],
        "btn_csv": "Export CSV",
        "btn_task": "Queue New Collection",
        "btn_notify": "Notify Stakeholders",
        "footer_shortcuts": "Shortcuts: S (SVG) • P (PDF) • G (PNG)",
        "panel_sitrep": "Situation Panel",
    },
    "pt": {
        "title": "DAP ATLAS — Port SaaS",
        "subtitle": "Contagem Automática de Veículos em Pátio",
        "badge_live": "Live 24/7",
        "kpi_vehicles": "Veículos (estimativa)",
        "kpi_conf": "Confiança",
        "kpi_proc": "Tempo de Processamento",
        "kpi_area": "Área Analisada",
        "kpi_res": "Resolução",
        "kpi_source": "Fonte",
        "tab_findings": "Achados",
        "tab_meta": "Metadados",
        "tab_kpis": "KPIs & Setores",
        "tab_actions": "SLA & Ações",
        "findings": [
            "Estimativa de veículos no pátio: 897 ±10% (IA supervisionada por amostras locais).",
            "Ocupação média acima de 85% em 2 setores (limiar de atenção).",
            "Tendência semanal indica +7% no estoque do pátio (últimos 14 dias).",
            "Tempo de processamento: 10 s (sem intervenção humana).",
            "Próxima janela óptica em ~2h; sugerir coleta ao pôr do sol (sombras longas)."
        ],
        "meta_rows": [
            ("Porto","{PORT}"),
            ("AOI","{AOI}"),
            ("Aquisição","{ACQ}"),
            ("Sensor","{SENSOR}"),
            ("Resolução","{RES}"),
            ("Área analisada","{AREA}"),
            ("Geração","{GEN}"),
            ("Sistema","DAP ATLAS — Port SaaS"),
        ],
        "tbl_sector_head": ["Setor","Área","Veículos","Ocupação"],
        "chart_title": "Veículos no Pátio — Últimos 14 dias",
        "sla_list": [
            "<b>SLA DAP ATLAS (pátios):</b> T90 &lt; 30 s por AOI | Erro relativo ≤ ±12% com amostragem local.",
            "Exportações: CSV (contagens por setor), GeoJSON (polígonos), Relatório PDF (SITREP).",
            "Recomendações: normalizar horário de coleta, evitar ângulos extremos e sombra nos corredores."
        ],
        "btn_csv": "Exportar CSV",
        "btn_task": "Taskear Nova Coleta",
        "btn_notify": "Notificar Stakeholders",
        "footer_shortcuts": "Atalhos: S (SVG) • P (PDF) • G (PNG)",
        "panel_sitrep": "Painel de Situação",
    }
}[LANG]

PORT_NAME = PORT_NAME_EN if LANG=="en" else PORT_NAME_PT
SENSOR_TX = SENSOR_EN if LANG=="en" else SENSOR_PT
RES_TX    = RES_EN if LANG=="en" else RES_PT
AREA_TX   = YARD_AREA_EN if LANG=="en" else YARD_AREA_PT
VEH_TX    = VEH_EST_EN if LANG=="en" else VEH_EST_PT
CONF_TX   = CONF_EN if LANG=="en" else CONF_PT
PROC_TX   = PROC_T_EN if LANG=="en" else PROC_T_PT

# ========= Build HTML helpers =========
def meta_table_rows():
    rows = []
    for k, v in T["meta_rows"]:
        v = v.format(PORT=PORT_NAME, AOI=AOI_ID, ACQ=ACQ_DT, SENSOR=SENSOR_TX,
                     RES=RES_TX, AREA=AREA_TX, GEN=NOW_LABEL)
        rows.append(f"<tr><th>{k}</th><td>{v}</td></tr>")
    return "".join(rows)

sector_rows = "".join(
    f"<tr><td>{s['sector']}</td><td>{s['area_en'] if LANG=='en' else s['area_pt']}</td>"
    f"<td>{s['vehicles']}</td><td>{s['occ']}</td></tr>"
    for s in sectors
)

findings_html = "".join(f"<li>{a}</li>" for a in T["findings"])

# ========= HTML =========
html = f"""
<!doctype html>
<html><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>{T['title']}</title>
<style>
:root {{
  --panel-w:{PANEL_W_PX}px; --gap:{PANEL_GAP_PX}px;
  --primary:{PRIMARY}; --accent:{ACCENT};
  --bg:{BG_DARK}; --card:{CARD_DARK}; --text:{TEXT}; --muted:{MUTED}; --border:{BORDER};
}}
*{{box-sizing:border-box}}
html,body{{height:100%;margin:0;background:var(--bg);color:var(--text);
  font-family: Inter, Roboto, Segoe UI, -apple-system, system-ui, Arial, sans-serif}}

.stage{{min-height:100vh;display:flex;gap:18px;align-items:stretch;justify-content:center;padding:28px}}
.mapwrap{{flex:1 1 60%;border-radius:18px;overflow:hidden;border:1px solid var(--border);
  background:#0a111f; box-shadow:0 18px 44px rgba(0,0,0,.55); position:relative}}
.mapimg{{position:absolute; inset:0; width:100%; height:100%; object-fit:cover; opacity:.95}}

.panel{{flex:0 0 560px; display:flex; flex-direction:column; gap:12px; padding:16px;
  border:1px solid var(--border); border-radius:18px; background:var(--card);
  box-shadow:0 18px 44px rgba(0,0,0,.55); overflow:auto}}

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
.metric .k{{font-size:1.15rem; font-weight:800}}
.metric .l{{font-size:.85rem; color:var(--muted)}}

.tabs{{margin-top:6px}}
.tabs input{{display:none}}
.tabs label{{display:inline-block; padding:8px 12px; margin-right:8px; border:1px solid var(--border);
  border-bottom:none; border-top-left-radius:10px; border-top-right-radius:10px;
  color:var(--muted); background:rgba(255,255,255,.02); cursor:pointer; font-weight:800; font-size:.9rem}}
.tabs input:checked + label{{color:#08121f; background:var(--primary); border-color:var(--primary)}}
.tabbox{{border:1px solid var(--border); border-radius:0 12px 12px 12px; padding:12px; margin-top:-1px}}

ul.bullets{{margin:6px 0 0 0; padding-left:1.2rem}} ul.bullets li{{margin:8px 0}}
.tbl{{width:100%; border-collapse:collapse}} .tbl th, .tbl td{{padding:9px 6px; border-bottom:1px solid var(--border); text-align:left; font-size:.95rem}}
.tbl th{{color:var(--muted); font-weight:700}}

.actions{{display:flex; gap:8px; flex-wrap:wrap; margin-top:8px}}
.btn{{display:inline-flex; align-items:center; gap:8px; padding:9px 12px; border-radius:10px; font-weight:800; font-size:.9rem; cursor:pointer; text-decoration:none}}
.btn.primary{{background:var(--primary); color:#08121f; border:1px solid var(--primary)}}
.btn.ghost{{background:rgba(255,255,255,.04); color:#E6EEFC; border:1px solid var(--border)}}

.footer{{margin-top:auto; display:flex; justify-content:space-between; align-items:center}}
.small{{font-size:.85rem; color:var(--muted)}}
.hint{{font-size:.8rem; color:var(--muted)}}
</style>
</head>
<body>
  <div class="stage">
    <div class="mapwrap">
      {"<img class='mapimg' src='"+bg_img_uri+"' alt='scene'/>" if bg_img_uri else ""}
    </div>

    <div class="panel" id="panel">
      <div class="header">
        <div class="brand">
          <div class="logo">{("<img src='"+logo_uri+"' alt='DAP ATLAS'/>" if logo_uri else "<div style='color:#000;font-weight:900'>DA</div>")}</div>
          <div>
            <div class="ttl">{T['title']}</div>
            <div class="sub">{T['subtitle']}</div>
          </div>
        </div>
        <div class="badge">{AOI_ID} • {T['badge_live']}</div>
      </div>

      <!-- KPIs -->
      <div class="metrics">
        <div class="metric"><div class="k">{VEH_TX}</div><div class="l">{T['kpi_vehicles']}</div></div>
        <div class="metric"><div class="k">{CONF_TX}</div><div class="l">{T['kpi_conf']}</div></div>
        <div class="metric"><div class="k">{PROC_TX}</div><div class="l">{T['kpi_proc']}</div></div>
        <div class="metric"><div class="k">{AREA_TX}</div><div class="l">{T['kpi_area']}</div></div>
        <div class="metric"><div class="k">{RES_TX}</div><div class="l">{T['kpi_res']}</div></div>
        <div class="metric"><div class="k">{SENSOR_TX}</div><div class="l">{T['kpi_source']}</div></div>
      </div>

      <!-- Tabs -->
      <div class="tabs">
        <input type="radio" name="t" id="tab1" checked><label for="tab1">{T['tab_findings']}</label>
        <input type="radio" name="t" id="tab2"><label for="tab2">{T['tab_meta']}</label>
        <input type="radio" name="t" id="tab3"><label for="tab3">{T['tab_kpis']}</label>
        <input type="radio" name="t" id="tab4"><label for="tab4">{T['tab_actions']}</label>

        <div class="tabbox" id="c1">
          <ul class="bullets">{findings_html}</ul>
        </div>

        <div class="tabbox" id="c2" style="display:none">
          <table class="tbl">
            <thead><tr><th>Key</th><th>Value</th></tr></thead>
            <tbody>{meta_table_rows()}</tbody>
          </table>
        </div>

        <div class="tabbox" id="c3" style="display:none">
          <div style="margin-bottom:10px;font-weight:800">{T['chart_title']}</div>
          <canvas id="vehChart" height="140"></canvas>
          <div style="height:8px"></div>
          <table class="tbl">
            <thead><tr><th>{T['tbl_sector_head'][0]}</th><th>{T['tbl_sector_head'][1]}</th><th>{T['tbl_sector_head'][2]}</th><th>{T['tbl_sector_head'][3]}</th></tr></thead>
            <tbody>{sector_rows}</tbody>
          </table>
        </div>

        <div class="tabbox" id="c4" style="display:none">
          <ul class="bullets">
            {"".join(f"<li>{item}</li>" for item in T['sla_list'])}
          </ul>
          <div class="actions">
            <a class="btn primary" href="#" onclick="notify('job','{T['btn_csv']}');return false;">{T['btn_csv']}</a>
            <a class="btn ghost"   href="#" onclick="notify('job','{T['btn_task']}');return false;">{T['btn_task']}</a>
            <a class="btn ghost"   href="#" onclick="notify('mail','{T['btn_notify']}');return false;">{T['btn_notify']}</a>
          </div>
        </div>
      </div>

      <div class="footer">
        <div class="small">© {datetime.now().year} MAVIPE Space Systems</div>
        <div class="small">{T['footer_shortcuts']}</div>
      </div>
    </div>
  </div>

  <!-- Libs -->
  <script src="https://cdn.jsdelivr.net/npm/dom-to-image-more@2.8.0/dist/dom-to-image-more.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/jspdf@2.5.1/dist/jspdf.umd.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/svg2pdf.js@2.2.3/dist/svg2pdf.umd.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>

  <script>
    // Tab switching
    const c1=document.getElementById('c1'), c2=document.getElementById('c2'), c3=document.getElementById('c3'), c4=document.getElementById('c4');
    document.getElementById('tab1').onchange=()=>{{c1.style.display='block'; c2.style.display='none'; c3.style.display='none'; c4.style.display='none';}};
    document.getElementById('tab2').onchange=()=>{{c1.style.display='none'; c2.style.display='block'; c3.style.display='none'; c4.style.display='none';}};
    document.getElementById('tab3').onchange=()=>{{c1.style.display='none'; c2.style.display='none'; c3.style.display='block'; c4.style.display='none';}};
    document.getElementById('tab4').onchange=()=>{{c1.style.display='none'; c2.style.display='none'; c3.style.display='none'; c4.style.display='block';}};

    // Toast
    function notify(kind,msg){{
      const n=document.createElement('div');
      n.textContent=msg;
      n.style.cssText='position:fixed;right:24px;bottom:24px;background:#10182b;color:#E6EEFC;border:1px solid rgba(255,255,255,.12);padding:10px 12px;border-radius:10px;box-shadow:0 10px 24px rgba(0,0,0,.4);font-weight:700;z-index:9999';
      document.body.appendChild(n);
      setTimeout(()=>n.remove(), 2200);
    }}

    // Chart.js — vehicle time series
    const vehCtx = document.getElementById('vehChart').getContext('2d');
    const vehChart = new Chart(vehCtx, {{
      type: 'line',
      data: {{
        labels: {json.dumps(dates)},
        datasets: [{{
          label: '{T['panel_sitrep']}',
          data: {json.dumps(counts)},
          tension: 0.25,
          borderColor: '#00E3A5',
          backgroundColor: 'rgba(0,227,165,.15)',
          fill: true,
          pointRadius: 2
        }}]
      }},
      options: {{
        responsive: true,
        plugins: {{
          legend: {{ display: false }},
        }},
        scales: {{
          x: {{ ticks: {{ color: '{MUTED}' }}, grid: {{ color: 'rgba(255,255,255,.06)' }} }},
          y: {{ ticks: {{ color: '{MUTED}' }}, grid: {{ color: 'rgba(255,255,255,.06)' }} }}
        }}
      }}
    }});

    // Export helpers
    const PANEL = document.getElementById('panel');
    function trigger(url,filename){{
      try{{ const a=document.createElement('a'); a.href=url; a.download=filename; a.rel='noopener'; a.target='_blank'; document.body.appendChild(a); a.click(); a.remove(); }}
      catch(e){{ window.open(url,'_blank','noopener'); }}
    }}
    async function exportSVG(){{
      const dataUrl=await domtoimage.toSvg(PANEL,{{bgcolor:'{CARD_DARK}',quality:1}});
      trigger(dataUrl,'PORT_SaaS.svg');
    }}
    async function exportPNG(){{
      const dataUrl=await domtoimage.toPng(PANEL,{{bgcolor:'{CARD_DARK}',quality:1}});
      trigger(dataUrl,'PORT_SaaS.png');
    }}
    async function exportPDF(){{
      const svgUrl=await domtoimage.toSvg(PANEL,{{bgcolor:'{CARD_DARK}',quality:1}});
      const svgText=await (await fetch(svgUrl)).text();
      const {{ jsPDF }} = window.jspdf; const pdf=new jsPDF({{ unit:'pt', format:'a4', orientation:'p' }});
      const parser=new DOMParser(); const svgDoc=parser.parseFromString(svgText,'image/svg+xml'); const svgEl=svgDoc.documentElement;
      const width=parseFloat(svgEl.getAttribute('width'))||PANEL.offsetWidth;
      const height=parseFloat(svgEl.getAttribute('height'))||PANEL.offsetHeight;
      const pageW=pdf.internal.pageSize.getWidth(), pageH=pdf.internal.pageSize.getHeight();
      const scale=Math.min(pageW/width,pageH/height);
      window.svg2pdf(svgEl,pdf,{{ x:(pageW-width*scale)/2, y:(pageH-height*scale)/2, scale }});
      const blob=pdf.output('blob'); const url=URL.createObjectURL(blob); trigger(url,'PORT_SaaS.pdf');
    }}
    document.addEventListener('keydown', e=>{{
      if(e.key==='s'||e.key==='S') exportSVG();
      if(e.key==='p'||e.key==='P') exportPDF();
      if(e.key==='g'||e.key==='G') exportPNG();
    }});
  </script>
</body></html>
"""

components.html(html, height=900, scrolling=False)
