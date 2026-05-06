/*
  CRISIS SENTINEL // Sci-Fi HUD Frontend
  Tactical threat monitoring interface
*/

let map = null, markers = [], radiusCircle = null, locationMarker = null;
let pollTimer = null, isScanning = false;
let scanLat = null, scanLon = null, scanRadius = 50;

// UTC Clock
setInterval(() => {
    const el = document.getElementById("utcClock");
    if (el) el.textContent = new Date().toISOString().substring(11, 19);
}, 1000);

// ============ SCAN ============

function startScan() {
    const loc = document.getElementById("locationInput").value.trim();
    const rad = parseInt(document.getElementById("radiusInput").value) || 50;
    if (!loc) { shakeEl(document.querySelector(".target-input .hud-input-wrap")); return; }

    const btn = document.getElementById("scanBtn");
    btn.disabled = true;
    btn.innerHTML = '<div class="btn-bg"></div><span class="spinner"></span><span>SCANNING...</span>';
    setStatus("Geocoding target location...");
    document.getElementById("headerStatus").textContent = "SCANNING";

    document.getElementById("statsBar").style.display = "block";
    document.getElementById("mainContent").style.display = "flex";
    if (!map) setTimeout(initMap, 100);

    // Animate status ring
    const ring = document.getElementById("statusRing");
    if (ring) ring.style.animation = "ringSpin 2s linear infinite";

    fetch("/api/scan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ location: loc, radius: rad }),
    })
    .then(r => r.json())
    .then(data => {
        if (data.error) { setStatus("ERROR: " + data.error); resetBtn(); return; }
        scanLat = data.lat; scanLon = data.lon; scanRadius = data.radius_km;
        setStatus(`Scanning ${loc.toUpperCase()} // ${rad}km radius...`);
        document.getElementById("coordDisplay").textContent =
            `${scanLat.toFixed(4)}, ${scanLon.toFixed(4)}`;
        if (map) updateMapCenter(scanLat, scanLon, scanRadius, loc);
        isScanning = true;
        startPolling();
    })
    .catch(() => { setStatus("CONNECTION FAILED"); resetBtn(); });
}

function resetBtn() {
    const btn = document.getElementById("scanBtn");
    btn.disabled = false;
    btn.innerHTML = `<div class="btn-bg"></div>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <polygon points="5,3 19,12 5,21"/></svg><span>INITIATE SCAN</span>`;
    document.getElementById("headerStatus").textContent = "STANDBY";
    const ring = document.getElementById("statusRing");
    if (ring) ring.style.animation = "";
}

function shakeEl(el) {
    el.style.animation = "shake 0.4s ease";
    setTimeout(() => el.style.animation = "", 400);
}

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("locationInput").addEventListener("keypress", e => { if (e.key === "Enter") startScan(); });
    document.getElementById("radiusInput").addEventListener("keypress", e => { if (e.key === "Enter") startScan(); });
});

// ============ POLLING ============

function startPolling() {
    if (pollTimer) clearInterval(pollTimer);
    pollTimer = setInterval(fetchResults, 2000);
    fetchResults();
}

function fetchResults() {
    fetch("/api/results").then(r => r.json()).then(data => {
        updateStats(data);
        updateFeed(data.results);
        updateMapMarkers(data.results);
        updateSources(data.source_counts || {});
        showErrors(data.errors);
        updateClassification(data.results);

        if (!data.is_scanning && isScanning) {
            isScanning = false;
            clearInterval(pollTimer);
            setStatus(`SCAN COMPLETE // ${data.total_scanned} posts // ${data.crisis_count} crisis events`);
            resetBtn();
            document.getElementById("headerStatus").textContent = `${data.total_scanned} POSTS`;
            document.getElementById("mapBadge").textContent = `${data.crisis_count} CRISIS EVENTS`;

            // Threat bar
            const pct = data.total_scanned > 0 ? (data.crisis_count / data.total_scanned * 100) : 0;
            const bar = document.getElementById("threatBarFill");
            if (bar) bar.style.width = pct + "%";
        }
    }).catch(e => console.error("Poll error:", e));
}

// ============ UI UPDATES ============

function updateStats(data) {
    animNum("totalCount", data.total_scanned);
    animNum("crisisCount", data.crisis_count);
    animNum("safeCount", data.total_scanned - data.crisis_count);
    const sources = new Set(data.results.map(r => r.source));
    animNum("sourceCount", sources.size);
}

