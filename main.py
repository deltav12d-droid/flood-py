<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Flood Alert & Navigation — Trivandrum</title>

<!-- Leaflet -->
<link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>

<style>
:root{
  --bg:#0f1720; --panel:#0b1220; --text:#e6eef6; --muted:#9fb0c8;
  --accent:#16a34a; --danger:#ef4444; --safe:#165f2b; /* dark green */
  --pending:#f59e0b; /* orange for pending reports */
}
*{box-sizing:border-box}
body{margin:0;font-family:Inter,Segoe UI,Arial,Helvetica,sans-serif;background:var(--bg);color:var(--text);height:100vh;overflow:hidden}
#map{height:100%;width:100%}

/* Left control panel */
#leftPanel{
  position:absolute; left:12px; top:12px; z-index:1600; width:360px;
  background:var(--panel); padding:12px; border-radius:12px;
  box-shadow:0 10px 30px rgba(0,0,0,0.45);
}
#leftPanel h3{ margin:0 0 8px 0; font-size:16px }
.input{ width:100%; padding:10px; margin-bottom:8px; border-radius:8px; border:0; background:#071025; color:var(--text) }
.btn{ padding:10px; border-radius:8px; border:0; cursor:pointer; box-shadow:0 6px 18px rgba(0,0,0,0.35); background:var(--accent); color:#022; font-weight:700 }
.btn.ghost{ background:transparent; color:var(--text); border:1px solid rgba(255,255,255,0.04); font-weight:600 }
.small{ font-size:12px; color:var(--muted) }

/* suggestion box */
.suggestions{
  position: absolute;
  z-index: 2200;
  background: #071025;
  border-radius: 8px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.6);
  overflow:auto;
  max-height:220px;
  color:var(--text);
  border:1px solid rgba(255,255,255,0.03);
}
.suggestions div{ padding:10px; border-bottom:1px solid rgba(255,255,255,0.02); cursor:pointer; font-size:13px }
.suggestions div:hover{ background: rgba(255,255,255,0.02) }
.suggestions .muted{ color:var(--muted); font-size:12px; padding:8px }

/* legend */
#legend{ position:absolute; left:12px; bottom:12px; z-index:1200; background:var(--panel); padding:10px; border-radius:10px; color:var(--muted); font-size:13px }

/* map finish button */
#mapFinishBtn{ position:absolute; right:16px; top:76px; z-index:2000; display:none; padding:10px 14px; border-radius:10px; background:var(--accent); color:#04311a; font-weight:700; cursor:pointer; box-shadow:0 12px 30px rgba(2,6,23,0.6) }

/* pick toolbar */
#pickToolbar{
  position:absolute; left:50%; transform:translateX(-50%);
  bottom:18px; z-index:2000; display:none; gap:6px;
  background:#0b1324; border:1px solid rgba(255,255,255,0.06);
  padding:8px; border-radius:10px; box-shadow:0 10px 30px rgba(0,0,0,0.45);
}
.pickBtn{ padding:8px 10px; border-radius:8px; border:0; cursor:pointer; background:#0f203c; color:#e6eef6 }

/* thank you */
#thankYou{ position:fixed; left:50%; top:40%; transform:translate(-50%,-50%); z-index:3000; display:none; padding:18px 24px; border-radius:12px; background:linear-gradient(90deg,#10b981,#16a34a); color:#022; font-weight:800; box-shadow:0 20px 60px rgba(2,6,23,0.5); }

/* small top badge */
.toast{
  position:fixed; left:50%; transform:translateX(-50%); top:10%; z-index:4000;
  background:#0ea5a9; color:#022; padding:10px 14px; border-radius:8px; display:none;
}

/* modal panel generic */
.modal{ position:fixed; inset:0; display:none; align-items:center; justify-content:center; z-index:2600; background:rgba(0,0,0,0.5) }
.panel{ width:720px; max-height:86vh; overflow:auto; background:var(--panel); padding:16px; border-radius:12px; color:var(--text) }
</style>
</head>
<body>

  <div id="leftPanel">
    <h3>Flood Alert — Trivandrum</h3>

    <label class="small">Start</label>
    <div style="display:flex;gap:8px">
      <input id="startInput" class="input" placeholder="Type start or 'Current location'">
      <button id="useCurrentBtn" class="btn" style="padding:8px 10px">Current</button>
    </div>
    <div id="startSuggest" class="suggestions" style="display:none"></div>

    <label class="small">Destination</label>
    <input id="endInput" class="input" placeholder="Type destination">
    <div id="endSuggest" class="suggestions" style="display:none"></div>

    <div style="display:flex;gap:8px;margin-top:6px">
      <button id="getRouteBtn" class="btn">Get Route</button>
      <button id="findSafeBtn" class="btn" style="background:var(--safe); color:#fff; display:none">Find Fast & Safe Route</button>
    </div>

    <div id="routeInfo" class="small" style="margin-top:8px"></div>

    <div style="display:flex;gap:8px;margin-top:10px">
      <button id="reportBtn" class="btn" style="background:var(--danger); color:#420000">Report Flood</button>
    </div>

    <div style="margin-top:10px" id="weatherBadge" class="small" hidden></div>
  </div>

  <div id="legend">
    <div style="margin-bottom:6px"><strong>Legend</strong></div>
    <div style="display:flex;gap:8px;align-items:center"><div style="width:18px;height:10px;background:var(--danger)"></div><div class="small">Approved flooded road (red dotted)</div></div>
    <div style="display:flex;gap:8px;align-items:center"><div style="width:18px;height:10px;background:var(--pending)"></div><div class="small">Pending user report (orange dotted)</div></div>
    <div style="display:flex;gap:8px;align-items:center"><div style="width:18px;height:10px;background:var(--safe)"></div><div class="small">Safe alternate (dark green)</div></div>
  </div>

  <div id="map"></div>

  <button id="mapFinishBtn">Finish Report</button>
  <div id="thankYou">✅ Thank you — report submitted</div>
  <div id="undoToast" class="toast"></div>

  <!-- Pick-on-map toolbar -->
  <div id="pickToolbar">
    <button id="ptUndo" class="pickBtn">Undo</button>
    <button id="ptRedo" class="pickBtn">Redo</button>
    <button id="ptClear" class="pickBtn">Clear</button>
    <button id="ptCancel" class="pickBtn" style="background:#5b2333">Cancel</button>
  </div>

  <!-- Report modal -->
  <div id="reportModal" class="modal">
    <div class="panel">
      <h3 style="margin-top:0">Report Flooded Road</h3>
      <p class="small" style="line-height:1.6">
        <b>How to report:</b><br>
        1) Select severity and notes.<br>
        2) Click <b>Pick on Map</b>.<br>
        3) Tap along the flooded road (at least 2 points). Use <b>Undo/Redo/Clear</b> while drawing.<br>
        4) Click <b>Finish Report</b> at the top-right.<br>
        <i>Until admin approves, it will show as <b>Pending</b> (orange dashed) to all users.</i>
      </p>

      <div style="display:flex;gap:8px">
        <div style="flex:1">
          <label class="small">Severity</label>
          <select id="reportSeverity" class="input">
            <option>Moderate</option>
            <option>Low</option>
            <option>High</option>
          </select>
        </div>
        <div style="flex:2">
          <label class="small">Notes (optional)</label>
          <input id="reportNotes" class="input" placeholder="Landmark, depth, etc.">
        </div>
      </div>

      <div style="display:flex;gap:8px;margin-top:8px">
        <button id="pickRoadBtn" class="btn">Pick on Map</button>
        <button id="closeReportBtn" class="btn" style="background:#334155;color:#fff">Cancel</button>
      </div>
    </div>
  </div>

