import React, { useState, useEffect, useRef, useMemo, useCallback } from "react";
import * as THREE from "three";
import {
  Satellite, Radar, Ship, AlertTriangle, TrendingUp, MapPin, Clock,
  CheckCircle2, ArrowRight, ArrowLeft, FileText, Download, RotateCcw,
  Layers, Activity, Compass, Wind, Navigation2, Target, Search,
  ChevronRight, Anchor, Waves, Gauge, Crosshair, ScanLine, FileCheck2,
  ShieldAlert, Info
} from "lucide-react";

/* ============================================================================
   SAGARDRHISTI — Marine Intelligence Platform
   Design system: deep-ocean instrument panel. Corner-bracket framing (viewfinder
   motif) replaces card+shadow chrome. Two type roles: a light, wide-tracked
   display face for narrative copy, and a tabular-numeral technical face for
   every reading, coordinate and score. Numbering is used only where the
   content is a genuine sequence (the investigation pipeline).
   ============================================================================ */

const TOKENS = {
  bg: "#031018",
  navy: "#061D2A",
  navy2: "#0A2A3D",
  ocean: "#07527A",
  babyblue: "#8DDCF7",
  cyan: "#35C9F5",
  white: "#F5FAFC",
  oil: "#D99A3D",
  warning: "#F5B942",
  critical: "#FF5B5B",
};

/* ---------------------------------------------------------------------------
   Global style block
--------------------------------------------------------------------------- */
function GlobalStyles() {
  return (
    <style>{`
      .sgd-root, .sgd-root * { box-sizing: border-box; }
      .sgd-root {
        --bg:${TOKENS.bg}; --navy:${TOKENS.navy}; --navy2:${TOKENS.navy2};
        --ocean:${TOKENS.ocean}; --babyblue:${TOKENS.babyblue}; --cyan:${TOKENS.cyan};
        --white:${TOKENS.white}; --oil:${TOKENS.oil}; --warning:${TOKENS.warning};
        --critical:${TOKENS.critical};
        background: var(--bg);
        color: var(--white);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, Helvetica, Arial, sans-serif;
        min-height: 100vh;
        width: 100%;
        position: relative;
        overflow-x: hidden;
      }
      .sgd-mono {
        font-family: "SF Mono", "Roboto Mono", ui-monospace, Menlo, Consolas, monospace;
        font-variant-numeric: tabular-nums;
        letter-spacing: 0.02em;
      }
      .sgd-display {
        font-weight: 300;
        letter-spacing: 0.01em;
      }
      .sgd-label {
        font-family: "SF Mono", "Roboto Mono", ui-monospace, Menlo, Consolas, monospace;
        font-size: 11px;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: #6FA8C4;
      }
      .sgd-scrollbar::-webkit-scrollbar { width: 6px; height: 6px; }
      .sgd-scrollbar::-webkit-scrollbar-thumb { background: #10475F; border-radius: 3px; }
      .sgd-scrollbar::-webkit-scrollbar-track { background: transparent; }

      @keyframes sgdFadeUp { from { opacity:0; transform: translateY(14px);} to {opacity:1; transform:translateY(0);} }
      @keyframes sgdFadeIn { from {opacity:0;} to {opacity:1;} }
      @keyframes sgdPulse { 0%,100% {opacity:1;} 50%{opacity:0.35;} }
      @keyframes sgdScan { 0% { transform: translateY(-100%);} 100% { transform: translateY(100%);} }
      @keyframes sgdDrift { 0% { background-position: 0 0; } 100% { background-position: 240px 240px; } }
      @keyframes sgdBob { 0%,100% { transform: translateY(0);} 50% { transform: translateY(-6px);} }
      @keyframes sgdSweep { 0% { transform: rotate(0deg);} 100% { transform: rotate(360deg);} }

      .sgd-enter { animation: sgdFadeUp 0.6s cubic-bezier(.16,.8,.24,1) both; }
      .sgd-enter-1 { animation-delay: .05s; }
      .sgd-enter-2 { animation-delay: .12s; }
      .sgd-enter-3 { animation-delay: .19s; }
      .sgd-enter-4 { animation-delay: .26s; }

      .sgd-bracket { position: relative; }
      .sgd-bracket::before, .sgd-bracket::after,
      .sgd-bracket .sgd-bl, .sgd-bracket .sgd-br {
        content: ""; position: absolute; width: 14px; height: 14px;
        border-color: #2C7A9E; opacity: 0.85; transition: opacity .25s, border-color .25s;
      }
      .sgd-bracket::before { top: -1px; left: -1px; border-top: 1.5px solid; border-left: 1.5px solid; }
      .sgd-bracket::after { top: -1px; right: -1px; border-top: 1.5px solid; border-right: 1.5px solid; }
      .sgd-bracket .sgd-bl { bottom: -1px; left: -1px; border-bottom: 1.5px solid; border-left: 1.5px solid; }
      .sgd-bracket .sgd-br { bottom: -1px; right: -1px; border-bottom: 1.5px solid; border-right: 1.5px solid; }
      .sgd-bracket:hover::before, .sgd-bracket:hover::after,
      .sgd-bracket:hover .sgd-bl, .sgd-bracket:hover .sgd-br { border-color: var(--cyan); opacity: 1; }

      .sgd-btn-primary {
        background: linear-gradient(180deg, #4FD3F7, #1FA8DE);
        color: #04141F; font-weight: 600; border: none; cursor: pointer;
        padding: 14px 28px; font-size: 14px; letter-spacing: 0.03em;
        transition: transform .2s ease, box-shadow .2s ease, filter .2s ease;
        box-shadow: 0 0 0 rgba(53,201,245,0);
      }
      .sgd-btn-primary:hover { filter: brightness(1.08); box-shadow: 0 8px 30px -8px rgba(53,201,245,0.55); transform: translateY(-1px); }
      .sgd-btn-primary:active { transform: translateY(0px) scale(0.99); }

      .sgd-btn-ghost {
        background: transparent; color: var(--babyblue);
        border: 1px solid #204a5f; cursor: pointer;
        padding: 13px 26px; font-size: 14px; letter-spacing: 0.03em;
        transition: border-color .2s ease, background .2s ease, color .2s;
      }
      .sgd-btn-ghost:hover { border-color: var(--cyan); background: rgba(53,201,245,0.06); color: var(--white); }

      .sgd-hairline { height: 1px; background: linear-gradient(90deg, transparent, #163B4E, transparent); }
      .sgd-vline { width: 1px; background: #133547; }

      .sgd-nav-item { transition: color .2s, background .2s, border-color .2s; }
      .sgd-nav-item:hover { color: var(--white) !important; }

      .sgd-row:hover { background: rgba(141,220,247,0.035); }

      .sgd-glow-text { text-shadow: 0 0 24px rgba(53,201,245,0.35); }
    `}</style>
  );
}

/* ---------------------------------------------------------------------------
   Small reusable atoms
--------------------------------------------------------------------------- */
function Bracket({ children, style, className = "" }) {
  return (
    <div className={`sgd-bracket ${className}`} style={style}>
      {children}
      <span className="sgd-bl" />
      <span className="sgd-br" />
    </div>
  );
}

function Reading({ label, value, unit, size = 22, color = TOKENS.white, align = "left" }) {
  return (
    <div style={{ textAlign: align }}>
      <div className="sgd-label" style={{ marginBottom: 6 }}>{label}</div>
      <div className="sgd-mono" style={{ fontSize: size, fontWeight: 600, color }}>
        {value}{unit && <span style={{ fontSize: size * 0.5, marginLeft: 4, color: "#6FA8C4", fontWeight: 500 }}>{unit}</span>}
      </div>
    </div>
  );
}

function StatusPill({ tone = "cyan", children }) {
  const map = {
    cyan: { c: TOKENS.cyan, bg: "rgba(53,201,245,0.10)" },
    warning: { c: TOKENS.warning, bg: "rgba(245,185,66,0.10)" },
    critical: { c: TOKENS.critical, bg: "rgba(255,91,91,0.10)" },
    oil: { c: TOKENS.oil, bg: "rgba(217,154,61,0.10)" },
    neutral: { c: "#8FB8CC", bg: "rgba(143,184,204,0.08)" },
  };
  const s = map[tone];
  return (
    <span className="sgd-label" style={{
      color: s.c, background: s.bg, border: `1px solid ${s.c}55`,
      padding: "6px 12px", display: "inline-flex", alignItems: "center", gap: 7
    }}>
      <span style={{ width: 5, height: 5, borderRadius: "50%", background: s.c, animation: "sgdPulse 2s ease-in-out infinite" }} />
      {children}
    </span>
  );
}

function ScoreBar({ value, max = 100, color = TOKENS.cyan, height = 6 }) {
  return (
    <div style={{ width: "100%", height, background: "#0C2A3A", position: "relative", overflow: "hidden" }}>
      <div style={{
        width: `${(value / max) * 100}%`, height: "100%",
        background: `linear-gradient(90deg, ${color}88, ${color})`,
        transition: "width 1s cubic-bezier(.16,.8,.24,1)"
      }} />
    </div>
  );
}

function SectionHead({ eyebrow, title, sub }) {
  return (
    <div style={{ marginBottom: 32 }}>
      {eyebrow && <div className="sgd-label" style={{ color: TOKENS.cyan, marginBottom: 10 }}>{eyebrow}</div>}
      <h2 className="sgd-display" style={{ fontSize: 30, margin: 0, color: TOKENS.white }}>{title}</h2>
      {sub && <p style={{ color: "#7FAEC7", fontSize: 15, marginTop: 10, maxWidth: 560, lineHeight: 1.6 }}>{sub}</p>}
    </div>
  );
}

