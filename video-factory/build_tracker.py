#!/usr/bin/env python3
"""Render the Skeleton Video Factory check-off board from the manifest.

Reads production-manifest.json and writes tracker.html - a self-contained page
(no server, no network) that lists every product in SKU order (matching the
audio/ folder), with its script, an inline player for its cloned-skeleton VO,
and its ready-to-paste Nano Banana + Flow/Seedance prompts (one-click copy).

Each row has ONE actionable checkbox: "video made". Tick it when you finish the
video and the row disappears from the default view and the counters tick down.
Products that ALREADY have a video on box.shopluvbuds.com are treated as done and
hidden by default too. Manual ticks persist in the browser's localStorage.

Run:  python3 build_tracker.py   ->   open tracker.html
Re-run after build_manifest.py or a TTS batch to refresh the data.
"""
from __future__ import annotations
import json, html, os, re
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import quote

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "production-manifest.json"
OUT = HERE / "tracker.html"

CSS = """
:root{--bg:#0f1115;--card:#171a21;--line:#262b36;--fg:#e6e9ef;--mut:#8a93a6;--acc:#5b8cff;--ok:#2ecc71;--warn:#e0a83e}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.5 -apple-system,Segoe UI,Roboto,sans-serif}
header{position:sticky;top:0;background:#0f1115ee;backdrop-filter:blur(6px);border-bottom:1px solid var(--line);padding:14px 20px;z-index:5}
h1{margin:0 0 8px;font-size:17px}.sub{color:var(--mut);font-size:12px}
.bar{height:8px;background:var(--line);border-radius:6px;overflow:hidden;margin:10px 0 6px}
.bar>i{display:block;height:100%;background:var(--ok);transition:width .2s}
.stats{display:flex;gap:8px;flex-wrap:wrap;color:var(--mut);font-size:12px;align-items:center}
.stats b{color:var(--fg)}.stats .big{color:var(--warn);font-size:13px}
.chip{cursor:pointer;user-select:none;background:var(--card);border:1px solid var(--line);border-radius:999px;padding:5px 10px;color:var(--mut);transition:border-color .15s,color .15s,background .15s}
.chip:hover{border-color:var(--acc);color:var(--fg)}
.chip.on{border-color:var(--acc);color:var(--fg);background:#1a2338}
.chip.big{color:var(--warn)}
.chip.big.on{border-color:var(--warn);background:#2a2310}
.controls{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px;align-items:center}
.controls input,.controls select{background:var(--card);color:var(--fg);border:1px solid var(--line);border-radius:8px;padding:7px 10px;font-size:13px}
.controls input[type=search]{flex:1;min-width:180px}
.controls .hide-done{display:flex;align-items:center;gap:8px;color:var(--mut);font-size:13px;user-select:none;white-space:nowrap;cursor:pointer;padding:6px 10px;background:var(--card);border:1px solid var(--line);border-radius:8px}
.controls .hide-done input{width:16px;height:16px;accent-color:var(--ok);cursor:pointer}
.b.host-box{color:#8fe3a8;border-color:#2a5a3a}.b.host-shop{color:#8ab4ff;border-color:#2a3a5a}.b.host-none{color:var(--mut)}
main{padding:16px 20px;max-width:1100px;margin:0 auto}
.row{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px;margin-bottom:12px}
.row.made{opacity:.55}
.rh{display:flex;justify-content:space-between;gap:12px;align-items:flex-start}
.name{font-weight:600}.sku{color:var(--mut);font-size:12px;font-family:ui-monospace,monospace}
.visit{color:var(--acc);text-decoration:none}.visit:hover{text-decoration:underline}
.badges{display:flex;gap:6px;flex-wrap:wrap;margin-top:4px}
.b{font-size:11px;padding:2px 8px;border-radius:20px;border:1px solid var(--line);color:var(--mut)}
.b.pri{color:#ffd27a;border-color:#5a4a24}.b.copy{color:#ff9d9d;border-color:#5a2a2a}
.b.site{color:#8fe3a8;border-color:#2a5a3a}
.b.img.high{color:#8fe3a8;border-color:#2a5a3a}.b.img.medium{color:#ffd27a;border-color:#5a4a24}.b.img.low{color:#ff9d9d;border-color:#5a2a2a}
.rhright{display:flex;gap:10px;align-items:flex-start}
.thumbwrap{flex:0 0 auto;line-height:0}
.thumb{width:78px;height:78px;object-fit:cover;border-radius:8px;border:1px solid var(--line);display:block;background:#0b0d12}
.script{margin:10px 0;color:#cfd6e4;font-size:13px;white-space:pre-wrap;max-height:0;overflow:hidden;transition:max-height .2s}
.script.open{max-height:600px}
.toggle{cursor:pointer;color:var(--acc);font-size:12px;user-select:none}
.audio{display:flex;align-items:center;gap:10px;margin:10px 0 4px}
.audio audio{height:34px;flex:1;min-width:0}
.afile{color:var(--mut);font-size:11px;font-family:ui-monospace,monospace;white-space:nowrap}
.prompts{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:8px}
@media(max-width:680px){.prompts{grid-template-columns:1fr}}
.pbox{background:#12151c;border:1px solid var(--line);border-radius:8px;padding:8px}
.pbox .lbl{font-size:11px;color:var(--mut);display:flex;justify-content:space-between;margin-bottom:4px}
.pbox pre{margin:0;white-space:pre-wrap;font:12px/1.45 ui-monospace,monospace;color:#c6cede;max-height:80px;overflow:auto}
.cp{cursor:pointer;color:var(--acc);border:0;background:none;font-size:11px}
.made-row{display:flex;align-items:center;gap:10px;margin-top:12px;padding-top:10px;border-top:1px solid var(--line)}
.made-row label{display:flex;align-items:center;gap:8px;font-size:14px;cursor:pointer;user-select:none;font-weight:600}
.made-row input{width:20px;height:20px;accent-color:var(--ok);cursor:pointer}
.made-row.on input{cursor:not-allowed}
.hidden{display:none}
"""

