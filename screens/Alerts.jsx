import React, { useState } from "react";
import {
  AlertTriangle,
  Radar,
  FileText,
  Ship,
  X,
  Satellite,
  Cpu,
  Radio,
  Waves as WaveIcon,
} from "lucide-react";
import { Bracket, Reading, Pill, Bar, Caveat, SimTag } from "../components/ui.jsx";
import { COLORS, CASE, RESULT, VESSELS, SPILL, DRIFT, ORCHESTRATOR } from "../data/mock.js";

/* ==========================================================================
   ALERT DASHBOARD
   Generated from the existing CASE / RESULT / VESSELS / SPILL / DRIFT data —
   no new mock source, no backend. One alert per screened candidate vessel.
   ========================================================================== */

const EVIDENCE_SOURCES = [
  { key: "sar", label: "SAR", icon: Satellite },
  { key: "ml", label: "ML ensemble", icon: Cpu },
  { key: "ais", label: "AIS", icon: Radio },
  { key: "drift", label: "Ocean drift", icon: WaveIcon },
];

function severityOf(score) {
  if (score >= 0.7) return "HIGH";
  if (score >= 0.4) return "MEDIUM";
  return "LOW";
}

const SEVERITY_TONE = { HIGH: "critical", MEDIUM: "warning", LOW: "baby" };

function buildAlerts() {
  const candidates = VESSELS.filter((v) => v.tier === "candidate");
  return candidates.map((v) => {
    const severity = severityOf(v.score);
    return {
      id: v.mmsi,
      vessel: v,
      severity,
      status:
        v.rank === 1
          ? "Potential source identified"
          : severity === "LOW"
          ? "Screened — low correlation"
          : "Under investigation",
    };
  });
}

