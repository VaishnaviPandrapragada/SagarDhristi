import React, { useState } from "react";
import { Wind, Waves as WaveIcon, Thermometer, Navigation2 } from "lucide-react";
import { Bracket, Reading, Pill, Bar, StageHead, StageNav, Caveat, SimTag, SarTexture, SLICK_PATH } from "../components/ui.jsx";
import { COLORS, SPILL, ENVIRONMENT, DRIFT } from "../data/mock.js";

/* ==========================================================================
   STAGE 05 — CHARACTERIZE SPILL
   ========================================================================== */
export function CharacterizeStage({ go }) {
  const [showDims, setShowDims] = useState(true);

  return (
    <div className="split">
      <div>
        <StageHead
          step="05"
          question="Understanding the spill"
          title="Measuring what the mask actually describes"
          lede="Geometry is extracted from the agreed mask: how large, how elongated, how ragged. These descriptors feed both the age estimate and the source-type inference two stages later."
        />

        <Bracket>
          <div style={{ position: "relative", aspectRatio: "16 / 10", background: "#051722" }}>
            <svg width="100%" height="100%" viewBox="0 0 400 250" preserveAspectRatio="xMidYMid slice">
              <defs><SarTexture id="char" frequency={0.4} seed={3} tint="#0E3346" /></defs>
              <rect width="400" height="250" fill="#07202D" />
              <rect width="400" height="250" filter="url(#char)" opacity="0.8" />
              <path d={SLICK_PATH} fill={COLORS.oil} opacity="0.42" stroke={COLORS.critical} strokeWidth="1.6" />
              {showDims && (
                <g>
                  <line x1="106" y1="152" x2="292" y2="152" stroke={COLORS.baby} strokeWidth="0.9" strokeDasharray="4 3" />
                  <text x="180" y="146" className="mono" fontSize="9" fill={COLORS.baby}>{SPILL.length} km</text>
                  <line x1="212" y1="104" x2="212" y2="192" stroke={COLORS.baby} strokeWidth="0.9" strokeDasharray="4 3" />
                  <text x="218" y="172" className="mono" fontSize="9" fill={COLORS.baby}>{SPILL.width} km</text>
                  <circle cx="199" cy="148" r="2.4" fill={COLORS.cyan} />
                  <text x="206" y="134" className="mono" fontSize="8.5" fill={COLORS.cyan}>{SPILL.location}</text>
                </g>
              )}
            </svg>
            <button
              className="label"
              onClick={() => setShowDims((v) => !v)}
              style={{ position: "absolute", top: 12, right: 14, background: "rgba(3,16,24,0.7)", border: "1px solid #1B4A60", padding: "6px 11px", cursor: "pointer", color: showDims ? COLORS.cyan : "#5C879C" }}
            >
              Dimensions
            </button>
          </div>
        </Bracket>

        <div className="metrics" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(128px, 1fr))", marginTop: 28 }}>
          {[
            ["Area", SPILL.area, "km²"],
            ["Perimeter", SPILL.perimeter, "km"],
            ["Length", SPILL.length, "km"],
            ["Width", SPILL.width, "km"],
            ["Aspect ratio", SPILL.aspect, ""],
            ["Confidence", SPILL.confidence.toFixed(2), ""],
          ].map(([l, v, u]) => (
            <div key={l}><Reading label={l} value={v} unit={u} size={19} /></div>
          ))}
        </div>

        <StageNav onBack={() => go("orchestrator")} onNext={() => go("environment")} nextLabel="Load ocean data" />
      </div>

      <aside>
        <Reading label="Estimated age" value={SPILL.age} size={25} />
        <div className="note" style={{ marginTop: 10 }}>
          Derived from slick spreading and weathering rate against the environmental record. Treated as a range, never a timestamp.
        </div>

        <div className="hairline" style={{ margin: "28px 0" }} />

        <div className="label" style={{ marginBottom: 20 }}>Shape descriptors</div>
        {SPILL.descriptors.map((d, i) => (
          <div key={d.label} style={{ marginBottom: 24 }}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
              <span style={{ fontSize: 13.5 }}>{d.label}</span>
              <span className="mono" style={{ fontSize: 13, color: COLORS.baby }}>{d.value.toFixed(2)}</span>
            </div>
            <Bar value={d.value} color={COLORS.baby} delay={i * 0.08} />
            <p className="note" style={{ margin: "9px 0 0" }}>{d.note}</p>
          </div>
        ))}

        <div style={{ marginTop: 8 }}><SimTag /></div>
      </aside>
    </div>
  );
}