function NavButtons({ onBack, onNext, backLabel = "Back", nextLabel = "Continue" }) {
  return (
    <div style={{ display: "flex", justifyContent: "space-between", marginTop: 48, paddingTop: 24, borderTop: "1px solid #0F3040" }}>
      <button className="sgd-btn-ghost" onClick={onBack} style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <ArrowLeft size={15} /> {backLabel}
      </button>
      <button className="sgd-btn-primary" onClick={onNext} style={{ display: "flex", alignItems: "center", gap: 8 }}>
        {nextLabel} <ArrowRight size={15} />
      </button>
    </div>
  );
}

/* Synthetic SAR-style texture, generated purely with SVG turbulence (no external imagery) */
function SyntheticTexture({ id, baseFrequency = 0.9, seed = 4, tint = "#0A2A3A", opacity = 1 }) {
  return (
    <filter id={id}>
      <feTurbulence type="fractalNoise" baseFrequency={baseFrequency} numOctaves={2} seed={seed} result="noise" />
      <feColorMatrix in="noise" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0.9 0.9 0.9 0 0" result="mono" />
      <feComponentTransfer in="mono" result="contrast">
        <feFuncA type="linear" slope="1.6" intercept="-0.25" />
      </feComponentTransfer>
      <feFlood floodColor={tint} result="tintColor" />
      <feComposite in="tintColor" in2="contrast" operator="in" result="tinted" />
      <feComposite in="tinted" in2="SourceGraphic" operator="over" />
    </filter>
  );
}

/* ---------------------------------------------------------------------------
   MOCK DATA
--------------------------------------------------------------------------- */
const CASE = {
  id: "CASE 2026-0417",
  status: "INVESTIGATION ACTIVE",
  detected: "27 AUG 2026 · 06:52 UTC",
  confidence: 95,
  area: 2.4,
  origin: "22.4°N, 69.1°E",
  age: "12–18 HRS",
  vessels: 14,
};

const AGENTS = [
  { key: "unet", name: "U-NET", type: "Pixel-level segmentation", confidence: 91, desc: "Encoder-decoder CNN trained on labelled Sentinel-1 spill masks. Outputs a per-pixel probability map." },
  { key: "deeplab", name: "DEEPLABV3+", type: "Semantic segmentation", confidence: 89, desc: "Atrous convolutions capture multi-scale slick geometry, from thin sheen to thick pooled oil." },
  { key: "transunet", name: "TRANSUNET", type: "Transformer-enhanced segmentation", confidence: 86, desc: "Transformer-enhanced segmentation captures long-range spatial context while preserving fine-grained spill boundaries." },
];

const CHARACTERIZATION = {
  area: 2.4, perimeter: 8.7, length: 3.8, width: 1.2, aspectRatio: 3.16, confidence: 95, age: "12–18 hours",
  shape: [
    { label: "Irregularity", value: 0.62, note: "Boundary deviates from a smooth ellipse — consistent with active weathering." },
    { label: "Elongation", value: 0.81, note: "Strong directional stretching along the surface current vector." },
    { label: "Compactness", value: 0.44, note: "Low compactness typical of a wind-sheared surface slick, not a point discharge." },
  ],
};

const DRIFT = {
  wind: { speed: 14, dir: "NE" },
  current: { speed: 0.8, dir: "E" },
  originTime: "27 AUG 03:40 UTC",
  detectionTime: "27 AUG 06:52 UTC",
  confidence: "HIGH",
  uncertainty: "±1.1 NM",
};

const VESSELS = [
  { rank: 1, name: "MV KESTREL", type: "Bulk Carrier", mmsi: "419002331", imo: "9284710", distance: 0.4, timeOffset: -22, speed: 8.4, heading: 118, trajectory: 91, behaviour: 84, aisGap: "12 min", score: 87, tier: "strongest", pos: { x: 61, y: 46 } },
  { rank: 2, name: "MT SEA ORCHID", type: "Chemical Tanker", mmsi: "419887210", imo: "9351102", distance: 2.1, timeOffset: -58, speed: 11.2, heading: 244, trajectory: 63, behaviour: 47, aisGap: "0 min", score: 54, tier: "potential", pos: { x: 38, y: 58 } },
  { rank: 3, name: "MV DEVI PRIYA", type: "General Cargo", mmsi: "419112873", imo: "9412093", distance: 4.8, timeOffset: -140, speed: 9.7, heading: 302, trajectory: 31, behaviour: 22, aisGap: "0 min", score: 22, tier: "normal", pos: { x: 74, y: 27 } },
  { rank: 4, name: "MT NAVIGATOR STAR", type: "Product Tanker", mmsi: "419664521", imo: "9198845", distance: 6.2, timeOffset: 84, speed: 12.9, heading: 78, trajectory: 24, behaviour: 18, aisGap: "0 min", score: 17, tier: "normal", pos: { x: 22, y: 70 } },
  { rank: 5, name: "MV BLUE HORIZON", type: "Container", mmsi: "419773098", imo: "9331177", distance: 8.9, timeOffset: -206, speed: 14.1, heading: 190, trajectory: 12, behaviour: 9, aisGap: "0 min", score: 9, tier: "normal", pos: { x: 84, y: 63 } },
  { rank: 6, name: "MT GULF PIONEER", type: "Crude Tanker", mmsi: "419228841", imo: "9276630", distance: 11.4, timeOffset: 172, speed: 10.3, heading: 15, trajectory: 8, behaviour: 6, aisGap: "0 min", score: 6, tier: "normal", pos: { x: 15, y: 20 } },
];

const EVIDENCE = [
  { label: "Spatial Proximity", score: 92, note: "Kestrel's reconstructed 03:40 UTC position sits 0.4 NM from the hindcast origin." },
  { label: "Temporal Correlation", score: 89, note: "Passage through the origin window precedes detection by 22 minutes." },
  { label: "Trajectory Match", score: 81, note: "Course and speed profile align with the drift-corrected backtrack path." },
  { label: "Behavioural Anomaly", score: 78, note: "Irregular speed reduction and a minor course deviation inside the origin window." },
  { label: "AIS Continuity", score: 64, note: "A 12-minute transmission gap overlaps the estimated discharge time." },
];

const PIPELINE_SCREENS = [
  { id: "overview", label: "Case Overview", icon: Layers },
  { id: "detection", step: "01", label: "Detection", icon: Satellite },
  { id: "ai-analysis", step: "02", label: "AI Analysis", icon: Activity },
  { id: "characterization", step: "03", label: "Characterization", icon: Crosshair },
  { id: "drift", step: "04", label: "Drift", icon: Compass },
  { id: "ais", step: "05", label: "AIS", icon: Radar },
  { id: "ranking", step: "06", label: "Ranking", icon: Gauge },
  { id: "evidence", step: "07", label: "Evidence", icon: ShieldAlert },
  { id: "report", step: "08", label: "Report", icon: FileCheck2 },
];

/* ============================================================================
   THREE.JS OCEAN HERO
   ============================================================================ */