<script>
/* ================== BROADCAST SYNC ================== */
const bc = new BroadcastChannel('flood-sync');
function bcSend(msg){ try{ bc.postMessage(msg);}catch(e){} }
bc.onmessage = (e)=>{
  const m=e.data||{};
  if(m.type==='db-changed'){
    renderApprovedRoads();
    renderPendingReports();
  }
};

/* ================== LOCAL STORAGE HELPERS ================== */
function lsGet(k, def){ try{ const v = localStorage.getItem(k); return v ? JSON.parse(v) : def; } catch(e){ return def; } }
function lsSet(k, v){ localStorage.setItem(k, JSON.stringify(v)); }
function genId(){ return 'id'+Math.random().toString(36).slice(2,9); }

/* ================== CONFIG ================== */
const OWM_KEY = 'ce70bf8bdb2bbf3ad192ee196735d6cf';
const VIEWBOX = '76.7,8.7,77.2,8.3'; // Trivandrum bbox for suggestions

/* ================== MAP INIT & ICONS ================== */
const bounds = L.latLngBounds([8.3,76.7],[8.7,77.2]);
const map = L.map('map',{minZoom:11,maxZoom:18,maxBounds:bounds}).setView([8.5241,76.9366],13);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19}).addTo(map);
if(OWM_KEY) L.tileLayer(`https://tile.openweathermap.org/map/precipitation_new/{z}/{x}/{y}.png?appid=${OWM_KEY}`,{opacity:0.55}).addTo(map);