function animNum(id, target) {
    const el = document.getElementById(id);
    const cur = parseInt(el.textContent) || 0;
    if (cur === target) return;
    const diff = target - cur, steps = Math.min(Math.abs(diff), 12), ss = diff / steps;
    let s = 0;
    const iv = setInterval(() => {
        s++;
        if (s >= steps) { el.textContent = String(target).padStart(3, "0"); clearInterval(iv); }
        else el.textContent = String(Math.round(cur + ss * s)).padStart(3, "0");
    }, 35);
}

function updateSources(sc) {
    const c = document.getElementById("sourceFilters");
    if (!sc || !Object.keys(sc).length) { c.innerHTML = ""; return; }
    const labels = { reddit:"REDDIT", twitter:"TWITTER", twitter_nitter:"TWITTER",
        instagram:"INSTAGRAM", threads:"THREADS", bluesky:"BLUESKY",
        gdelt:"GDELT", google_news:"NEWS" };
    c.innerHTML = Object.entries(sc).map(([s, n]) =>
        `<span class="source-pill">${labels[s]||s} <span class="pill-count">${n}</span></span>`
    ).join("");
}

function updateFeed(results) {
    const feed = document.getElementById("feed");
    document.getElementById("feedCount").textContent = results.length + " POSTS";

    if (!results.length) {
        if (isScanning) feed.innerHTML = `<div class="feed-empty">
            <span class="spinner" style="width:20px;height:20px;border-width:2px"></span>
            <p class="mono">INTERCEPTING SIGNALS...</p></div>`;
        return;
    }

    const labels = { reddit:"REDDIT", twitter:"TWITTER", twitter_nitter:"TWITTER",
        instagram:"INSTA", threads:"THREADS", bluesky:"BSKY",
        gdelt:"GDELT", google_news:"NEWS" };

    feed.innerHTML = results.map((item, i) => {
        const cls = item.is_crisis ? "crisis" : "safe";
        const badge = item.is_crisis
            ? '<span class="badge crisis-badge">CRISIS</span>'
            : '<span class="badge safe-badge">CLEAR</span>';
        const src = labels[item.source] || item.source;
        const conf = Math.round(item.confidence * 100) + "%";

        return `<div class="feed-item ${cls}" style="animation-delay:${i*0.025}s">
            <div class="badges">${badge}<span class="badge source-badge">${src}</span></div>
            <div class="text">${escapeHtml(item.text)}</div>
            <div class="meta">
                <span>${conf}</span><span>|</span><span>${src}</span>
                ${item.url ? `<span>|</span><a href="${item.url}" target="_blank" rel="noopener">LINK→</a>` : ""}
            </div>
        </div>`;
    }).join("");
}

function showErrors(errors) {
    const s = document.getElementById("errorSection");
    const l = document.getElementById("errorList");
    if (!errors || !Object.keys(errors).length) { s.style.display = "none"; return; }
    s.style.display = "block";
    l.innerHTML = Object.entries(errors).map(([k,v]) =>
        `<div>► ${k.toUpperCase()}: ${escapeHtml(v)}</div>`
    ).join("");
}

function setStatus(msg) {
    const el = document.getElementById("statusText");
    el.innerHTML = isScanning ? '<span class="spinner"></span>' + msg : msg;
}

// ============ MAP ============

function initMap() {
    if (map) return;
    map = L.map("map", { zoomControl: true, attributionControl: false })
        .setView([20.5937, 78.9629], 5);

    // Dark sci-fi tiles
    L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
        maxZoom: 19, subdomains: "abcd"
    }).addTo(map);

    L.control.attribution({ prefix: false, position: "bottomleft" })
        .addAttribution('CARTO').addTo(map);
}

function updateMapCenter(lat, lon, rkm, name) {
    if (!map) return;
    const zoom = rkm > 500 ? 5 : rkm > 200 ? 7 : rkm > 50 ? 9 : 11;
    map.setView([lat, lon], zoom);

    if (radiusCircle) map.removeLayer(radiusCircle);
    if (locationMarker) map.removeLayer(locationMarker);

    // Scan radius circle
    radiusCircle = L.circle([lat, lon], {
        radius: rkm * 1000, color: "#00f0ff", fillColor: "#00f0ff",
        fillOpacity: 0.04, weight: 1, dashArray: "10,8",
    }).addTo(map);

    // Center pin
    locationMarker = L.marker([lat, lon], {
        icon: L.divIcon({
            className: "", iconSize: [16, 16], iconAnchor: [8, 8],
            html: `<div style="width:16px;height:16px;border-radius:50%;
                border:2px solid #00f0ff;background:rgba(0,240,255,0.3);
                box-shadow:0 0 20px rgba(0,240,255,0.4),0 0 40px rgba(0,240,255,0.15);"></div>`
        })
    }).addTo(map);

    locationMarker.bindPopup(
        `<div style="font-family:'Orbitron',sans-serif;font-size:11px;color:#00f0ff;letter-spacing:1px;">
            ${escapeHtml(name.toUpperCase())}
            <div style="font-family:'Share Tech Mono',monospace;font-size:10px;color:#6a7a8a;margin-top:3px;">
                ${lat.toFixed(4)}, ${lon.toFixed(4)} // ${rkm}KM
            </div></div>`
    ).openPopup();
}