function OceanScene() {
  const mountRef = useRef(null);
  const frameRef = useRef(null);

  useEffect(() => {
    const mount = mountRef.current;
    if (!mount) return;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(TOKENS.bg);
    scene.fog = new THREE.FogExp2(TOKENS.bg, 0.028);

    const camera = new THREE.PerspectiveCamera(42, mount.clientWidth / mount.clientHeight, 0.1, 200);
    camera.position.set(0, 15, 34);
    camera.lookAt(0, -1, 0);

    const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(mount.clientWidth, mount.clientHeight);
    mount.appendChild(renderer.domElement);

    /* ---------------- lighting ---------------- */
    const ambient = new THREE.AmbientLight(0x1b4a5f, 1.1);
    scene.add(ambient);
    const key = new THREE.DirectionalLight(0x9fe0f7, 1.1);
    key.position.set(12, 22, 8);
    scene.add(key);
    const rim = new THREE.PointLight(0x35c9f5, 2.2, 60);
    rim.position.set(-14, 8, -10);
    scene.add(rim);
    const oilGlow = new THREE.PointLight(0xd99a3d, 1.4, 20);
    oilGlow.position.set(9, 3, -5);
    scene.add(oilGlow);

    /* ---------------- ocean surface ---------------- */
    const WIDTH = 56, DEPTH = 56, SEGX = 110, SEGZ = 110;
    const oceanGeo = new THREE.PlaneGeometry(WIDTH, DEPTH, SEGX, SEGZ);
    oceanGeo.rotateX(-Math.PI / 2);
    const basePos = oceanGeo.attributes.position.array.slice();

    const oceanMat = new THREE.MeshPhongMaterial({
      color: new THREE.Color(TOKENS.ocean),
      emissive: new THREE.Color(0x0a2c3a),
      specular: new THREE.Color(0x8fe6ff),
      shininess: 70,
      transparent: true,
      opacity: 0.97,
      side: THREE.DoubleSide,
    });
    const oceanMesh = new THREE.Mesh(oceanGeo, oceanMat);
    scene.add(oceanMesh);

    // faint scanning wireframe overlay for the "satellite grid" feel
    const gridGeo = new THREE.PlaneGeometry(WIDTH, DEPTH, 22, 22);
    gridGeo.rotateX(-Math.PI / 2);
    const gridMat = new THREE.MeshBasicMaterial({ color: 0x35c9f5, wireframe: true, transparent: true, opacity: 0.06 });
    const gridMesh = new THREE.Mesh(gridGeo, gridMat);
    gridMesh.position.y = 0.03;
    scene.add(gridMesh);

    function waveHeight(x, z, t) {
      return (
        Math.sin(x * 0.18 + t * 0.9) * 0.55 +
        Math.sin(z * 0.22 - t * 0.7) * 0.45 +
        Math.sin((x + z) * 0.12 + t * 0.4) * 0.35 +
        Math.sin(x * 0.05 - z * 0.06 + t * 0.25) * 0.5
      );
    }

    /* ---------------- oil patch (irregular blob) ---------------- */
    const oilShape = new THREE.Shape();
    const oilPts = 22;
    for (let i = 0; i <= oilPts; i++) {
      const a = (i / oilPts) * Math.PI * 2;
      const r = 3.2 + Math.sin(a * 3.1) * 0.7 + Math.cos(a * 5.3) * 0.4;
      const px = Math.cos(a) * r;
      const py = Math.sin(a) * r * 0.62;
      if (i === 0) oilShape.moveTo(px, py); else oilShape.lineTo(px, py);
    }
    const oilGeo = new THREE.ShapeGeometry(oilShape, 8);
    oilGeo.rotateX(-Math.PI / 2);
    const oilMat = new THREE.MeshPhongMaterial({
      color: new THREE.Color(TOKENS.oil), emissive: new THREE.Color(0x5c3a10),
      transparent: true, opacity: 0.82, shininess: 30, side: THREE.DoubleSide,
    });
    const oilMesh = new THREE.Mesh(oilGeo, oilMat);
    oilMesh.position.set(9.5, 0.12, -4.5);
    scene.add(oilMesh);

    /* ---------------- boat ---------------- */
    const boat = new THREE.Group();
    const hullMat = new THREE.MeshPhongMaterial({ color: 0xe9f6fb, emissive: 0x0d2733, shininess: 60 });
    const trimMat = new THREE.MeshPhongMaterial({ color: 0x35c9f5, emissive: 0x0a2733, shininess: 80 });

    const hullShape = new THREE.Shape();
    hullShape.moveTo(-1.5, -0.3);
    hullShape.lineTo(1.1, -0.3);
    hullShape.lineTo(1.6, 0);
    hullShape.lineTo(1.1, 0.3);
    hullShape.lineTo(-1.5, 0.3);
    hullShape.lineTo(-1.5, -0.3);
    const hullGeo = new THREE.ExtrudeGeometry(hullShape, { depth: 0.5, bevelEnabled: false });
    hullGeo.rotateX(Math.PI / 2);
    hullGeo.translate(0, 0.18, -0.25);
    const hull = new THREE.Mesh(hullGeo, hullMat);
    boat.add(hull);

    const cabin = new THREE.Mesh(new THREE.BoxGeometry(0.9, 0.55, 0.7), trimMat);
    cabin.position.set(-0.3, 0.58, 0);
    boat.add(cabin);
    const mast = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.9, 6), trimMat);
    mast.position.set(-0.3, 1.15, 0);
    boat.add(mast);
    boat.scale.setScalar(1.15);
    scene.add(boat);

    const pathR1 = 15, pathR2 = 10;
    function boatPos(t) {
      const a = t * 0.22;
      return new THREE.Vector3(Math.cos(a) * pathR1 - 4, 0, Math.sin(a) * pathR2 + 2);
    }

    /* ---------------- wake (fading triangle-strip wedge) ---------------- */
    const WAKE_STEPS = 46;
    const wakeGeo = new THREE.BufferGeometry();
    const wakePositions = new Float32Array(WAKE_STEPS * 2 * 3);
    const wakeColors = new Float32Array(WAKE_STEPS * 2 * 3);
    const wakeIndices = [];
    for (let i = 0; i < WAKE_STEPS - 1; i++) {
      const a = i * 2, b = i * 2 + 1, c = i * 2 + 2, d = i * 2 + 3;
      wakeIndices.push(a, b, c, b, d, c);
    }
    wakeGeo.setAttribute("position", new THREE.BufferAttribute(wakePositions, 3));
    wakeGeo.setAttribute("color", new THREE.BufferAttribute(wakeColors, 3));
    wakeGeo.setIndex(wakeIndices);
    const wakeMat = new THREE.MeshBasicMaterial({
      vertexColors: true, transparent: true, opacity: 0.55, side: THREE.DoubleSide, depthWrite: false,
    });
    const wakeMesh = new THREE.Mesh(wakeGeo, wakeMat);
    scene.add(wakeMesh);
    const wakeHistory = [];

    /* ---------------- mist particles ---------------- */
    const MIST_N = 260;
    const mistGeo = new THREE.BufferGeometry();
    const mistPos = new Float32Array(MIST_N * 3);
    const mistSpeed = new Float32Array(MIST_N);
    for (let i = 0; i < MIST_N; i++) {
      mistPos[i * 3] = (Math.random() - 0.5) * 50;
      mistPos[i * 3 + 1] = Math.random() * 8;
      mistPos[i * 3 + 2] = (Math.random() - 0.5) * 50;
      mistSpeed[i] = 0.15 + Math.random() * 0.25;
    }
    mistGeo.setAttribute("position", new THREE.BufferAttribute(mistPos, 3));
    const mistMat = new THREE.PointsMaterial({
      color: 0x9fe0f7, size: 0.11, transparent: true, opacity: 0.35,
      blending: THREE.AdditiveBlending, depthWrite: false,
    });
    const mist = new THREE.Points(mistGeo, mistMat);
    scene.add(mist);

    /* ---------------- satellite orbit ring ---------------- */
    const ring = new THREE.Mesh(
      new THREE.TorusGeometry(24, 0.02, 8, 100),
      new THREE.MeshBasicMaterial({ color: 0x35c9f5, transparent: true, opacity: 0.12 })
    );
    ring.rotation.x = Math.PI / 2.4;
    ring.position.y = 6;
    scene.add(ring);
    const satellite = new THREE.Mesh(
      new THREE.SphereGeometry(0.13, 8, 8),
      new THREE.MeshBasicMaterial({ color: 0xbaf1ff })
    );
    scene.add(satellite);

    /* ---------------- animate ---------------- */
    const clock = new THREE.Clock();

    function animate() {
      const t = clock.getElapsedTime();

      // waves
      const posAttr = oceanGeo.attributes.position;
      for (let i = 0; i < posAttr.count; i++) {
        const ix = basePos[i * 3], iz = basePos[i * 3 + 2];
        posAttr.array[i * 3 + 1] = waveHeight(ix, iz, t);
      }
      posAttr.needsUpdate = true;
      oceanGeo.computeVertexNormals();
      gridMesh.position.y = 0.02;

      // boat
      const bp = boatPos(t);
      const bpAhead = boatPos(t + 0.06);
      bp.y = waveHeight(bp.x, bp.z, t) + 0.12;
      boat.position.copy(bp);
      boat.lookAt(bpAhead.x, bp.y, bpAhead.z);
      boat.rotation.z = Math.sin(t * 1.4) * 0.04;
      boat.rotation.x = Math.sin(t * 1.1) * 0.03;

      // oil patch gently bobs
      oilMesh.position.y = waveHeight(9.5, -4.5, t) * 0.4 + 0.1;

      // wake history
      wakeHistory.unshift({ x: bp.x, z: bp.z, y: bp.y, dir: Math.atan2(bpAhead.x - bp.x, bpAhead.z - bp.z) });
      if (wakeHistory.length > WAKE_STEPS) wakeHistory.pop();
      const oceanColor = new THREE.Color(TOKENS.ocean);
      const foamColor = new THREE.Color(0xdff7ff);
      for (let i = 0; i < WAKE_STEPS; i++) {
        const h = wakeHistory[i] || wakeHistory[wakeHistory.length - 1] || { x: bp.x, z: bp.z, y: bp.y, dir: 0 };
        const age = i / WAKE_STEPS;
        const width = 0.05 + age * 1.5;
        const px = Math.cos(h.dir) * width, pz = -Math.sin(h.dir) * width;
        wakePositions[i * 6] = h.x + px;
        wakePositions[i * 6 + 1] = h.y + 0.03;
        wakePositions[i * 6 + 2] = h.z + pz;
        wakePositions[i * 6 + 3] = h.x - px;
        wakePositions[i * 6 + 4] = h.y + 0.03;
        wakePositions[i * 6 + 5] = h.z - pz;
        const mixed = foamColor.clone().lerp(oceanColor, age);
        wakeColors[i * 6] = mixed.r; wakeColors[i * 6 + 1] = mixed.g; wakeColors[i * 6 + 2] = mixed.b;
        wakeColors[i * 6 + 3] = mixed.r; wakeColors[i * 6 + 4] = mixed.g; wakeColors[i * 6 + 5] = mixed.b;
      }
      wakeGeo.attributes.position.needsUpdate = true;
      wakeGeo.attributes.color.needsUpdate = true;

      // mist drift
      const mp = mistGeo.attributes.position;
      for (let i = 0; i < MIST_N; i++) {
        mp.array[i * 3 + 1] += mistSpeed[i] * 0.01;
        if (mp.array[i * 3 + 1] > 9) mp.array[i * 3 + 1] = 0;
      }
      mp.needsUpdate = true;

      // satellite orbit
      const sa = t * 0.25;
      satellite.position.set(Math.cos(sa) * 24, 6 + Math.sin(sa * 0.6) * 1.5, Math.sin(sa) * 24 * Math.cos(Math.PI / 2.4));
      ring.rotation.z = t * 0.05;

      // camera drift
      camera.position.x = Math.sin(t * 0.08) * 3;
      camera.position.y = 15 + Math.sin(t * 0.12) * 0.6;
      camera.lookAt(0, -0.5, 0);

      renderer.render(scene, camera);
      frameRef.current = requestAnimationFrame(animate);
    }
    animate();

    function handleResize() {
      if (!mount) return;
      camera.aspect = mount.clientWidth / mount.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(mount.clientWidth, mount.clientHeight);
    }
    const ro = new ResizeObserver(handleResize);
    ro.observe(mount);

    return () => {
      cancelAnimationFrame(frameRef.current);
      ro.disconnect();
      mount.removeChild(renderer.domElement);
      [oceanGeo, gridGeo, oilGeo, hullGeo, wakeGeo, mistGeo].forEach((g) => g.dispose());
      [oceanMat, gridMat, oilMat, hullMat, trimMat, wakeMat, mistMat].forEach((m) => m.dispose());
      renderer.dispose();
    };
  }, []);

  return <div ref={mountRef} style={{ position: "absolute", inset: 0 }} />;
}