/* start/end icons */
const startIcon = L.divIcon({ className: 'start-icon', html: `<div style="background:#2563eb;border-radius:50%;width:18px;height:18px;border:3px solid white"></div>`, iconSize:[24,24], iconAnchor:[12,24]});
const endIcon = L.divIcon({ className: 'end-icon', html: `<div style="background:#ef4444;border-radius:50%;width:18px;height:18px;border:3px solid white"></div>`, iconSize:[24,24], iconAnchor:[12,24]});

/* ================== SUGGEST (Nominatim) ================== */
async function nominatim(q){
  if(!q) return [];
  const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(q)}&limit=6&viewbox=${VIEWBOX}&bounded=1`;
  try{ const r = await fetch(url, {headers:{'Accept-Language':'en'}}); if(!r.ok) return []; return r.json(); } catch(e){ return []; }
}
function positionSuggest(inputEl, boxEl){
  const r = inputEl.getBoundingClientRect();
  boxEl.style.left = (r.left + window.scrollX) + 'px';
  boxEl.style.top = (r.bottom + window.scrollY + 6) + 'px';
  boxEl.style.width = r.width + 'px';
}
function attachSuggest(inputEl, boxEl){
  let t=null;
  inputEl.addEventListener('input', ()=>{ clearTimeout(t); const q=inputEl.value.trim(); if(!q){ boxEl.style.display='none'; boxEl.innerHTML=''; return; } t=setTimeout(async ()=>{ const res = await nominatim(q); boxEl.innerHTML=''; if(!res || res.length===0){ const d=document.createElement('div'); d.className='muted'; d.innerText='No results in Trivandrum'; boxEl.appendChild(d); } else { res.forEach(it=>{ const div=document.createElement('div'); div.innerHTML = `📍 ${it.display_name}`; div.onclick = ()=>{ inputEl.value = it.display_name; inputEl._latlng=[parseFloat(it.lat), parseFloat(it.lon)]; boxEl.style.display='none'; boxEl.innerHTML=''; }; boxEl.appendChild(div); }); } positionSuggest(inputEl, boxEl); boxEl.style.display='block'; },250); });
  inputEl.addEventListener('blur', ()=>{ setTimeout(()=>{ boxEl.style.display='none'; },200); });
}
attachSuggest(document.getElementById('startInput'), document.getElementById('startSuggest'));
attachSuggest(document.getElementById('endInput'), document.getElementById('endSuggest'));

/* ================== GEO & WEATHER ================== */
let userPos=null, userMarker=null;
if(navigator.geolocation){
  navigator.geolocation.watchPosition(p=>{
    userPos=[p.coords.latitude,p.coords.longitude];
    if(!userMarker) userMarker = L.circleMarker(userPos,{radius:7,fillColor:'#06b6d4',color:'#fff',weight:2}).addTo(map).bindPopup('You are here');
    else userMarker.setLatLng(userPos);
    updateWeather(userPos[0], userPos[1]);
  }, err=>{ console.warn(err); }, { enableHighAccuracy:true, maximumAge:5000 });
} else updateWeather(8.5241,76.9366);
async function updateWeather(lat, lon){
  try{
    const url = `https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lon}&units=metric&appid=${OWM_KEY}`;
    const r = await fetch(url);
    if(!r.ok) return;
    const j = await r.json();
    const badge = document.getElementById('weatherBadge'); badge.hidden = false;
    const rain = (j.rain && j.rain['1h']) ? ` · Rain(1h): ${j.rain['1h']}mm` : '';
    badge.innerHTML = `<b>Weather</b><br>${Math.round(j.main.temp)}°C · Hum ${j.main.humidity}%${rain}`;
  }catch(e){ console.warn('weather failed', e); }
}

/* ================== DATA (roads, reports, meta) ================== */
function getRoads(){ return lsGet('roads', []); }        // approved flooded roads [{id,coords,severity}]
function setRoads(arr){ lsSet('roads', arr); }
function getReports(){ return lsGet('reports', []); }     // pending reports [{id,coords,text,time,status,severity}]
function setReports(arr){ lsSet('reports', arr); }
function getMeta(){ return lsGet('meta', { showPendingOnUser:true, activity:[] }); }
function setMeta(m){ lsSet('meta', m); }

/* seed demo once */
(function seedDemo(){
  if(getRoads().length===0){
    setRoads([
      { id: genId(), coords:[[8.5280,76.9350],[8.5285,76.9370]], severity:'Moderate' },
      { id: genId(), coords:[[8.5150,76.9550],[8.5160,76.9560]], severity:'Low' }
    ]);
  }
})();

/* ================== RENDER LAYERS ================== */
let approvedLayers={}, pendingLayers={};
function clearLayerDict(dict){ Object.values(dict).forEach(l=>{ try{ map.removeLayer(l);}catch(e){} }); Object.keys(dict).forEach(k=> delete dict[k]); }

function renderApprovedRoads(){
  clearLayerDict(approvedLayers);
  getRoads().forEach(r=>{
    const l = L.polyline(r.coords, { color:'var(--danger)', weight:5, dashArray:'8,8' }).addTo(map);
    l.bindPopup(`Flooded road (verified)${r.severity ? ' — '+r.severity : ''}`);
    approvedLayers[r.id]=l;
  });
}
function renderPendingReports(){
  clearLayerDict(pendingLayers);
  const meta = getMeta();
  if(!meta.showPendingOnUser) return; // admin toggle
  getReports().filter(x=>x.status==='pending' || !x.status).forEach(r=>{
    const l = L.polyline(r.coords, { color:'var(--pending)', weight:5, dashArray:'8,8' }).addTo(map);
    l.bindPopup(`Reported by user — Pending admin approval${r.severity ? ' — '+r.severity : ''}${r.text ? '<br>Note: '+r.text : ''}`);
    pendingLayers[r.id]=l;
  });
}

/* ================== ROUTING ================== */
function pointToSegmentDistance(pt,A,B){
  const toRad = Math.PI/180;
  const R = 6371000;
  const latRef = pt[0]*toRad;
  const x1 = A[1]*toRad*Math.cos(latRef)*R, y1 = A[0]*toRad*R;
  const x2 = B[1]*toRad*Math.cos(latRef)*R, y2 = B[0]*toRad*R;
  const x3 = pt[1]*toRad*Math.cos(latRef)*R, y3 = pt[0]*toRad*R;
  const dx = x2-x1, dy = y2-y1;
  if(dx===0 && dy===0) return Math.hypot(x3-x1, y3-y1);
  const t = ((x3-x1)*dx + (y3-y1)*dy) / (dx*dx + dy*dy);
  const tt = Math.max(0, Math.min(1, t));
  const xc = x1 + dx*tt, yc = y1 + dy*tt;
  return Math.hypot(x3-xc, y3-yc);
}
function detectFloodHitsOnRoute(routeCoords){
  const hits=[];
  const roads = getRoads();
  for(const road of roads){
    let seg=null;
    for(const pt of routeCoords){
      let near=false;
      for(let i=0;i<road.coords.length-1;i++){
        if(pointToSegmentDistance(pt, road.coords[i], road.coords[i+1]) < 25){ near=true; break; }
      }
      if(near){ if(!seg) seg=[]; seg.push(pt); } else { if(seg){ hits.push({road, seg}); seg=null; } }
    }
    if(seg) hits.push({road, seg});
  }
  return hits;
}

async function osrmRoute(start, dest, via=null){
  const coords = `${start[1]},${start[0]};${via ? via[1]+','+via[0]+';' : ''}${dest[1]},${dest[0]}`;
  const url = `https://router.project-osrm.org/route/v1/driving/${coords}?overview=full&geometries=geojson`;
  const r = await fetch(url, { cache:'no-store' });
  if(!r.ok) throw new Error('Route service unavailable');
  const j = await r.json();
  if(!j.routes || j.routes.length===0) throw new Error('No route found');
  const coordsLatLng = j.routes[0].geometry.coordinates.map(c=>[c[1],c[0]]);
  return { coords: coordsLatLng, distance: j.routes[0].distance, duration: j.routes[0].duration };
}