JS = """
const DATA = %s;
const K = s => 'luvfactory:'+s+':video';
const load = sku => localStorage.getItem(K(sku))==='1';
const save = (sku,v) => localStorage.setItem(K(sku), v?'1':'0');
const onSite = p => p.has_video;                 // already has a video on box.shopluvbuds.com
const madeDurable = p => !!p.video_made;         // status.video=done in production-manifest.json
const madeHere = p => madeDurable(p) || load(p.sku); // rendered (manifest) OR operator tick
const done = p => onSite(p) || madeHere(p);      // has a video, one way or the other
const hostOf = p => p.host || 'none';            // box | shop | none
const HIDE_DONE_K = 'luvfactory:hideDone';
const hideDoneOn = () => localStorage.getItem(HIDE_DONE_K)==='1';
const setHideDone = v => localStorage.setItem(HIDE_DONE_K, v?'1':'0');

function setFilter(f){
  const sel=document.getElementById('filter');
  if(sel.value===f){ /* keep */ } else { sel.value=f; }
  document.querySelectorAll('.chip[data-filter]').forEach(el=>{
    el.classList.toggle('on', el.dataset.filter===f);
  });
  render();
}

function matches(p, f, q, hideDone){
  const hay=(p.name+' '+p.sku+' '+p.script+' '+(p.host||'')).toLowerCase();
  if(q && !hay.includes(q)) return false;
  let ok = true;
  if(f==='tomake')        ok = p.ready && !done(p);
  else if(f==='made')     ok = madeHere(p) && !onSite(p);
  else if(f==='onsite')   ok = onSite(p);
  else if(f==='hasimage') ok = !!p.img && p.ready && !done(p);
  else if(f==='hasimageany') ok = !!p.img;
  else if(f==='needscopy') ok = !p.ready;
  else if(f==='hostbox')  ok = hostOf(p)==='box';
  else if(f==='hostshop') ok = hostOf(p)==='shop';
  else if(f==='hostnone') ok = hostOf(p)==='none';
  // hide greyed-out done rows inside whatever filter is active
  if(ok && hideDone && done(p)) ok = false;
  return ok;
}

function render(){
  const q=(document.getElementById('q').value||'').toLowerCase();
  const f=document.getElementById('filter').value;
  const hideEl=document.getElementById('hideDone');
  const hideDone=!!(hideEl && hideEl.checked);
  let shown=0, toMake=0, madeN=0, onSiteN=0, ready=0, imgN=0, imgAny=0, boxN=0, shopN=0, noneN=0;
  for(const p of DATA){
    if(p.ready) ready++;
    if(onSite(p)) onSiteN++;
    if(madeHere(p) && !onSite(p)) madeN++;
    if(p.ready && !done(p)) toMake++;
    if(p.img && p.ready && !done(p)) imgN++;
    if(p.img) imgAny++;
    if(hostOf(p)==='box') boxN++;
    else if(hostOf(p)==='shop') shopN++;
    else noneN++;
    const row=document.getElementById('r-'+p.id);
    row.classList.toggle('made', madeHere(p) || onSite(p));
    const ok=matches(p, f, q, hideDone);
    row.classList.toggle('hidden', !ok);
    if(ok) shown++;
  }
  const have = madeN + DATA.filter(p=>p.ready && onSite(p)).length;
  const pct = ready ? Math.round(100*have/ready) : 0;
  document.getElementById('pctbar').style.width=pct+'%%';
  document.getElementById('pct').textContent=pct+'%% of product videos exist ('+have+'/'+ready+')';
  document.getElementById('cToMake').textContent=toMake;
  document.getElementById('cMade').textContent=madeN;
  document.getElementById('cSite').textContent=onSiteN;
  document.getElementById('cImg').textContent=imgN;
  document.getElementById('cImgAny').textContent=imgAny;
  document.getElementById('cBox').textContent=boxN;
  document.getElementById('cShop').textContent=shopN;
  document.getElementById('shown').textContent=shown;
  document.querySelectorAll('.chip[data-filter]').forEach(el=>{
    el.classList.toggle('on', el.dataset.filter===f);
  });
}
function toggle(sku,cb){ save(sku,cb.checked); render(); }
function copy(id,btn){navigator.clipboard.writeText(document.getElementById(id).textContent);btn.textContent='copied';setTimeout(()=>btn.textContent='copy',900);}
function toggleScript(id){document.getElementById('s-'+id).classList.toggle('open');}
window.addEventListener('DOMContentLoaded',()=>{
  for(const p of DATA){
    const cb=document.getElementById('cb-'+p.id);
    if(cb && !cb.disabled) cb.checked = load(p.sku);
  }
  const hideCb=document.getElementById('hideDone');
  if(hideCb){
    hideCb.checked = hideDoneOn();
    hideCb.addEventListener('change',()=>{ setHideDone(hideCb.checked); render(); });
  }
  document.getElementById('q').addEventListener('input',render);
  document.getElementById('filter').addEventListener('change',e=>setFilter(e.target.value));
  document.querySelectorAll('.chip[data-filter]').forEach(el=>{
    el.addEventListener('click',()=>setFilter(el.dataset.filter));
  });
  setFilter(document.getElementById('filter').value || 'tomake');
});
"""