function updateMapMarkers(results) {
    if (!map) return;
    markers.forEach(m => map.removeLayer(m));
    markers = [];
    if (!scanLat || !scanLon || !results.length) return;

    let ci = 0;
    results.forEach(item => {
        if (!item.is_crisis) return;
        ci++;
        const a = ci * 137.508 * Math.PI / 180;
        const d = (Math.random() * 0.6 + 0.15) * scanRadius / 111;
        const lt = scanLat + d * Math.cos(a);
        const ln = scanLon + d * Math.sin(a) / Math.cos(scanLat * Math.PI / 180);

        const clr = item.confidence > 0.7 ? "#ff2244" : item.confidence > 0.4 ? "#ffaa00" : "#ffdd00";

        const m = L.circleMarker([lt, ln], {
            radius: 6, fillColor: clr, color: clr,
            weight: 1, fillOpacity: 0.8,
        }).addTo(map);

        const labels = { reddit:"REDDIT", twitter:"TWITTER", twitter_nitter:"TWITTER",
            instagram:"INSTA", threads:"THREADS", bluesky:"BSKY",
            gdelt:"GDELT", google_news:"NEWS" };

        m.bindPopup(`<div style="font-family:'Rajdhani',sans-serif;max-width:240px;">
            <div style="font-family:'Orbitron',sans-serif;font-size:10px;color:${clr};letter-spacing:1px;margin-bottom:4px;">
                CRISIS // ${labels[item.source]||item.source}
            </div>
            <div style="font-size:12px;color:#c8dce8;line-height:1.4;">
                ${escapeHtml(item.text.substring(0, 160))}...
            </div>
            <div style="font-family:'Share Tech Mono',monospace;font-size:10px;color:#6a7a8a;margin-top:4px;">
                CONFIDENCE: <span style="color:${clr}">${Math.round(item.confidence*100)}%</span>
            </div></div>`);

        markers.push(m);
    });

    document.getElementById("mapBadge").textContent = markers.length + " CRISIS EVENTS";

    // Show map toggle
    document.getElementById("mapToggle").style.display = "flex";
}

// ============ HEAT MAP ============

let heatLayer = null;
let currentMapView = "markers";
let lastResults = [];

function setMapView(view) {
    currentMapView = view;
    document.getElementById("markerViewBtn").classList.toggle("active", view === "markers");
    document.getElementById("heatViewBtn").classList.toggle("active", view === "heat");

    if (view === "heat") {
        // Hide markers, show heat
        markers.forEach(m => map.removeLayer(m));
        showHeatMap(lastResults);
    } else {
        // Hide heat, show markers
        if (heatLayer) { map.removeLayer(heatLayer); heatLayer = null; }
        updateMapMarkers(lastResults);
    }
}

function showHeatMap(results) {
    if (!map || !scanLat || !scanLon) return;
    if (heatLayer) { map.removeLayer(heatLayer); heatLayer = null; }

    const points = [];
    let ci = 0;
    results.forEach(item => {
        if (!item.is_crisis) return;
        ci++;
        const a = ci * 137.508 * Math.PI / 180;
        const d = (Math.random() * 0.6 + 0.15) * scanRadius / 111;
        const lt = scanLat + d * Math.cos(a);
        const ln = scanLon + d * Math.sin(a) / Math.cos(scanLat * Math.PI / 180);
        points.push([lt, ln, item.confidence]);
    });

    if (points.length > 0 && typeof L.heatLayer !== "undefined") {
        heatLayer = L.heatLayer(points, {
            radius: 30, blur: 20, maxZoom: 17, max: 1.0,
            gradient: { 0.2: 'rgba(255, 34, 68, 0.2)', 0.4: 'rgba(255, 34, 68, 0.4)', 0.6: 'rgba(255, 34, 68, 0.6)', 0.8: 'rgba(255, 34, 68, 0.8)', 1.0: '#ff2244' }
        }).addTo(map);
    }
}