let mainRouteLayer = null, altRouteLayer = null, floodedSegments = [], startMarker=null, endMarker=null;
function setStartEndMarkers(startCoords, endCoords){
  if(startMarker) try{ map.removeLayer(startMarker);}catch(e){}
  if(endMarker) try{ map.removeLayer(endMarker);}catch(e){}
  startMarker = L.marker(startCoords, {icon:startIcon}).addTo(map).bindPopup('Start');
  endMarker = L.marker(endCoords, {icon:endIcon}).addTo(map).bindPopup('Destination');
}

document.getElementById('getRouteBtn').addEventListener('click', async ()=>{
  try{
    if(mainRouteLayer) try{ map.removeLayer(mainRouteLayer);}catch(e){}
    if(altRouteLayer) try{ map.removeLayer(altRouteLayer);}catch(e){}
    floodedSegments.forEach(l=>{ try{ map.removeLayer(l);}catch(e){} }); floodedSegments=[];
    document.getElementById('findSafeBtn').style.display='none';
    document.getElementById('routeInfo').innerText = 'Calculating route...';

    const sVal = document.getElementById('startInput').value.trim();
    const eVal = document.getElementById('endInput').value.trim();
    if(!sVal || !eVal){ alert('Enter start & destination'); document.getElementById('routeInfo').innerText=''; return; }
    const start = await resolvePlace(sVal, document.getElementById('startInput'));
    const dest = await resolvePlace(eVal, document.getElementById('endInput'));
    if(!start || !dest){ alert('Could not resolve places'); document.getElementById('routeInfo').innerText=''; return; }

    setStartEndMarkers(start, dest);
    const main = await osrmRoute(start, dest);
    mainRouteLayer = L.polyline(main.coords, { color:'#1e40af', weight:6, opacity:0.95 }).addTo(map);
    map.fitBounds(mainRouteLayer.getBounds(), { padding:[60,60] });
    document.getElementById('routeInfo').innerText = `Route: ${(main.distance/1000).toFixed(2)} km · ${(main.duration/60).toFixed(1)} min`;

    const hits = detectFloodHitsOnRoute(main.coords);
    if(hits.length > 0){
      hits.forEach(h=>{
        const l = L.polyline(h.seg, { color:'var(--danger)', weight:6, dashArray:'10,8' }).addTo(map);
        floodedSegments.push(l);
      });
      document.getElementById('routeInfo').innerText += ' · Flood detected on route';
      const safeBtn = document.getElementById('findSafeBtn');
      safeBtn.style.display='inline-block';
      safeBtn.onclick = ()=> generateSafeAlternate(main.coords, start, dest);
    } else {
      document.getElementById('routeInfo').innerText += ' · No flooded roads on route';
    }
  }catch(e){ console.error(e); alert('Route error. Try different points or retry.'); document.getElementById('routeInfo').innerText=''; }
});