def esc(s: str) -> str:
    return html.escape(s or "")

def cssid(sku: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "_", sku or "")

def audio_rel(p: dict) -> tuple[str, str]:
    """(url-encoded relative src, plain basename) for the product's WAV, or ('','')."""
    af = p.get("audio_file") or ""
    base = os.path.basename(af)
    if not base:
        return "", ""
    return "audio/" + quote(base), base

def host_kind(p: dict) -> str:
    label = (p.get("view_label") or "").lower()
    url = (p.get("view_url") or "").lower()
    if "box.shopluvbuds" in label or "box.shopluvbuds" in url:
        return "box"
    if "shopluvbuds" in label or "shopluvbuds.com" in url:
        return "shop"
    return "none"

def row_html(p: dict) -> str:
    rid = cssid(p["sku"])
    on_site = bool(p.get("has_video"))
    video_made = (p.get("status") or {}).get("video") == "done"
    ready = p["status"]["script"] == "ready"
    host = host_kind(p)
    badges = []
    if on_site:
        badges.append('<span class="b site">video on site</span>')
    elif video_made:
        badges.append('<span class="b site">video rendered</span>')
    elif ready:
        badges.append('<span class="b pri">needs video</span>')
    if not ready:
        badges.append('<span class="b copy">needs copy</span>')
    if p.get("base_image"):
        conf = esc(p.get("base_image_confidence") or "")
        badges.append(f'<span class="b img {conf}">image: {conf}</span>')
    if host == "box":
        badges.append('<span class="b host-box">box.shopluvbuds.com</span>')
    elif host == "shop":
        badges.append('<span class="b host-shop">shopluvbuds.com</span>')
    else:
        badges.append('<span class="b host-none">no store url</span>')

    src, base = audio_rel(p)
    audio = ""
    if src:
        audio = (f'<div class="audio"><audio controls preload="none" src="{esc(src)}"></audio>'
                 f'<span class="afile">{esc(base)}</span></div>')

    nano = esc(p.get("nano_banana_prompt", ""))
    anim = esc(p.get("animation_prompt", ""))
    script = esc(p.get("script", "")) or '<span style="color:var(--warn)">no script yet - write copy</span>'
    wc = f' &middot; {p["word_count"]} words' if p.get("word_count") else ""
    visit = ""
    if p.get("view_url"):
        visit = (f' &middot; <a class="visit" href="{esc(p["view_url"])}" target="_blank" '
                 f'rel="noopener">{esc(p["view_label"])}</a>')
    thumb = ""
    if p.get("base_image"):
        bi = esc(p["base_image"]); conf = esc(p.get("base_image_confidence") or "")
        txt = esc(p.get("base_image_text") or "")
        thumb = (f'<a class="thumbwrap" href="{bi}" target="_blank" rel="noopener" '
                 f'title="matched base image ({conf}) - reads: {txt}"><img class="thumb" src="{bi}" loading="lazy"></a>')

    if on_site:
        cb = '<input type="checkbox" id="cb-{rid}" checked disabled>'.format(rid=rid)
        cls = "made-row on"
        label = "video already on box.shopluvbuds.com"
    elif video_made:
        cb = '<input type="checkbox" id="cb-{rid}" checked disabled>'.format(rid=rid)
        cls = "made-row on"
        label = "video rendered (awaiting CDN / site wire)"
    else:
        cb = '<input type="checkbox" id="cb-{rid}" onchange="toggle(\'{sku}\',this)">'.format(
            rid=rid, sku=esc(p["sku"]))
        cls = "made-row"
        label = "video made"

    return f"""<div class="row" id="r-{rid}">
  <div class="rh"><div>
    <div class="name">{esc(p['name'])}</div>
    <div class="sku">{esc(p['sku'])}{wc}{visit}</div>
    <div class="badges">{''.join(badges)}</div>
  </div><div class="rhright">{thumb}<div class="toggle" onclick="toggleScript('{rid}')">script</div></div></div>
  <div class="script" id="s-{rid}">{script}</div>
  {audio}
  <div class="prompts">
    <div class="pbox"><div class="lbl">Nano Banana (image) <button class="cp" onclick="copy('n-{rid}',this)">copy</button></div><pre id="n-{rid}">{nano}</pre></div>
    <div class="pbox"><div class="lbl">Flow / Seedance (animate) <button class="cp" onclick="copy('a-{rid}',this)">copy</button></div><pre id="a-{rid}">{anim}</pre></div>
  </div>
  <div class="{cls}"><label>{cb} {label}</label></div>
</div>"""