/* ============================================================================
   SCREEN 1 — LANDING
   ============================================================================ */
function LandingScreen({ onStart, onExplore }) {
  const [entered, setEntered] = useState(false);
  useEffect(() => { const id = setTimeout(() => setEntered(true), 60); return () => clearTimeout(id); }, []);

  return (
    <div style={{ position: "relative", height: "100vh", width: "100%", overflow: "hidden" }}>
      <OceanScene />

      {/* vignette for legibility, kept minimal so the ocean stays the hero */}
      <div style={{
        position: "absolute", inset: 0, pointerEvents: "none",
        background: "radial-gradient(ellipse at 50% 30%, transparent 35%, rgba(3,16,24,0.55) 100%), linear-gradient(180deg, rgba(3,16,24,0.55) 0%, transparent 22%, transparent 70%, rgba(3,16,24,0.75) 100%)"
      }} />

      <div style={{ position: "relative", zIndex: 2, height: "100%", display: "flex", flexDirection: "column" }}>
        <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "28px 44px", opacity: entered ? 1 : 0, transition: "opacity 1s ease" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <Waves size={18} color={TOKENS.cyan} />
            <span className="sgd-label" style={{ color: TOKENS.babyblue, fontSize: 12 }}>SAGARDRHISTI</span>
          </div>
          <span className="sgd-label">SENTINEL-1 · AI · OCEAN DYNAMICS · AIS</span>
        </header>

        <div style={{ flex: 1, display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", padding: "0 24px", textAlign: "center" }}>
          <div className={entered ? "sgd-enter" : ""} style={{ opacity: entered ? undefined : 0 }}>
            <h1 className="sgd-display sgd-glow-text" style={{
              fontSize: "clamp(40px, 8vw, 92px)", margin: 0, lineHeight: 1.02,
              color: TOKENS.white, letterSpacing: "0.01em"
            }}>
              SAGAR<span style={{ color: TOKENS.cyan, fontWeight: 400 }}>DHRISTI</span>
            </h1>
          </div>

          <p className={entered ? "sgd-enter sgd-enter-1" : ""} style={{
            opacity: entered ? undefined : 0, fontSize: "clamp(16px, 2.4vw, 22px)", color: TOKENS.babyblue,
            marginTop: 22, marginBottom: 8, fontWeight: 300, letterSpacing: "0.01em"
          }}>
            See the Spill. Trace the Source.
          </p>

          <p className={entered ? "sgd-enter sgd-enter-2" : ""} style={{
            opacity: entered ? undefined : 0, color: "#8FB8CC", maxWidth: 520, fontSize: 15.5, lineHeight: 1.7, marginTop: 14
          }}>
            AI-powered satellite intelligence for marine oil spill detection and vessel attribution.
          </p>

          <div className={entered ? "sgd-enter sgd-enter-3" : ""} style={{ opacity: entered ? undefined : 0, display: "flex", gap: 16, marginTop: 40, flexWrap: "wrap", justifyContent: "center" }}>
            <button className="sgd-btn-primary" onClick={onStart} style={{ display: "flex", alignItems: "center", gap: 10 }}>
              Start Investigation <ArrowRight size={16} />
            </button>
            <button className="sgd-btn-ghost" onClick={onExplore}>Explore Technology</button>
          </div>
        </div>

        <div className={entered ? "sgd-enter sgd-enter-4" : ""} style={{ opacity: entered ? undefined : 0, display: "flex", flexDirection: "column", alignItems: "center", paddingBottom: 30, gap: 8 }}>
          <span className="sgd-label" style={{ fontSize: 10 }}>Scroll to investigate</span>
          <div style={{ width: 1, height: 26, background: "linear-gradient(180deg, #35C9F5, transparent)", animation: "sgdBob 2s ease-in-out infinite" }} />
        </div>
      </div>
    </div>
  );
}

/* ============================================================================
   PIPELINE RAIL (left navigation for internal screens)
   ============================================================================ */
function PipelineRail({ activeId, onNavigate }) {
  return (
    <aside style={{
      width: 232, flexShrink: 0, borderRight: "1px solid #0F3040",
      padding: "28px 0", display: "flex", flexDirection: "column", height: "100%", overflowY: "auto"
    }} className="sgd-scrollbar">
      <div style={{ padding: "0 24px 26px", display: "flex", alignItems: "center", gap: 10, cursor: "pointer" }} onClick={() => onNavigate("overview")}>
        <Waves size={16} color={TOKENS.cyan} />
        <div>
          <div style={{ fontSize: 13.5, fontWeight: 600, letterSpacing: "0.02em" }}>SagarDhristi</div>
          <div className="sgd-label" style={{ fontSize: 9.5 }}>Marine Intelligence</div>
        </div>
      </div>
      <div className="sgd-hairline" style={{ margin: "0 24px 18px" }} />

      <div style={{ padding: "0 12px", display: "flex", flexDirection: "column", gap: 2 }}>
        {PIPELINE_SCREENS.filter(s => s.step).map((s) => {
          const Icon = s.icon;
          const active = activeId === s.id;
          return (
            <div key={s.id} className="sgd-nav-item" onClick={() => onNavigate(s.id)}
              style={{
                display: "flex", alignItems: "center", gap: 12, padding: "10px 12px", cursor: "pointer",
                color: active ? TOKENS.white : "#628CA3",
                background: active ? "rgba(53,201,245,0.08)" : "transparent",
                borderLeft: active ? `2px solid ${TOKENS.cyan}` : "2px solid transparent",
              }}>
              <span className="sgd-mono" style={{ fontSize: 10.5, color: active ? TOKENS.cyan : "#3F6B80", width: 16 }}>{s.step}</span>
              <Icon size={14} strokeWidth={1.8} />
              <span style={{ fontSize: 13 }}>{s.label}</span>
            </div>
          );
        })}
      </div>

      <div style={{ marginTop: "auto", padding: "20px 24px 0" }}>
        <div className="sgd-hairline" style={{ marginBottom: 16 }} />
        <div className="sgd-label" style={{ marginBottom: 6 }}>{CASE.id}</div>
        <StatusPill tone="cyan">ACTIVE</StatusPill>
      </div>
    </aside>
  );
}

function TopBar({ title, sub }) {
  return (
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", padding: "26px 44px 0" }}>
      <div>
        <div className="sgd-label" style={{ marginBottom: 6 }}>{sub}</div>
        <div style={{ fontSize: 19, fontWeight: 600 }}>{title}</div>
      </div>
      <div style={{ textAlign: "right" }}>
        <div className="sgd-mono" style={{ fontSize: 12, color: "#7FAEC7" }}>{CASE.detected}</div>
      </div>
    </div>
  );
}

/* ============================================================================
   SCREEN 2 — CASE OVERVIEW
   ============================================================================ */
function OverviewScreen({ onNavigate }) {
  const flow = ["Satellite Image", "Preprocessing", "Multi-Agent Analysis", "Orchestrator", "Characterization", "Drift Analysis", "AIS Investigation", "Vessel Ranking", "Evidence"];
  return (
    <div style={{ padding: "40px 44px 60px", maxWidth: 1180 }}>
      <div className="sgd-enter" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 16, marginBottom: 6 }}>
        <div>
          <div className="sgd-mono" style={{ fontSize: 13, color: TOKENS.cyan, marginBottom: 8 }}>{CASE.id}</div>
          <h1 className="sgd-display" style={{ fontSize: 34, margin: 0 }}>Marine Intelligence Platform</h1>
        </div>
        <StatusPill tone="cyan">{CASE.status}</StatusPill>
      </div>
      <p className="sgd-enter sgd-enter-1" style={{ color: "#7FAEC7", marginTop: 14, maxWidth: 640, lineHeight: 1.7 }}>
        A Sentinel-1 SAR pass flagged a probable slick off the Gulf of Kutch. The system has run detection,
        AI segmentation, drift hindcasting and AIS correlation — the findings below summarize the current state
        of the investigation.
      </p>

      <div className="sgd-enter sgd-enter-2" style={{
        display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: 0,
        marginTop: 44, border: "1px solid #0F3040", borderLeft: "none"
      }}>
        {[
          { label: "Detection", value: `${CASE.confidence}%`, note: "Sentinel-1 SAR confidence", icon: Satellite },
          { label: "Spill Area", value: CASE.area, unit: "km²", icon: Waves },
          { label: "Estimated Origin", value: CASE.origin, small: true, icon: MapPin },
          { label: "Estimated Age", value: CASE.age, small: true, icon: Clock },
          { label: "Vessels Analyzed", value: CASE.vessels, icon: Ship },
        ].map((m, i) => {
          const Icon = m.icon;
          return (
            <div key={i} style={{ borderLeft: "1px solid #0F3040", padding: "22px 20px" }}>
              <Icon size={15} color="#5A93AC" style={{ marginBottom: 14 }} />
              <div className="sgd-label" style={{ marginBottom: 8 }}>{m.label}</div>
              <div className="sgd-mono" style={{ fontSize: m.small ? 16 : 26, fontWeight: 600, color: TOKENS.white }}>
                {m.value}{m.unit && <span style={{ fontSize: 14, color: "#6FA8C4", marginLeft: 4 }}>{m.unit}</span>}
              </div>
            </div>
          );
        })}
      </div>

      <div className="sgd-enter sgd-enter-3" style={{ marginTop: 64 }}>
        <div className="sgd-label" style={{ marginBottom: 22 }}>Investigation Pipeline</div>
        <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", gap: 0 }}>
          {flow.map((f, i) => (
            <React.Fragment key={f}>
              <div style={{
                fontSize: 12.5, padding: "9px 14px", border: "1px solid #163B4E", color: "#9AC4DA",
                background: "#061826"
              }}>{f}</div>
              {i < flow.length - 1 && <ChevronRight size={14} color="#2C5A70" style={{ margin: "0 4px" }} />}
            </React.Fragment>
          ))}
        </div>
      </div>

      <div className="sgd-enter sgd-enter-4" style={{ marginTop: 56 }}>
        <button className="sgd-btn-primary" onClick={() => onNavigate("detection")} style={{ display: "flex", alignItems: "center", gap: 10 }}>
          Enter Detection <ArrowRight size={15} />
        </button>
      </div>
    </div>
  );
}