async function generateSafeAlternate(mainCoords, start, dest){
  try{
    document.getElementById('routeInfo').innerText = 'Generating safe alternate...';
    if(!mainCoords || mainCoords.length===0) return alert('No main route to base on');
    const hits = detectFloodHitsOnRoute(mainCoords);
    if(hits.length===0) { alert('No flooded segments to avoid'); return; }

    const hit = hits[0];
    const mid = hit.seg[Math.floor(hit.seg.length/2)];
    const offsetMeters = 300, offDeg = offsetMeters / 111000;
    const candidates = [
      [ mid[0] + offDeg, mid[1] - offDeg ],
      [ mid[0] - offDeg, mid[1] + offDeg ],
      [ mid[0] + offDeg, mid[1] + offDeg ],
      [ mid[0] - offDeg, mid[1] - offDeg ]
    ];

    let best = null;
    for(const via of candidates){
      try{
        const res = await osrmRoute(start, dest, via);
        const ins = detectFloodHitsOnRoute(res.coords);
        if(ins.length === 0){ best = res; break; }
        if(!best || res.duration < best.duration) best = res;
      }catch(err){ console.warn('candidate failed', err); }
    }
    if(!best) return alert('No alternate route found');

    if(mainRouteLayer) { try{ map.removeLayer(mainRouteLayer);}catch(e){} mainRouteLayer=null; }
    if(altRouteLayer) try{ map.removeLayer(altRouteLayer);}catch(e){}
    altRouteLayer = L.polyline(best.coords, { color: 'var(--safe)', weight:6 }).addTo(map);
    map.fitBounds(altRouteLayer.getBounds(), { padding:[60,60] });
    document.getElementById('routeInfo').innerText = `Safe alternate: ${(best.distance/1000).toFixed(2)} km · ${(best.duration/60).toFixed(1)} min`;
  }catch(e){ console.error(e); alert('Safe alternate error. Try again.'); }
}