// ============ CLASSIFICATION RESULTS ============

function updateClassification(results) {
    if (!results || !results.length) return;

    document.getElementById("classificationSection").style.display = "block";
    lastResults = results;

    // 1. Confidence Distribution
    const confBars = document.getElementById("confBars");
    const high = results.filter(r => r.confidence >= 0.7).length;
    const med = results.filter(r => r.confidence >= 0.4 && r.confidence < 0.7).length;
    const low = results.filter(r => r.confidence < 0.4).length;
    const total = results.length || 1;

    confBars.innerHTML = `
        <div class="conf-row">
            <span class="conf-label">HIGH &gt;70%</span>
            <div class="conf-bar-track"><div class="conf-bar-fill high" style="width:${high/total*100}%"></div></div>
            <span class="conf-count">${high}</span>
        </div>
        <div class="conf-row">
            <span class="conf-label">MED 40-70%</span>
            <div class="conf-bar-track"><div class="conf-bar-fill med" style="width:${med/total*100}%"></div></div>
            <span class="conf-count">${med}</span>
        </div>
        <div class="conf-row">
            <span class="conf-label">LOW &lt;40%</span>
            <div class="conf-bar-track"><div class="conf-bar-fill low" style="width:${low/total*100}%"></div></div>
            <span class="conf-count">${low}</span>
        </div>`;

    // 2. Source Breakdown
    const srcDiv = document.getElementById("sourceBreakdown");
    const srcCounts = {};
    const srcCrisis = {};
    results.forEach(r => {
        srcCounts[r.source] = (srcCounts[r.source] || 0) + 1;
        if (r.is_crisis) srcCrisis[r.source] = (srcCrisis[r.source] || 0) + 1;
    });
    const maxSrc = Math.max(...Object.values(srcCounts), 1);
    const labels = { reddit:"REDDIT", twitter:"TWITTER", twitter_nitter:"TWITTER",
        instagram:"INSTA", threads:"THREADS", bluesky:"BSKY",
        gdelt:"GDELT", google_news:"NEWS" };

    srcDiv.innerHTML = Object.entries(srcCounts).map(([s, n]) => {
        const crisis = srcCrisis[s] || 0;
        return `<div class="src-row">
            <span class="src-name">${labels[s]||s}</span>
            <div class="src-bar-track"><div class="src-bar-fill" style="width:${n/maxSrc*100}%"></div></div>
            <span class="src-stats">${n} / ${crisis}⚠</span>
        </div>`;
    }).join("");

    // 3. Keywords
    const kwDiv = document.getElementById("keywordCloud");
    const crisisWords = {};
    const keywords = ["flood","earthquake","fire","storm","disaster","crisis","emergency",
        "cyclone","attack","accident","explosion","collapse","drought","tsunami","landslide",
        "rescue","damage","killed","injured","evacuation","warning","alert","death","destroyed"];

    results.forEach(r => {
        if (!r.is_crisis) return;
        const txt = r.text.toLowerCase();
        keywords.forEach(kw => {
            if (txt.includes(kw)) crisisWords[kw] = (crisisWords[kw] || 0) + 1;
        });
    });

    const sorted = Object.entries(crisisWords).sort((a,b) => b[1] - a[1]).slice(0, 12);
    const maxKw = sorted.length > 0 ? sorted[0][1] : 1;

    kwDiv.innerHTML = sorted.map(([kw, cnt]) => {
        const cls = cnt / maxKw > 0.6 ? "hot" : cnt / maxKw > 0.3 ? "warm" : "cool";
        return `<span class="keyword-tag ${cls}">${kw.toUpperCase()} (${cnt})</span>`;
    }).join("") || '<span class="keyword-tag cool">NO KEYWORDS DETECTED</span>';
}

// ============ UTILS ============

function escapeHtml(t) { const d = document.createElement("div"); d.textContent = t; return d.innerHTML; }

// Inject shake animation
(function(){
    const s = document.createElement("style");
    s.textContent = `
        @keyframes shake { 0%,100%{transform:translateX(0)} 20%{transform:translateX(-6px)}
            40%{transform:translateX(6px)} 60%{transform:translateX(-4px)} 80%{transform:translateX(4px)} }
        @keyframes ringSpin { to{stroke-dashoffset:0} }
    `;
    document.head.appendChild(s);
})();