/* ============================================================================
   SCREEN 3 — SATELLITE IMAGE ANALYSIS
   ============================================================================ */
function SatelliteScreen({ onNavigate }) {
  const tabs = ["Original", "VV", "VH", "Preprocessed", "Segmentation", "Final Detection"];
  const [tab, setTab] = useState("Final Detection");
  const showDetection = tab === "Segmentation" || tab === "Final Detection";
  const seedMap = { Original: 4, VV: 6, VH: 9, Preprocessed: 3, Segmentation: 3, "Final Detection": 3 };
  const freqMap = { Original: 0.9, VV: 0.75, VH: 1.1, Preprocessed: 0.5, Segmentation: 0.5, "Final Detection": 0.5 };

  return (
    <div style={{ padding: "34px 44px 60px", display: "grid", gridTemplateColumns: "1fr 320px", gap: 40 }}>
      <div>
        <SectionHead eyebrow="Screen 03 · Detection" title="Sentinel-1 SAR Analysis" sub="C-band backscatter imagery processed through noise removal, speckle filtering and normalization before segmentation." />

        <div style={{ display: "flex", gap: 4, marginBottom: 18, flexWrap: "wrap" }}>
          {tabs.map((t) => (
            <button key={t} onClick={() => setTab(t)} className="sgd-mono" style={{
              padding: "9px 16px", fontSize: 12.5, cursor: "pointer",
              background: tab === t ? "rgba(53,201,245,0.1)" : "transparent",
              color: tab === t ? TOKENS.cyan : "#628CA3",
              border: `1px solid ${tab === t ? "#2C7A9E" : "#163B4E"}`,
            }}>{t}</button>
          ))}
        </div>

        <Bracket>
          <div style={{ position: "relative", width: "100%", aspectRatio: "16/10", background: "#061826", overflow: "hidden" }}>
            <svg width="100%" height="100%" viewBox="0 0 400 250" preserveAspectRatio="xMidYMid slice">
              <defs>
                <SyntheticTexture id={`sartex-${tab}`} baseFrequency={freqMap[tab]} seed={seedMap[tab]} tint="#0B3244" />
              </defs>
              <rect width="400" height="250" fill="#051722" />
              <rect width="400" height="250" filter={`url(#sartex-${tab})`} opacity="0.9" />
              {showDetection && (
                <g>
                  <path d="M 210 120 C 230 105, 260 108, 275 122 C 292 138, 288 158, 268 166 C 248 176, 218 172, 205 155 C 195 142, 196 130, 210 120 Z"
                    fill={TOKENS.oil} opacity="0.55" stroke={TOKENS.warning} strokeWidth="1.2" />
                  <text x="284" y="118" className="sgd-mono" fontSize="9" fill={TOKENS.warning}>OIL SPILL</text>
                </g>
              )}
              <g opacity="0.5">
                {Array.from({ length: 6 }).map((_, i) => (
                  <line key={i} x1={i * 66} y1="0" x2={i * 66} y2="250" stroke="#123244" strokeWidth="0.5" />
                ))}
              </g>
            </svg>
            <div style={{
              position: "absolute", top: 0, left: 0, width: "100%", height: "26%",
              background: "linear-gradient(180deg, rgba(53,201,245,0.14), transparent)",
              animation: "sgdScan 5s linear infinite"
            }} />
            <div style={{ position: "absolute", bottom: 12, left: 14 }} className="sgd-label">{tab.toUpperCase()}</div>
            <div className="sgd-mono" style={{ position: "absolute", bottom: 12, right: 14, fontSize: 11, color: "#7FAEC7" }}>22.4°N 69.1°E</div>
          </div>
        </Bracket>

        <NavButtons onBack={() => onNavigate("overview")} onNext={() => onNavigate("ai-analysis")} nextLabel="Run AI Analysis" />
      </div>

      <div>
        <div style={{ marginBottom: 30 }}>
          <div className="sgd-label" style={{ marginBottom: 10 }}>Source</div>
          <div style={{ fontSize: 16, fontWeight: 600 }}>SENTINEL-1</div>
          <div className="sgd-mono" style={{ fontSize: 12.5, color: "#7FAEC7" }}>SAR · C-band</div>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20, marginBottom: 30 }}>
          <Reading label="Acquisition" value="27 AUG" unit="2026" size={16} />
          <Reading label="AOI" value="22.4°N" unit="69.1°E" size={16} />
        </div>

        <div style={{ marginBottom: 30 }}>
          <div className="sgd-label" style={{ marginBottom: 12 }}>Preprocessing</div>
          {["Noise removal", "Speckle filtering", "Normalization"].map((s) => (
            <div key={s} style={{ display: "flex", alignItems: "center", gap: 9, marginBottom: 9, fontSize: 13.5, color: "#C5E2EF" }}>
              <CheckCircle2 size={14} color={TOKENS.cyan} /> {s}
            </div>
          ))}
        </div>

        <div className="sgd-hairline" style={{ margin: "26px 0" }} />

        <div className="sgd-label" style={{ marginBottom: 10 }}>Detection</div>
        <div style={{ fontSize: 17, fontWeight: 700, color: TOKENS.warning, marginBottom: 14 }}>OIL SPILL DETECTED</div>
        <Reading label="Confidence" value={CASE.confidence} unit="%" size={30} color={TOKENS.cyan} />
        <ScoreBar value={CASE.confidence} color={TOKENS.cyan} />
      </div>
    </div>
  );
}

/* ============================================================================
   SCREEN 4 — MULTI-AGENT AI ANALYSIS
   ============================================================================ */
function AIAnalysisScreen({ onNavigate }) {
  const [active, setActive] = useState(null);
  return (
    <div style={{ padding: "34px 44px 60px", maxWidth: 1080 }}>
      <SectionHead eyebrow="Screen 04 · AI Analysis" title="Multi-Agent Detection Architecture" sub="Three independent models analyze the same scene. An orchestrator reconciles their outputs into a single, confidence-weighted detection." />

      <div style={{ position: "relative", marginTop: 10 }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 28 }}>
          {AGENTS.map((a, i) => (
            <Bracket key={a.key} className="sgd-enter" style={{ animationDelay: `${i * 0.08}s` }}>
              <div onMouseEnter={() => setActive(a.key)} onMouseLeave={() => setActive(null)}
                style={{ padding: "26px 22px", cursor: "default", background: active === a.key ? "rgba(53,201,245,0.04)" : "transparent", transition: "background .2s" }}>
                <div className="sgd-label" style={{ marginBottom: 12 }}>Agent {i + 1}</div>
                <div style={{ fontSize: 19, fontWeight: 700, marginBottom: 6, letterSpacing: "0.01em" }}>{a.name}</div>
                <div style={{ fontSize: 13, color: "#7FAEC7", marginBottom: 20 }}>{a.type}</div>
                <div className="sgd-mono" style={{ fontSize: 28, fontWeight: 600, color: TOKENS.babyblue, marginBottom: 6 }}>{a.confidence}%</div>
                <ScoreBar value={a.confidence} color={TOKENS.babyblue} />
                <p style={{ fontSize: 12.5, color: "#628CA3", marginTop: 16, lineHeight: 1.6, minHeight: 52 }}>{a.desc}</p>
              </div>
            </Bracket>
          ))}
        </div>

        {/* connecting lines down to orchestrator */}
        <svg width="100%" height="70" style={{ display: "block", marginTop: -1 }} viewBox="0 0 900 70" preserveAspectRatio="none">
          <line x1="150" y1="0" x2="450" y2="55" stroke="#204A5F" strokeWidth="1.4" />
          <line x1="450" y1="0" x2="450" y2="55" stroke="#204A5F" strokeWidth="1.4" />
          <line x1="750" y1="0" x2="450" y2="55" stroke="#204A5F" strokeWidth="1.4" />
        </svg>

        <Bracket style={{ maxWidth: 460, margin: "0 auto" }}>
          <div style={{ padding: "26px 30px", textAlign: "center", background: "rgba(141,220,247,0.04)" }}>
            <div className="sgd-label" style={{ color: TOKENS.cyan, marginBottom: 10 }}>Orchestrator</div>
            <div style={{ fontSize: 14, color: "#9AC4DA", marginBottom: 18 }}>Weighted consensus across all three agents</div>
            <div className="sgd-hairline" style={{ marginBottom: 18 }} />
            <div style={{ fontSize: 20, fontWeight: 700, color: TOKENS.warning, marginBottom: 8 }}>OIL SPILL DETECTED</div>
            <div className="sgd-mono" style={{ fontSize: 34, fontWeight: 700, color: TOKENS.cyan }}>{CASE.confidence}%<span style={{ fontSize: 14, color: "#6FA8C4", marginLeft: 6 }}>CONFIDENCE</span></div>
          </div>
        </Bracket>
      </div>

      <NavButtons onBack={() => onNavigate("detection")} onNext={() => onNavigate("characterization")} nextLabel="Characterize Spill" />
    </div>
  );
}