/* ================== resolve place helper ================== */
async function resolvePlace(text, inputEl){
  if(!text) return null;
  if(text.toLowerCase().includes('current') && userPos) return userPos;
  if(inputEl && inputEl._latlng) return inputEl._latlng;
  const m = text.match(/(-?\d+(\.\d+)?)\s*[,;]\s*(-?\d+(\.\d+)?)/);
  if(m) return [parseFloat(m[1]), parseFloat(m[3])];
  const res = await nominatim(text);
  if(res && res.length>0) return [parseFloat(res[0].lat), parseFloat(res[0].lon)];
  return null;
}
document.getElementById('useCurrentBtn').addEventListener('click', ()=>{ if(userPos){ document.getElementById('startInput').value='Current location'; document.getElementById('startInput')._latlng = userPos; } else alert('Allow location'); });

/* ================== REPORT FLOW (with Undo/Redo while drawing) ================== */
let reportPickMode=false, reportDrawPts=[], redoStack=[], reportPreview=null, lastSubmittedId=null, undoTimer=null;
const reportModal = document.getElementById('reportModal');

document.getElementById('reportBtn').addEventListener('click', ()=>{ reportModal.style.display='flex'; });
document.getElementById('closeReportBtn').addEventListener('click', ()=>{ reportModal.style.display='none'; });

document.getElementById('pickRoadBtn').addEventListener('click', ()=>{
  reportModal.style.display='none';
  startPickMode();
});