def main() -> int:
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    products = m["products"]   # already SKU-sorted by build_manifest.py
    # slim data for the client filter/counters
    slim = [{"id": cssid(p["sku"]), "sku": p["sku"], "name": p["name"], "script": p["script"],
             "has_video": bool(p.get("has_video")),
             "video_made": (p.get("status") or {}).get("video") == "done",
             "ready": p["status"]["script"] == "ready",
             "img": bool(p.get("base_image")), "word_count": p["word_count"],
             "host": host_kind(p), "view_label": p.get("view_label") or ""}
            for p in products]
    rows = "\n".join(row_html(p) for p in products)
    js = JS % json.dumps(slim)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    ready_n = sum(1 for p in products if p["status"]["script"] == "ready")
    site_n = sum(1 for p in products if p.get("has_video"))
    made_n = sum(1 for p in products
                 if (p.get("status") or {}).get("video") == "done" and not p.get("has_video"))
    page = f"""<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Skeleton Video Factory - Tracker</title><style>{CSS}</style></head><body>
<header>
  <h1>Skeleton Video Factory <span class="sub">box.shopluvbuds.com &middot; {len(products)} products &middot; SKU order &middot; built {now}</span></h1>
  <div class="bar"><i id="pctbar"></i></div>
  <div class="stats">
    <span id="pct"></span>
    <button type="button" class="chip big" data-filter="tomake">to make <b id="cToMake">0</b></button>
    <button type="button" class="chip" data-filter="made">made here <b id="cMade">0</b></button>
    <button type="button" class="chip" data-filter="onsite">on site <b id="cSite">0</b></button>
    <button type="button" class="chip" data-filter="hasimage">have image (to make) <b id="cImg">0</b></button>
    <button type="button" class="chip" data-filter="hasimageany">have image (any) <b id="cImgAny">0</b></button>
    <button type="button" class="chip" data-filter="hostbox">box.shopluvbuds.com <b id="cBox">0</b></button>
    <button type="button" class="chip" data-filter="hostshop">shopluvbuds.com <b id="cShop">0</b></button>
    <button type="button" class="chip" data-filter="all">all / showing <b id="shown">0</b></button>
  </div>
  <div class="controls">
    <input type="search" id="q" placeholder="search product, sku, script text...">
    <select id="filter">
      <option value="tomake">to make (need a video)</option>
      <option value="hasimage">to make, has base image</option>
      <option value="hasimageany">has base image (any status)</option>
      <option value="made">made here (rendered, not on site yet)</option>
      <option value="onsite">already on site</option>
      <option value="hostbox">linked on box.shopluvbuds.com</option>
      <option value="hostshop">linked on shopluvbuds.com only</option>
      <option value="hostnone">no store url</option>
      <option value="needscopy">needs copy</option>
      <option value="all">all products</option>
    </select>
    <label class="hide-done" title="Hide greyed-out rows that already have a video">
      <input type="checkbox" id="hideDone"> hide done
    </label>
  </div>
</header>
<main>{rows}</main>
<script>{js}</script>
</body></html>"""
    OUT.write_text(page, encoding="utf-8")
    print(f"Wrote {OUT.name}  ({len(products)} products, {ready_n} script-ready, "
          f"{site_n} on site, {made_n} rendered-not-live)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