/* ============================================================================
   SCREEN 5 — SPILL CHARACTERIZATION
   ============================================================================ */
function CharacterizationScreen({ onNavigate }) {
  const c = CHARACTERIZATION;
  return (
    <div style={{ padding: "34px 44px 60px", display: "grid", gridTemplateColumns: "1fr 340px", gap: 40 }}>
      <div>
        <SectionHead eyebrow="Screen 05 · Characterization" title="Spill Geometry & Morphology" sub="Physical dimensions and shape descriptors extracted from the segmented slick boundary." />

        <Bracket>
          <div style={{ position: "relative", width: "100%", aspectRatio: "16/10", background: "#061826" }}>
            <svg width="100%" height="100%" viewBox="0 0 400 250">
              <defs><SyntheticTexture id="chartex" baseFrequency={0.5} seed={3} tint="#0B3244" /></defs>
              <rect width="400" height="250" fill="#051722" />
              <rect width="400" height="250" filter="url(#chartex)" opacity="0.85" />
              <path d="M 150 120 C 175 100, 220 100, 250 118 C 278 134, 275 158, 245 170 C 210 184, 165 178, 148 158 C 136 144, 138 130, 150 120 Z"
                fill={TOKENS.oil} opacity="0.5" stroke={TOKENS.warning} strokeWidth="1.4" />
              <line x1="148" y1="140" x2="278" y2="140" stroke={TOKENS.babyblue} strokeWidth="1" strokeDasharray="4 3" />
              <text x="190" y="132" className="sgd-mono" fontSize="9" fill={TOKENS.babyblue}>3.8 KM</text>
              <line x1="212" y1="105" x2="212" y2="182" stroke={TOKENS.babyblue} strokeWidth="1" strokeDasharray="4 3" />
              <text x="218" y="150" className="sgd-mono" fontSize="9" fill={TOKENS.babyblue}>1.2 KM</text>
            </svg>
          </div>
        </Bracket>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 0, marginTop: 30, border: "1px solid #0F3040", borderLeft: "none" }}>
          {[
            { label: "Area", value: c.area, unit: "km²" },
            { label: "Perimeter", value: c.perimeter, unit: "km" },
            { label: "Length", value: c.length, unit: "km" },
            { label: "Width", value: c.width, unit: "km" },
            { label: "Aspect Ratio", value: c.aspectRatio, unit: "" },
            { label: "Confidence", value: `${c.confidence}%`, unit: "" },
          ].map((m) => (
            <div key={m.label} style={{ borderLeft: "1px solid #0F3040", padding: "18px 18px" }}>
              <div className="sgd-label" style={{ marginBottom: 8 }}>{m.label}</div>
              <div className="sgd-mono" style={{ fontSize: 19, fontWeight: 600 }}>{m.value}<span style={{ fontSize: 12, color: "#6FA8C4", marginLeft: 3 }}>{m.unit}</span></div>
            </div>
          ))}
        </div>

        <NavButtons onBack={() => onNavigate("ai-analysis")} onNext={() => onNavigate("drift")} nextLabel="Run Drift Analysis" />
      </div>

      <div>
        <div className="sgd-label" style={{ marginBottom: 6 }}>Estimated Age</div>
        <div className="sgd-mono" style={{ fontSize: 26, fontWeight: 600, marginBottom: 30 }}>{c.age}</div>

        <div className="sgd-label" style={{ marginBottom: 18 }}>Shape Analysis</div>
        {c.shape.map((s) => (
          <div key={s.label} style={{ marginBottom: 22 }}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
              <span style={{ fontSize: 13.5 }}>{s.label}</span>
              <span className="sgd-mono" style={{ fontSize: 13, color: TOKENS.babyblue }}>{s.value.toFixed(2)}</span>
            </div>
            <ScoreBar value={s.value} max={1} color={TOKENS.babyblue} />
            <p style={{ fontSize: 12, color: "#628CA3", marginTop: 8, lineHeight: 1.6 }}>{s.note}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ============================================================================
   SCREEN 6 — DRIFT / HINDCAST ANALYSIS
   ============================================================================ */
function DriftScreen({ onNavigate }) {
  const [phase, setPhase] = useState(2); // 0 past 1 origin 2 detection 3 forecast
  const phases = ["Past", "Origin", "Detection", "Forecast"];
  return (
    <div style={{ padding: "34px 44px 60px", display: "grid", gridTemplateColumns: "1fr 320px", gap: 40 }}>
      <div>
        <SectionHead eyebrow="Screen 06 · Drift" title="Drift & Hindcast Reconstruction" sub="Backward particle tracking estimates the discharge origin; forward tracking projects the slick's likely path." />

        <Bracket>
          <div style={{ position: "relative", width: "100%", aspectRatio: "16/10", background: "#061826" }}>
            <svg width="100%" height="100%" viewBox="0 0 400 250">
              <defs><SyntheticTexture id="drifttex" baseFrequency={0.4} seed={7} tint="#0A2A3A" /></defs>
              <rect width="400" height="250" fill="#051722" />
              <rect width="400" height="250" filter="url(#drifttex)" opacity="0.7" />

              {/* backtrack (amber) */}
              <path d="M 235 130 C 205 118, 175 108, 150 95" fill="none" stroke={TOKENS.oil} strokeWidth="1.6" strokeDasharray="5 4" markerEnd="url(#arrowAmber)" opacity={phase >= 1 ? 1 : 0.25} />
              {/* forecast (baby blue) */}
              <path d="M 235 130 C 260 148, 290 165, 320 190" fill="none" stroke={TOKENS.babyblue} strokeWidth="1.6" strokeDasharray="5 4" markerEnd="url(#arrowBlue)" opacity={phase >= 3 ? 1 : 0.25} />

              <defs>
                <marker id="arrowAmber" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill={TOKENS.oil} /></marker>
                <marker id="arrowBlue" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill={TOKENS.babyblue} /></marker>
              </defs>

              <circle cx="150" cy="95" r="5" fill={TOKENS.oil} opacity={phase >= 1 ? 1 : 0.3} />
              <text x="158" y="92" className="sgd-mono" fontSize="9" fill={TOKENS.oil} opacity={phase >= 1 ? 1 : 0.3}>ORIGIN</text>

              <ellipse cx="235" cy="130" rx="20" ry="13" fill={TOKENS.warning} opacity="0.5" stroke={TOKENS.warning} strokeWidth="1" />
              <text x="212" y="152" className="sgd-mono" fontSize="9" fill={TOKENS.warning}>DETECTED SLICK</text>

              <circle cx="320" cy="190" r="4" fill={TOKENS.babyblue} opacity={phase >= 3 ? 1 : 0.3} />
              <text x="300" y="207" className="sgd-mono" fontSize="9" fill={TOKENS.babyblue} opacity={phase >= 3 ? 1 : 0.3}>FORECAST</text>
            </svg>
          </div>
        </Bracket>

        <div style={{ marginTop: 26 }}>
          <div className="sgd-label" style={{ marginBottom: 14 }}>Timeline</div>
          <div style={{ position: "relative", height: 4, background: "#0C2A3A" }}>
            <div style={{ position: "absolute", height: "100%", width: `${(phase / 3) * 100}%`, background: `linear-gradient(90deg, ${TOKENS.oil}, ${TOKENS.babyblue})`, transition: "width .4s" }} />
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", marginTop: 12 }}>
            {phases.map((p, i) => (
              <button key={p} onClick={() => setPhase(i)} className="sgd-mono" style={{
                background: "none", border: "none", cursor: "pointer", fontSize: 11.5,
                color: phase === i ? TOKENS.white : "#4E7C93", letterSpacing: "0.08em"
              }}>{p.toUpperCase()}</button>
            ))}
          </div>
        </div>

        <NavButtons onBack={() => onNavigate("characterization")} onNext={() => onNavigate("ais")} nextLabel="Investigate AIS Traffic" />
      </div>

      <div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20, marginBottom: 30 }}>
          <div>
            <div className="sgd-label" style={{ marginBottom: 8, display: "flex", alignItems: "center", gap: 6 }}><Wind size={12} /> Wind</div>
            <div className="sgd-mono" style={{ fontSize: 19, fontWeight: 600 }}>{DRIFT.wind.speed} kn</div>
            <div className="sgd-mono" style={{ fontSize: 12, color: "#7FAEC7" }}>→ {DRIFT.wind.dir}</div>
          </div>
          <div>
            <div className="sgd-label" style={{ marginBottom: 8, display: "flex", alignItems: "center", gap: 6 }}><Navigation2 size={12} /> Current</div>
            <div className="sgd-mono" style={{ fontSize: 19, fontWeight: 600 }}>{DRIFT.current.speed} kn</div>
            <div className="sgd-mono" style={{ fontSize: 12, color: "#7FAEC7" }}>→ {DRIFT.current.dir}</div>
          </div>
        </div>

        <div className="sgd-hairline" style={{ margin: "24px 0" }} />

        <Reading label="Origin Time" value={DRIFT.originTime} size={15} />
        <div style={{ height: 22 }} />
        <div className="sgd-label" style={{ marginBottom: 8 }}>Hindcast Confidence</div>
        <StatusPill tone="cyan">{DRIFT.confidence}</StatusPill>
        <div style={{ height: 22 }} />
        <Reading label="Uncertainty" value={DRIFT.uncertainty} size={17} />
      </div>
    </div>
  );
}

/* ============================================================================
   SCREEN 7 — AIS INVESTIGATION
   ============================================================================ */
function AISScreen({ onNavigate }) {
  const [selected, setSelected] = useState(VESSELS[0]);
  const tierColor = (t) => t === "strongest" ? TOKENS.critical : t === "potential" ? TOKENS.warning : TOKENS.cyan;

  return (
    <div style={{ padding: "34px 44px 60px", display: "grid", gridTemplateColumns: "1fr 340px", gap: 40 }}>
      <div>
        <SectionHead eyebrow="Screen 07 · AIS" title="AIS Traffic Reconstruction" sub="Vessel positions and historical tracks reconstructed around the estimated origin window." />

        <div style={{ display: "flex", gap: 28, marginBottom: 20 }}>
          <Reading label="Origin Window" value="±3" unit="hrs" size={16} />
          <Reading label="Radius" value="12" unit="NM" size={16} />
          <Reading label="Vessels" value={CASE.vessels} size={16} />
        </div>

        <Bracket>
          <div style={{ position: "relative", width: "100%", aspectRatio: "16/10", background: "#061826" }}>
            <svg width="100%" height="100%" viewBox="0 0 100 62.5">
              <defs><SyntheticTexture id="aistex" baseFrequency={0.35} seed={11} tint="#0A2A3A" /></defs>
              <rect width="100" height="62.5" fill="#051722" />
              <rect width="100" height="62.5" filter="url(#aistex)" opacity="0.55" />
              {Array.from({ length: 5 }).map((_, i) => (
                <line key={i} x1="0" y1={i * 12.5} x2="100" y2={i * 12.5} stroke="#0F3040" strokeWidth="0.2" />
              ))}
              <ellipse cx="61" cy="46" rx="9" ry="9" fill="none" stroke={TOKENS.warning} strokeWidth="0.3" strokeDasharray="1 1" />
              <circle cx="61" cy="46" r="1.3" fill={TOKENS.oil} />
              <text x="63.5" y="45" className="sgd-mono" fontSize="2.4" fill={TOKENS.oil}>ORIGIN</text>

              {VESSELS.map((v) => (
                <g key={v.mmsi} onClick={() => setSelected(v)} style={{ cursor: "pointer" }}>
                  <line x1={v.pos.x} y1={v.pos.y} x2={v.pos.x - 6} y2={v.pos.y - 4} stroke={tierColor(v.tier)} strokeWidth="0.25" opacity="0.5" />
                  <circle cx={v.pos.x} cy={v.pos.y} r={selected.mmsi === v.mmsi ? 2 : 1.4}
                    fill={tierColor(v.tier)} stroke={selected.mmsi === v.mmsi ? "#fff" : "none"} strokeWidth="0.3" />
                </g>
              ))}
            </svg>
            <div style={{ position: "absolute", top: 12, right: 14, display: "flex", gap: 14 }}>
              {[["Normal", TOKENS.cyan], ["Potential", TOKENS.warning], ["Strongest", TOKENS.critical]].map(([l, c]) => (
                <div key={l} style={{ display: "flex", alignItems: "center", gap: 5 }}>
                  <span style={{ width: 6, height: 6, borderRadius: "50%", background: c }} />
                  <span className="sgd-label" style={{ fontSize: 9 }}>{l}</span>
                </div>
              ))}
            </div>
          </div>
        </Bracket>

        <NavButtons onBack={() => onNavigate("drift")} onNext={() => onNavigate("ranking")} nextLabel="Rank Vessels" />
      </div>

      <div>
        <div className="sgd-label" style={{ marginBottom: 16 }}>Selected Vessel</div>
        <div style={{ fontSize: 20, fontWeight: 700, marginBottom: 4 }}>{selected.name}</div>
        <div className="sgd-mono" style={{ fontSize: 12.5, color: "#7FAEC7", marginBottom: 24 }}>{selected.type}</div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 18, marginBottom: 24 }}>
          <Reading label="MMSI" value={selected.mmsi} size={13} />
          <Reading label="IMO" value={selected.imo} size={13} />
        </div>

        <div className="sgd-hairline" style={{ margin: "20px 0" }} />

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 18 }}>
          <Reading label="Distance" value={selected.distance} unit="NM" size={18} />
          <Reading label="Time Offset" value={`${selected.timeOffset > 0 ? "+" : ""}${selected.timeOffset}`} unit="min" size={18} color={selected.timeOffset < 0 ? TOKENS.warning : TOKENS.babyblue} />
          <Reading label="Speed" value={selected.speed} unit="kn" size={18} />
          <Reading label="Heading" value={selected.heading} unit="°" size={18} />
        </div>

        <div style={{ marginTop: 26 }}>
          <StatusPill tone={selected.tier === "strongest" ? "critical" : selected.tier === "potential" ? "warning" : "cyan"}>
            {selected.tier === "strongest" ? "Strongest Candidate" : selected.tier === "potential" ? "Potential Vessel" : "Normal Traffic"}
          </StatusPill>
        </div>

        <div style={{ marginTop: 28 }}>
          <div className="sgd-label" style={{ marginBottom: 10 }}>Other Vessels</div>
          <div className="sgd-scrollbar" style={{ maxHeight: 220, overflowY: "auto" }}>
            {VESSELS.map((v) => (
              <div key={v.mmsi} onClick={() => setSelected(v)} className="sgd-row" style={{
                display: "flex", justifyContent: "space-between", padding: "9px 4px", cursor: "pointer",
                borderBottom: "1px solid #0F2938", background: selected.mmsi === v.mmsi ? "rgba(53,201,245,0.06)" : "transparent"
              }}>
                <span style={{ fontSize: 12.5 }}>{v.name}</span>
                <span style={{ width: 6, height: 6, borderRadius: "50%", background: tierColor(v.tier), marginTop: 3 }} />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

/* ============================================================================
   SCREEN 8 — VESSEL FILTERING & RANKING
   ============================================================================ */
function RankingScreen({ onNavigate }) {
  const filters = ["14 Vessels", "Spatial Filter", "Temporal Filter", "Trajectory Filter", "Behavioural Filter", "Potential Sources"];
  const sorted = [...VESSELS].sort((a, b) => b.score - a.score);
  return (
    <div style={{ padding: "34px 44px 60px", maxWidth: 1180 }}>
      <SectionHead eyebrow="Screen 08 · Ranking" title="Vessel Filtering & Ranking" sub="Candidates are narrowed through four sequential filters. Scores express correlation with the reconstructed origin — not confirmed responsibility." />

      <div style={{ display: "flex", alignItems: "center", flexWrap: "wrap", marginBottom: 48 }}>
        {filters.map((f, i) => (
          <React.Fragment key={f}>
            <div style={{ fontSize: 12.5, padding: "10px 16px", border: "1px solid #163B4E", color: i === filters.length - 1 ? TOKENS.cyan : "#9AC4DA", borderColor: i === filters.length - 1 ? "#2C7A9E" : "#163B4E" }}>{f}</div>
            {i < filters.length - 1 && <ChevronRight size={15} color="#2C5A70" style={{ margin: "0 6px" }} />}
          </React.Fragment>
        ))}
      </div>

      <div style={{ overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", minWidth: 760 }}>
          <thead>
            <tr>
              {["Rank", "Vessel", "Distance", "Time Offset", "Trajectory", "Behaviour", "AIS Gap", "Score"].map((h) => (
                <th key={h} className="sgd-label" style={{ textAlign: "left", padding: "0 14px 14px", borderBottom: "1px solid #163B4E" }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sorted.map((v) => (
              <tr key={v.mmsi} className="sgd-row" style={{
                background: v.tier === "strongest" ? "rgba(255,91,91,0.05)" : "transparent",
                borderBottom: "1px solid #0F2938"
              }}>
                <td className="sgd-mono" style={{ padding: "16px 14px", fontSize: 13, color: v.rank === 1 ? TOKENS.critical : "#7FAEC7" }}>#{v.rank}</td>
                <td style={{ padding: "16px 14px" }}>
                  <div style={{ fontWeight: 600, fontSize: 13.5 }}>{v.name}</div>
                  <div className="sgd-mono" style={{ fontSize: 11, color: "#628CA3" }}>{v.type}</div>
                </td>
                <td className="sgd-mono" style={{ padding: "16px 14px", fontSize: 13 }}>{v.distance} NM</td>
                <td className="sgd-mono" style={{ padding: "16px 14px", fontSize: 13 }}>{v.timeOffset > 0 ? "+" : ""}{v.timeOffset} min</td>
                <td style={{ padding: "16px 14px", width: 110 }}>
                  <ScoreBar value={v.trajectory} color={TOKENS.babyblue} height={4} />
                </td>
                <td style={{ padding: "16px 14px", width: 110 }}>
                  <ScoreBar value={v.behaviour} color={TOKENS.oil} height={4} />
                </td>
                <td className="sgd-mono" style={{ padding: "16px 14px", fontSize: 13 }}>{v.aisGap}</td>
                <td style={{ padding: "16px 14px" }}>
                  <span className="sgd-mono" style={{
                    fontSize: 16, fontWeight: 700,
                    color: v.tier === "strongest" ? TOKENS.critical : v.tier === "potential" ? TOKENS.warning : TOKENS.babyblue
                  }}>{v.score}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div style={{ marginTop: 20 }}>
        <span className="sgd-label" style={{ color: "#4E7C93" }}>Scores are an <span style={{ color: TOKENS.cyan }}>attribution correlation</span>, not proof of fault.</span>
      </div>

      <NavButtons onBack={() => onNavigate("ais")} onNext={() => onNavigate("evidence")} nextLabel="Review Evidence" />
    </div>
  );
}

/* ============================================================================
   SCREEN 9 — EVIDENCE & ATTRIBUTION
   ============================================================================ */
function EvidenceScreen({ onNavigate }) {
  const timeline = ["Satellite Detection", "AI Segmentation", "TRANSUNET", "Drift Hindcast", "AIS Correlation", "Vessel Ranking"];
  return (
    <div style={{ padding: "34px 44px 60px", display: "grid", gridTemplateColumns: "1fr 320px", gap: 40 }}>
      <div>
        <SectionHead eyebrow="Screen 09 · Evidence" title="Evidence & Attribution" sub="Each investigative stage contributes a weighted signal. Together they form a correlation score against the top-ranked vessel." />

        {EVIDENCE.map((e) => (
          <div key={e.label} style={{ marginBottom: 22 }}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
              <span style={{ fontSize: 14 }}>{e.label}</span>
              <span className="sgd-mono" style={{ fontSize: 14, color: TOKENS.cyan }}>{e.score}</span>
            </div>
            <ScoreBar value={e.score} color={TOKENS.cyan} />
            <p style={{ fontSize: 12.5, color: "#628CA3", marginTop: 8, lineHeight: 1.6 }}>{e.note}</p>
          </div>
        ))}

        <div className="sgd-hairline" style={{ margin: "30px 0 24px" }} />

        <div className="sgd-label" style={{ marginBottom: 18 }}>Evidence Timeline</div>
        <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center" }}>
          {timeline.map((t, i) => (
            <React.Fragment key={t}>
              <div style={{ fontSize: 12, padding: "9px 14px", border: "1px solid #163B4E", color: "#9AC4DA" }}>{t}</div>
              {i < timeline.length - 1 && <ChevronRight size={14} color="#2C5A70" style={{ margin: "0 4px" }} />}
            </React.Fragment>
          ))}
        </div>

        <NavButtons onBack={() => onNavigate("ranking")} onNext={() => onNavigate("report")} nextLabel="Generate Report" />
      </div>

      <div>
        <Bracket>
          <div style={{ padding: "28px 24px", textAlign: "center" }}>
            <div className="sgd-label" style={{ marginBottom: 12 }}>Attribution Score</div>
            <div className="sgd-mono" style={{ fontSize: 52, fontWeight: 700, color: TOKENS.critical, lineHeight: 1 }}>87</div>
            <div className="sgd-mono" style={{ fontSize: 13, color: "#628CA3" }}>/ 100</div>
          </div>
        </Bracket>

        <div style={{ marginTop: 26, fontSize: 13.5, color: "#9AC4DA", lineHeight: 1.7, fontStyle: "italic" }}>
          "Strong spatio-temporal correlation with the reconstructed spill origin."
        </div>

        <div style={{ marginTop: 26, display: "flex", flexDirection: "column", gap: 10 }}>
          <StatusPill tone="warning">Potential Source</StatusPill>
          <StatusPill tone="neutral">Not Confirmed Attribution</StatusPill>
        </div>

        <div style={{ marginTop: 26, padding: "14px 16px", border: "1px solid #163B4E", display: "flex", gap: 10 }}>
          <Info size={14} color="#5A93AC" style={{ flexShrink: 0, marginTop: 1 }} />
          <span style={{ fontSize: 11.5, color: "#628CA3", lineHeight: 1.6 }}>
            MV Kestrel is identified as the highest-correlation vessel. This is a probabilistic finding for
            investigative prioritization, not legal proof of responsibility.
          </span>
        </div>
      </div>
    </div>
  );
}

/* ============================================================================
   SCREEN 10 — FINAL REPORT
   ============================================================================ */
function ReportScreen({ onNavigate, onRestart }) {
  const rows = [
    ["Case ID", CASE.id],
    ["Satellite Detection", `${CASE.confidence}% confidence · Sentinel-1 SAR`],
    ["AI Analysis", "U-Net · DeepLabV3+ · TransUNet (orchestrated)"],
    ["Spill Characterization", `${CHARACTERIZATION.area} km² · aspect ratio ${CHARACTERIZATION.aspectRatio}`],
    ["Drift Analysis", `Origin ${DRIFT.originTime} · ${DRIFT.confidence} confidence`],
    ["AIS Reconstruction", `${CASE.vessels} vessels within 12 NM / ±3 hr window`],
    ["Vessel Ranking", "MV Kestrel ranked #1 of 14"],
    ["Evidence Score", "87 / 100 attribution correlation"],
  ];
  return (
    <div style={{ padding: "34px 44px 70px", maxWidth: 1080 }}>
      <SectionHead eyebrow="Screen 10 · Report" title="Final Investigation Report" sub="A complete, exportable record of the automated investigation — from detection through vessel attribution." />

      <Bracket>
        <div style={{ padding: "8px 0" }}>
          {rows.map(([k, v], i) => (
            <div key={k} style={{ display: "flex", justifyContent: "space-between", padding: "16px 24px", borderBottom: i < rows.length - 1 ? "1px solid #0F2938" : "none" }}>
              <span className="sgd-label" style={{ fontSize: 11.5 }}>{k}</span>
              <span className="sgd-mono" style={{ fontSize: 13, color: "#D5EBF5", textAlign: "right" }}>{v}</span>
            </div>
          ))}
        </div>
      </Bracket>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px,1fr))", gap: 0, marginTop: 40, border: "1px solid #0F3040", borderLeft: "none" }}>
        {[
          { label: "Oil Spill", value: `${CASE.area} km²` },
          { label: "Detection Confidence", value: `${CASE.confidence}%` },
          { label: "Estimated Origin", value: CASE.origin, small: true },
          { label: "Vessels Analyzed", value: CASE.vessels },
          { label: "Top Potential Source", value: "MV Kestrel", small: true },
          { label: "Attribution Score", value: "87/100" },
        ].map((m) => (
          <div key={m.label} style={{ borderLeft: "1px solid #0F3040", padding: "20px 18px" }}>
            <div className="sgd-label" style={{ marginBottom: 8 }}>{m.label}</div>
            <div className="sgd-mono" style={{ fontSize: m.small ? 15 : 22, fontWeight: 600 }}>{m.value}</div>
          </div>
        ))}
      </div>

      <div style={{ marginTop: 16, fontSize: 11.5, color: "#4E7C93", display: "flex", alignItems: "center", gap: 8 }}>
        <AlertTriangle size={13} color={TOKENS.warning} />
        All figures are simulated demonstration data for this frontend build.
      </div>

      <div style={{ display: "flex", gap: 14, marginTop: 40, flexWrap: "wrap" }}>
        <button className="sgd-btn-primary" style={{ display: "flex", alignItems: "center", gap: 9 }}>
          <FileText size={15} /> Generate Report
        </button>
        <button className="sgd-btn-ghost" style={{ display: "flex", alignItems: "center", gap: 9 }}>
          <Download size={15} /> Export Evidence
        </button>
        <button className="sgd-btn-ghost" onClick={onRestart} style={{ display: "flex", alignItems: "center", gap: 9 }}>
          <RotateCcw size={15} /> Start New Investigation
        </button>
      </div>
    </div>
  );
}

/* ============================================================================
   APP SHELL
   ============================================================================ */
export default function App() {
  const [screen, setScreen] = useState("landing"); // landing | overview | detection | ai-analysis | ...

  const navigate = useCallback((id) => {
    setScreen(id);
    window.scrollTo({ top: 0, behavior: "instant" in window ? "instant" : "auto" });
  }, []);

  const screenMeta = PIPELINE_SCREENS.find((s) => s.id === screen);

  if (screen === "landing") {
    return (
      <div className="sgd-root">
        <GlobalStyles />
        <LandingScreen onStart={() => navigate("overview")} onExplore={() => navigate("overview")} />
      </div>
    );
  }

  return (
    <div className="sgd-root">
      <GlobalStyles />
      <div style={{ display: "flex", minHeight: "100vh" }}>
        <PipelineRail activeId={screen} onNavigate={navigate} />
        <main style={{ flex: 1, minWidth: 0 }} key={screen}>
          <TopBar
            title={screenMeta ? screenMeta.label : "Case Overview"}
            sub={screenMeta && screenMeta.step ? `Step ${screenMeta.step}` : "Overview"}
          />
          <div className="sgd-enter">
            {screen === "overview" && <OverviewScreen onNavigate={navigate} />}
            {screen === "detection" && <SatelliteScreen onNavigate={navigate} />}
            {screen === "ai-analysis" && <AIAnalysisScreen onNavigate={navigate} />}
            {screen === "characterization" && <CharacterizationScreen onNavigate={navigate} />}
            {screen === "drift" && <DriftScreen onNavigate={navigate} />}
            {screen === "ais" && <AISScreen onNavigate={navigate} />}
            {screen === "ranking" && <RankingScreen onNavigate={navigate} />}
            {screen === "evidence" && <EvidenceScreen onNavigate={navigate} />}
            {screen === "report" && <ReportScreen onNavigate={navigate} onRestart={() => navigate("landing")} />}
          </div>
        </main>
      </div>
    </div>
  );
}