/* ==========================================================================
   STAGE 06 — OCEANOGRAPHIC & METEOROLOGICAL DATA
   ========================================================================== */
function Sparkline({ series, color, max }) {
  const top = max ?? Math.max(...series) * 1.15;
  const pts = series.map((v, i) => `${(i / (series.length - 1)) * 100},${40 - (v / top) * 34}`).join(" ");
  return (
    <svg viewBox="0 0 100 44" width="100%" height="58" preserveAspectRatio="none">
      <polyline points={pts} fill="none" stroke={color} strokeWidth="1.4" vectorEffect="non-scaling-stroke" />
      <polyline points={`0,44 ${pts} 100,44`} fill={color} opacity="0.1" />
    </svg>
  );
}

export function EnvironmentStage({ go }) {
  const e = ENVIRONMENT;
  return (
    <div>
      <StageHead
        step="06"
        question="How the sea is moving"
        title="Wind and current decide where the oil went"
        lede="The drift model is only as good as its forcing data. Wind, surface current, wave state and sea temperature are pulled for the six hours surrounding the acquisition."
      />

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(210px, 1fr))", gap: 26 }}>
        {[
          { icon: Wind, label: "Wind", value: e.wind.speed, unit: e.wind.unit, dir: e.wind.dir, bearing: e.wind.bearing, series: e.windSeries, color: COLORS.baby },
          { icon: Navigation2, label: "Surface current", value: e.current.speed, unit: e.current.unit, dir: e.current.dir, bearing: e.current.bearing, series: e.currentSeries, color: COLORS.cyan },
        ].map((m) => {
          const Icon = m.icon;
          return (
            <Bracket key={m.label}>
              <div style={{ padding: 22 }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
                  <span className="label">{m.label}</span>
                  <Icon size={14} color="#5A93AC" />
                </div>
                <div style={{ display: "flex", alignItems: "baseline", gap: 14 }}>
                  <span className="mono" style={{ fontSize: 34, color: COLORS.white }}>{m.value}</span>
                  <span className="mono" style={{ fontSize: 13, color: "#6FA8C4" }}>{m.unit}</span>
                  <span className="mono" style={{ fontSize: 13, color: m.color, marginLeft: "auto" }}>→ {m.dir}</span>
                </div>
                <Sparkline series={m.series} color={m.color} />
                <div className="mono" style={{ fontSize: 10, color: "#3F6B80", display: "flex", justifyContent: "space-between" }}>
                  <span>{e.hours[0]}:00</span><span>{e.hours[e.hours.length - 1]}:00 UTC</span>
                </div>
              </div>
            </Bracket>
          );
        })}

        <Bracket>
          <div style={{ padding: 22 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
              <span className="label">Sea state</span>
              <WaveIcon size={14} color="#5A93AC" />
            </div>
            <div style={{ display: "grid", gap: 22 }}>
              <Reading label="Significant wave height" value={e.wave.height} unit={e.wave.unit} size={26} sub={`Period ${e.wave.period}`} />
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <Thermometer size={13} color="#5A93AC" />
                <Reading label="Sea surface temperature" value={e.sst.value} unit={e.sst.unit} size={19} />
              </div>
            </div>
          </div>
        </Bracket>
      </div>

      {/* Combined forcing vector — the single number the drift model cares about. */}
      <div style={{ marginTop: 40, display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 40, alignItems: "center" }}>
        <div>
          <div className="label" style={{ marginBottom: 18 }}>Combined forcing</div>
          <svg viewBox="0 0 200 160" width="100%" style={{ maxWidth: 260 }}>
            <circle cx="100" cy="80" r="62" fill="none" stroke="#123244" strokeWidth="1" />
            <circle cx="100" cy="80" r="40" fill="none" stroke="#0F2938" strokeWidth="1" />
            {["N", "E", "S", "W"].map((d, i) => {
              const a = (i * 90 - 90) * (Math.PI / 180);
              return <text key={d} x={100 + Math.cos(a) * 74} y={80 + Math.sin(a) * 74 + 4} className="mono" fontSize="9" fill="#3F6B80" textAnchor="middle">{d}</text>;
            })}
            <line x1="100" y1="80" x2={100 + Math.cos((45 - 90) * Math.PI / 180) * 54} y2={80 + Math.sin((45 - 90) * Math.PI / 180) * 54}
              stroke={COLORS.baby} strokeWidth="2" />
            <line x1="100" y1="80" x2={100 + Math.cos(0) * 34} y2={80} stroke={COLORS.cyan} strokeWidth="2" />
            <circle cx="100" cy="80" r="3" fill={COLORS.white} />
          </svg>
          <div style={{ display: "flex", gap: 20, marginTop: 10 }}>
            <span className="label" style={{ color: COLORS.baby }}>— Wind</span>
            <span className="label" style={{ color: COLORS.cyan }}>— Current</span>
          </div>
        </div>

        <div>
          <p className="lede" style={{ marginTop: 0 }}>
            Wind at {e.wind.speed} kn from the {e.wind.dir} and an eastward current of {e.current.speed} kn together produce a
            net surface transport toward the east-north-east. Oil moves with roughly 3 % of the wind speed plus the full
            current — the windage term the particle model applies in the next stage.
          </p>
          <div style={{ marginTop: 20 }}>
            <Reading label="Data source" value={e.source} size={13} />
          </div>
          <div style={{ marginTop: 22 }}><SimTag /></div>
        </div>
      </div>

      <StageNav onBack={() => go("characterize")} onNext={() => go("drift")} nextLabel="Run drift analysis" />
    </div>
  );
}

/* ==========================================================================
   STAGE 07 — DRIFT ANALYSIS
   ========================================================================== */
export function DriftStage({ go }) {
  const [t, setT] = useState(2); // 0 source · 1 transport · 2 detection · 3 forecast
  const marks = ["Source window", "Transport", "Detection", "Forecast +18 h"];

  return (
    <div className="split">
      <div>
        <StageHead
          step="07"
          question="Where from, where next"
          title="Backwards to a source zone, forwards to a path"
          lede="A particle ensemble is released from the detected slick and run in reverse through the wind and current fields to a probable source zone, then forwards to project where the oil is heading."
        />

        <Bracket>
          <div style={{ position: "relative", aspectRatio: "16 / 10", background: "#051722" }}>
            <svg width="100%" height="100%" viewBox="0 0 400 250" preserveAspectRatio="xMidYMid slice">
              <defs>
                <SarTexture id="drift" frequency={0.3} seed={7} tint="#092A3C" />
                <marker id="ampt" markerWidth="8" markerHeight="8" refX="5" refY="4" orient="auto">
                  <path d="M0,1 L7,4 L0,7 Z" fill={COLORS.oil} />
                </marker>
                <marker id="blupt" markerWidth="8" markerHeight="8" refX="5" refY="4" orient="auto">
                  <path d="M0,1 L7,4 L0,7 Z" fill={COLORS.baby} />
                </marker>
              </defs>
              <rect width="400" height="250" fill="#07202D" />
              <rect width="400" height="250" filter="url(#drift)" opacity="0.6" />

              {/* source zone — a zone, never a point */}
              <g opacity={t >= 0 ? 1 : 0.2} style={{ transition: "opacity .4s" }}>
                <ellipse cx="104" cy="78" rx="30" ry="21" fill={COLORS.oil} opacity="0.12" stroke={COLORS.oil} strokeWidth="1" strokeDasharray="4 3" />
                <circle cx="104" cy="78" r="3.4" fill={COLORS.oil} />
                <text x="70" y="46" className="mono" fontSize="9" fill={COLORS.oil}>SOURCE ZONE</text>
              </g>

              {/* hindcast — amber */}
              <path d="M 216 136 C 190 122, 152 100, 112 82" fill="none" stroke={COLORS.oil} strokeWidth="1.7"
                strokeDasharray="6 4" markerEnd="url(#ampt)" opacity={t >= 1 ? 1 : 0.18} style={{ transition: "opacity .4s" }} />

              {/* detected slick */}
              <g opacity={t >= 2 ? 1 : 0.35} style={{ transition: "opacity .4s" }}>
                <ellipse cx="224" cy="140" rx="34" ry="19" fill={COLORS.critical} opacity="0.3" stroke={COLORS.critical} strokeWidth="1.2" />
                <text x="192" y="174" className="mono" fontSize="9" fill={COLORS.critical}>DETECTED SLICK</text>
              </g>

              {/* forecast — baby blue */}
              <path d="M 244 146 C 276 162, 306 180, 342 200" fill="none" stroke={COLORS.baby} strokeWidth="1.7"
                strokeDasharray="6 4" markerEnd="url(#blupt)" opacity={t >= 3 ? 1 : 0.18} style={{ transition: "opacity .4s" }} />
              <g opacity={t >= 3 ? 1 : 0.18} style={{ transition: "opacity .4s" }}>
                <ellipse cx="344" cy="202" rx="26" ry="15" fill={COLORS.baby} opacity="0.12" stroke={COLORS.baby} strokeWidth="1" strokeDasharray="4 3" />
                <text x="306" y="232" className="mono" fontSize="9" fill={COLORS.baby}>PREDICTED SPREAD</text>
              </g>
            </svg>
          </div>
        </Bracket>

        <div style={{ marginTop: 30 }}>
          <div className="label" style={{ marginBottom: 14 }}>Timeline</div>
          <input
            type="range" min={0} max={3} step={1} value={t}
            onChange={(e) => setT(Number(e.target.value))}
            aria-label="Drift timeline"
            style={{ width: "100%", accentColor: COLORS.cyan }}
          />
          <div style={{ display: "flex", justifyContent: "space-between", marginTop: 10, gap: 8 }}>
            {marks.map((m, i) => (
              <button key={m} onClick={() => setT(i)} className="mono"
                style={{
                  background: "none", border: "none", cursor: "pointer", padding: 0,
                  fontSize: 10.5, letterSpacing: "0.07em", textTransform: "uppercase",
                  color: t === i ? COLORS.white : "#3F6B80",
                }}>
                {m}
              </button>
            ))}
          </div>
        </div>

        <StageNav onBack={() => go("environment")} onNext={() => go("sourcetype")} nextLabel="Infer source type" />
      </div>

      <aside>
        <div style={{ display: "grid", gap: 24 }}>
          <div>
            <div className="label" style={{ marginBottom: 7, color: COLORS.oil }}>Hindcast — source window</div>
            <div className="mono" style={{ fontSize: 15 }}>{DRIFT.originWindow}</div>
            <div className="mono" style={{ fontSize: 12.5, color: "#5C879C", marginTop: 6 }}>{DRIFT.originZone}</div>
          </div>

          <div className="hairline" />

          <Reading label="Detection time" value={DRIFT.detection} size={14} />
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 18 }}>
            <Reading label="Uncertainty" value={DRIFT.uncertainty} size={17} />
            <Reading label="Forecast horizon" value={DRIFT.forecastHorizon} size={17} color={COLORS.baby} />
          </div>

          <div>
            <div className="label" style={{ marginBottom: 9 }}>Hindcast confidence</div>
            <Pill tone="cyan">{DRIFT.hindcastConfidence}</Pill>
          </div>

          <Reading label="Method" value={DRIFT.method} size={13} />
          <Caveat tone="warning">{DRIFT.spreadNote}</Caveat>
          <SimTag />
        </div>
      </aside>
    </div>
  );
}
