import React from "react";
import { ArrowRight, Satellite, Waves, MapPin, Clock, Ship } from "lucide-react";
import { Reading, Pill, SimTag, Caveat } from "../components/ui.jsx";
import { STAGES, PHASES } from "../data/pipeline.js";
import { COLORS, CASE } from "../data/mock.js";

export default function Overview({ go }) {
  const metrics = [
    { icon: Satellite, label: "Detection confidence", value: CASE.confidence.toFixed(2), sub: "Orchestrated" },
    { icon: Waves, label: "Spill area", value: CASE.area, unit: "km²", sub: "Irregular" },
    { icon: MapPin, label: "Estimated origin", value: CASE.aoi, small: true, sub: CASE.aoiName },
    { icon: Clock, label: "Estimated age", value: CASE.age, small: true, sub: "At acquisition" },
    { icon: Ship, label: "Vessels screened", value: CASE.vesselsScreened, sub: `${CASE.candidates} candidates` },
  ];

  return (
    <div>
      <div className="enter" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 20, flexWrap: "wrap" }}>
        <div>
          <div className="mono" style={{ fontSize: 13, color: COLORS.cyan, letterSpacing: "0.1em", marginBottom: 12 }}>
            {CASE.id}
          </div>
          <h1 style={{ fontSize: "clamp(26px, 4vw, 38px)", lineHeight: 1.12 }}>
            Suspected discharge, {CASE.aoiName}
          </h1>
        </div>
        <Pill tone="cyan">{CASE.status}</Pill>
      </div>

      <p className="lede enter d1" style={{ marginTop: 18 }}>
        A Sentinel-1 pass on {CASE.acquired} returned a dark patch consistent with surface oil. Fifteen stages
        have run end to end. Open any stage to see what it concluded and why.
      </p>

      <div className="metrics enter d2" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", marginTop: 48 }}>
        {metrics.map((m) => {
          const Icon = m.icon;
          return (
            <div key={m.label}>
              <Icon size={15} color="#5A93AC" strokeWidth={1.6} style={{ marginBottom: 16 }} />
              <Reading label={m.label} value={m.value} unit={m.unit} size={m.small ? 15 : 25} sub={m.sub} />
            </div>
          );
        })}
      </div>

      <div className="enter d3" style={{ marginTop: 60 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 24, flexWrap: "wrap", gap: 12 }}>
          <span className="label">Pipeline</span>
          <SimTag />
        </div>

        {PHASES.map((phase) => {
          const stages = STAGES.filter((s) => s.phase === phase);
          return (
            <div key={phase} style={{ display: "grid", gridTemplateColumns: "116px 1fr", gap: 20, padding: "22px 0", borderTop: "1px solid #0F3040" }}>
              <div>
                <div style={{ fontSize: 14, color: COLORS.baby }}>{phase}</div>
                <div className="mono" style={{ fontSize: 10.5, color: "#3F6B80", marginTop: 5 }}>
                  {stages[0].num}–{stages[stages.length - 1].num}
                </div>
              </div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                {stages.map((s) => (
                  <button key={s.id} onClick={() => go(s.id)} className="chip" style={{ cursor: "pointer", display: "flex", alignItems: "center", gap: 9 }}>
                    <span className="mono" style={{ fontSize: 10, color: "#3F6B80" }}>{s.num}</span>
                    {s.label}
                  </button>
                ))}
              </div>
            </div>
          );
        })}
        <div style={{ borderTop: "1px solid #0F3040" }} />
      </div>

      <div className="enter d4" style={{ marginTop: 40, maxWidth: 660 }}>
        <Caveat>
          All figures in this build are simulated demonstration data. Vessel names, MMSI and IMO numbers are fictional
          and no real vessel is implicated in any discharge.
        </Caveat>
      </div>

      <div className="enter d4" style={{ marginTop: 40 }}>
        <button className="btn btn-primary" onClick={() => go("sar")}>
          Open stage 01 <ArrowRight size={15} />
        </button>
      </div>
    </div>
  );
}