function startPickMode(){
  reportPickMode=true; reportDrawPts=[]; redoStack=[];
  if(reportPreview) try{ map.removeLayer(reportPreview);}catch(e){}
  document.getElementById('mapFinishBtn').style.display='inline-block';
  document.getElementById('pickToolbar').style.display='flex';
  toast('Tap map to add points (≥2). Use Undo/Redo. Finish when done.', 3000);
}
map.on('click', function(e){
  if(reportPickMode){
    reportDrawPts.push([e.latlng.lat, e.latlng.lng]);
    redoStack=[]; // reset redo after new add
    redrawPreview();
  }
});
function redrawPreview(){
  if(reportPreview) try{ map.removeLayer(reportPreview);}catch(e){}
  if(reportDrawPts.length>0){
    reportPreview = L.polyline(reportDrawPts, { color:'#f97316', weight:5, dashArray:'6,6' }).addTo(map);
  }
}
document.getElementById('ptUndo').addEventListener('click', ()=>{
  if(!reportPickMode || reportDrawPts.length===0) return;
  redoStack.push(reportDrawPts.pop());
  redrawPreview();
});
document.getElementById('ptRedo').addEventListener('click', ()=>{
  if(!reportPickMode || redoStack.length===0) return;
  reportDrawPts.push(redoStack.pop());
  redrawPreview();
});
document.getElementById('ptClear').addEventListener('click', ()=>{
  if(!reportPickMode) return;
  reportDrawPts=[]; redoStack=[];
  redrawPreview();
});
document.getElementById('ptCancel').addEventListener('click', ()=>{
  cancelPick();
  toast('Cancelled', 1200);
});

document.getElementById('mapFinishBtn').addEventListener('click', async ()=>{
  if(!reportPickMode) return;
  if(reportDrawPts.length < 2){ alert('Pick at least 2 points'); return; }
  const notes = document.getElementById('reportNotes').value.trim();
  const sev = document.getElementById('reportSeverity').value || 'Moderate';
  const rep = { id: genId(), coords: reportDrawPts.slice(), text: notes || '', time: Date.now(), status:'pending', severity:sev };
  const all = getReports(); all.unshift(rep); setReports(all);
  lastSubmittedId = rep.id;
  renderPendingReports();
  cancelPick();
  showThankYou();
  showUndoSubmitBar();
  bcSend({type:'db-changed'});
});

function cancelPick(){
  reportPickMode=false; reportDrawPts=[]; redoStack=[];
  if(reportPreview) try{ map.removeLayer(reportPreview);}catch(e){}
  reportPreview=null;
  document.getElementById('mapFinishBtn').style.display='none';
  document.getElementById('pickToolbar').style.display='none';
  document.getElementById('reportNotes').value='';
  document.getElementById('reportSeverity').value='Moderate';
}
function showThankYou(){ const el = document.getElementById('thankYou'); el.style.display='block'; setTimeout(()=> el.style.display='none', 1200); }
function toast(msg, ms=2000){ const el = document.getElementById('undoToast'); el.innerText = msg; el.style.display='block'; setTimeout(()=> el.style.display='none', ms); }
function showUndoSubmitBar(){
  const el = document.getElementById('undoToast');
  el.innerHTML = `Report submitted — <button id="undoBtn" style="margin-left:8px;cursor:pointer">Undo (15s)</button>`;
  el.style.display='block';
  const btn = document.getElementById('undoBtn');
  btn.onclick = ()=>{
    clearTimeout(undoTimer);
    const arr = getReports().filter(x=>x.id !== lastSubmittedId);
    setReports(arr);
    lastSubmittedId=null;
    el.style.display='none';
    renderPendingReports();
    bcSend({type:'db-changed'});
    toast('Report undone', 1200);
  };
  undoTimer = setTimeout(()=>{ el.style.display='none'; lastSubmittedId=null; }, 15000);
}

/* ================== INIT ================== */
function init(){
  renderApprovedRoads();
  renderPendingReports();
  setTimeout(()=>{ 
    positionSuggest(document.getElementById('startInput'), document.getElementById('startSuggest')); 
    positionSuggest(document.getElementById('endInput'), document.getElementById('endSuggest')); 
  }, 300);
}
init();
</script>
</body>
</html>