function AlertCard({ alert, onDismiss, go }) {
  const { vessel: v, severity, status } = alert;
  const isHigh = severity === "HIGH";

  return (
    <Bracket live={isHigh}>
      <div
        className="enter alert-card-inner"
        style={{
          padding: "26px 26px 24px",
          borderLeft: `2px solid ${isHigh ? COLORS.critical : "transparent"}`,
          background: isHigh ? "rgba(255,91,91,0.035)" : "transparent",
        }}
      >
        {/* Header row */}
        <div style={{ display: "flex", justifyContent: "space-between", gap: 16, flexWrap: "wrap", alignItems: "flex-start" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <span
              style={{
                width: 34,
                height: 34,
                display: "grid",
                placeItems: "center",
                border: `1px solid ${isHigh ? COLORS.critical : "#20536a"}`,
                color: isHigh ? COLORS.critical : COLORS.cyan,
                flexShrink: 0,
                boxShadow: isHigh ? "0 0 16px rgba(255,91,91,0.35)" : "none",
              }}
            >
              <AlertTriangle size={16} />
            </span>
            <div>
              <div className="alert-title" style={{ color: COLORS.white }}>Oil spill detected</div>
              <div className="mono alert-meta" style={{ color: "#5C879C", marginTop: 4 }}>
                {CASE.id} · {CASE.acquired}
              </div>
            </div>
          </div>

          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            <Pill tone={SEVERITY_TONE[severity]}>{severity} SEVERITY</Pill>
            <Pill tone="neutral" dot={false}>{status}</Pill>
          </div>
        </div>

        {/* Readings grid */}
        <div className="alert-readings">
          <Reading label="Detection confidence" value={ORCHESTRATOR.confidence.toFixed(2)} size={17} color={COLORS.cyan} />
          <Reading label="Estimated spill area" value={SPILL.area} unit="km²" size={17} />
          <Reading label="Suspected vessel" value={v.name} size={14} sub={`MMSI ${v.mmsi}`} />
          <Reading
            label="Vessel attribution"
            value={v.score.toFixed(2)}
            size={17}
            color={isHigh ? COLORS.critical : COLORS.baby}
          />
          <Reading label="Origin lat / long" value={SPILL.location} size={13} />
          <Reading label="Detection timestamp" value={CASE.acquired} size={12.5} />
        </div>

        <div style={{ marginTop: 18 }}>
          <Bar value={v.score} color={isHigh ? COLORS.critical : COLORS.warning} height={4} />
        </div>

        {/* Evidence sources */}
        <div style={{ marginTop: 24 }}>
          <div className="label" style={{ marginBottom: 12 }}>Evidence sources</div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
            {EVIDENCE_SOURCES.map((s) => (
              <span key={s.key} className="chip" style={{ display: "flex", alignItems: "center", gap: 7 }}>
                <s.icon size={12} /> {s.label}
              </span>
            ))}
          </div>
        </div>

        {isHigh && (
          <div style={{ marginTop: 20 }}>
            <Caveat tone="critical">
              High-severity correlation — {v.name}'s track and the reconstructed source zone overlap for a sustained
              window. Evidence score {v.score.toFixed(2)}, not a confirmed attribution.
            </Caveat>
          </div>
        )}

        {/* Actions */}
        <div className="alert-actions">
          <button className="btn btn-ghost" onClick={() => go("fusion")}>
            <Radar size={14} /> View evidence
          </button>
          <button className="btn btn-ghost" onClick={() => go("ranking")}>
            <Ship size={14} /> View vessel
          </button>
          <button className="btn btn-primary" onClick={() => go("report")}>
            <FileText size={14} /> Generate report
          </button>
          <button className="btn btn-ghost" onClick={() => onDismiss(alert.id)} style={{ marginLeft: "auto" }}>
            <X size={14} /> Dismiss
          </button>
        </div>
      </div>
    </Bracket>
  );
}

export default function Alerts({ go }) {
  const [alerts] = useState(buildAlerts);
  const [dismissed, setDismissed] = useState([]);

  const visible = alerts.filter((a) => !dismissed.includes(a.id));
  const dismissedCount = alerts.length - visible.length;

  const handleDismiss = (id) => setDismissed((ids) => [...ids, id]);

  return (
    <div className="alerts-page">

      <style>{`
        .alerts-page {
          width: 100%;
          max-width: 1100px;
          margin: 0 auto;
          box-sizing: border-box;
        }
        .alerts-page .alerts-page-header {
          margin: 0 0 28px;
          max-width: 760px;
        }
        .alerts-page .alerts-page-header h2 {
          margin: 0 !important;
          font-size: clamp(24px, 3.2vw, 32px) !important;
          line-height: 1.15 !important;
          white-space: normal !important;
          overflow-wrap: anywhere;
        }
        .alerts-page .alerts-count-row {
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 12px;
          margin-bottom: 22px;
          flex-wrap: wrap;
        }
        .alerts-page .alerts-grid {
          display: grid;
          gap: 18px;
          width: 100%;
        }
        .alerts-page .alert-card-inner {
          width: 100%;
          min-width: 0;
          box-sizing: border-box;
        }
        .alerts-page .alert-card-inner * {
          box-sizing: border-box;
          max-width: 100%;
        }
        .alerts-page .alert-title {
          font-size: 16px !important;
          line-height: 1.3 !important;
          white-space: normal !important;
          overflow-wrap: anywhere;
        }
        .alerts-page .alert-meta {
          font-size: 11px !important;
          line-height: 1.4 !important;
          white-space: normal !important;
          overflow-wrap: anywhere;
        }
        .alerts-page .alert-readings {
          display: grid;
          grid-template-columns: repeat(2, minmax(0, 1fr));
          gap: 18px;
          margin-top: 22px;
          padding-top: 20px;
          border-top: 1px solid #0F2938;
        }
        .alerts-page .alert-actions {
          display: flex;
          gap: 10px;
          flex-wrap: wrap;
          margin-top: 22px;
        }
        .alerts-page .alert-actions .btn {
          border-radius: 10px;
        }
        @media (max-width: 700px) {
          .alerts-page .alert-readings {
            grid-template-columns: 1fr;
          }
        }
      `}</style>

      <header className="alerts-page-header">
        <div className="label" style={{ color: COLORS.cyan, marginBottom: 12, display: "flex", alignItems: "center", gap: 8 }}>
          <AlertTriangle size={12} /> Investigation alerts
        </div>
        <h2 style={{ fontSize: "clamp(24px, 3.2vw, 32px)", lineHeight: 1.15 }}>
          Active alerts for {CASE.id}
        </h2>
        <p className="lede" style={{ marginTop: 14, marginBottom: 0 }}>
          One alert per screened candidate vessel, generated from the detection, drift and attribution stages
          already run for this case. {RESULT.statement}
        </p>
      </header>

      <div className="alerts-count-row">
        <div className="mono" style={{ fontSize: 11.5, color: "#4E7C93" }}>
          {visible.length} active · {dismissedCount} dismissed · {alerts.length} total
        </div>
        <SimTag />
      </div>

      {visible.length > 0 ? (
        <div className="alerts-grid">
          {visible.map((alert) => (
            <AlertCard key={alert.id} alert={alert} onDismiss={handleDismiss} go={go} />
          ))}
        </div>
      ) : (
        <Bracket>
          <div style={{ padding: "40px 26px", textAlign: "center" }}>
            <div className="label" style={{ marginBottom: 8 }}>All clear</div>
            <p className="note" style={{ margin: 0 }}>Every alert for this case has been dismissed.</p>
          </div>
        </Bracket>
      )}

      <div style={{ marginTop: 34 }}>
        <Caveat>
          Alerts reflect correlation scores from the pipeline, not confirmed attribution. Drift origin window:{" "}
          {DRIFT.originWindow}.
        </Caveat>
      </div>
    </div>
  );
}
