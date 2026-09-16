import React, { useState } from "react";
import { FileText, Download, RotateCcw, Check, Server, Terminal } from "lucide-react";
import { Bracket, Reading, Pill, Bar, StageHead, StageNav, Caveat, SimTag, SarTexture } from "../components/ui.jsx";
import { COLORS, CASE, RESULT, VESSELS, SPILL, DRIFT, ORCHESTRATOR, API_ENDPOINTS, API_SAMPLE } from "../data/mock.js";

/* ==========================================================================
   STAGE 13 — INVESTIGATION RESULT
   ========================================================================== */
export function ResultStage({ go }) {
  const top = RESULT.topCandidate;
  const chain = [
    "SAR scene", "Preprocessing", "Three vision models", "Orchestrated detection",
    "Spill geometry", "Ocean forcing", "Drift hindcast", "Source type",
    "Space-time filter", "Trajectory model", "Evidence fusion", "Ranking",
  ];

  return (
    <div className="split">
      <div>
        <StageHead
          step="13"
          question="A clear, explainable output"
          title="What the investigation can and cannot say"
          lede="The result names a source zone, a time window, a confidence level and a ranked shortlist — together with the chain of reasoning that produced each one."
        />

        <Bracket live>
          <div style={{ padding: "28px 26px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", gap: 20, flexWrap: "wrap", alignItems: "flex-start" }}>
              <div>
                <div className="label" style={{ marginBottom: 10 }}>Top candidate</div>
                <div style={{ fontSize: 26 }}>{top.name}</div>
                <div className="mono" style={{ fontSize: 12.5, color: "#5C879C", marginTop: 6 }}>
                  MMSI {top.mmsi} · IMO {top.imo} · {top.type}
                </div>
              </div>
              <div style={{ textAlign: "right" }}>
                <div className="label" style={{ marginBottom: 8 }}>Evidence score</div>
                <div className="mono" style={{ fontSize: 44, lineHeight: 1, color: COLORS.critical }}>{top.score.toFixed(2)}</div>
              </div>
            </div>

            <div style={{ marginTop: 24 }}><Bar value={top.score} color={COLORS.critical} height={6} /></div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: 24, marginTop: 30 }}>
              <Reading label="Probable source zone" value={RESULT.sourceZone} size={14} />
              <Reading label="Source time window" value={RESULT.sourceWindow} size={14} />
              <Reading label="Confidence" value={RESULT.confidence} size={14} />
            </div>

            <div style={{ marginTop: 26, display: "flex", gap: 10, flexWrap: "wrap" }}>
              <Pill tone="warning">Potential source</Pill>
              <Pill tone="neutral" dot={false}>Not confirmed attribution</Pill>
            </div>
          </div>
        </Bracket>

        <p style={{ fontSize: 15.5, color: "#A8CBDC", lineHeight: 1.75, marginTop: 30, maxWidth: 620 }}>
          {RESULT.statement}
        </p>

        <div style={{ marginTop: 34 }}>
          <div className="label" style={{ marginBottom: 16 }}>Reasoning chain</div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
            {chain.map((c, i) => (
              <span key={c} className="chip" style={{ fontSize: 11.5, padding: "7px 11px" }}>
                <span className="mono" style={{ color: "#3F6B80", marginRight: 7 }}>{String(i + 1).padStart(2, "0")}</span>
                {c}
              </span>
            ))}
          </div>
        </div>

        <StageNav onBack={() => go("ranking")} onNext={() => go("api")} nextLabel="See the API layer" />
      </div>

      <aside>
        <div className="label" style={{ marginBottom: 20 }}>Other candidates</div>
        {VESSELS.filter((v) => v.tier === "candidate").map((v) => (
          <div key={v.mmsi} style={{ paddingBottom: 16, marginBottom: 16, borderBottom: "1px solid #0F2938" }}>
            <div style={{ display: "flex", justifyContent: "space-between", gap: 10, marginBottom: 8 }}>
              <span style={{ fontSize: 13.5 }}>{v.name}</span>
              <span className="mono" style={{ fontSize: 14, color: v.rank === 1 ? COLORS.critical : COLORS.baby }}>{v.score.toFixed(2)}</span>
            </div>
            <Bar value={v.score} color={v.rank === 1 ? COLORS.critical : COLORS.baby} height={3} />
          </div>
        ))}

        <div style={{ marginTop: 26 }}>
          <Caveat>
            Transparency is the point of showing all three: a shortlist with visible spread supports an investigator's
            judgement instead of replacing it.
          </Caveat>
        </div>
        <div style={{ marginTop: 22 }}><SimTag /></div>
      </aside>
    </div>
  );
}

/* ==========================================================================
   STAGE 14 — API LAYER
   ========================================================================== */
const METHOD_COLOR = { GET: COLORS.cyan, POST: COLORS.warning };

export function ApiStage({ go }) {
  const [sel, setSel] = useState(API_ENDPOINTS[3].path);

  return (
    <div className="split">
      <div>
        <StageHead
          step="14"
          question="Making it accessible"
          title="The whole pipeline behind one HTTP interface"
          lede="Every stage is wrapped in a FastAPI service. A client uploads a scene, polls the case, and receives the same structured record the interface renders — so the analysis is usable from a ship, a coastguard system or a notebook."
        />

        <div style={{ border: "1px solid #0F3040" }}>
          {API_ENDPOINTS.map((e, i) => (
            <button key={e.path} onClick={() => setSel(e.path)}
              style={{
                display: "flex", alignItems: "center", gap: 16, width: "100%", textAlign: "left",
                padding: "16px 20px", cursor: "pointer", background: sel === e.path ? "rgba(53,201,245,0.05)" : "transparent",
                border: "none", borderBottom: i < API_ENDPOINTS.length - 1 ? "1px solid #0F2938" : "none",
                borderLeft: `2px solid ${sel === e.path ? COLORS.cyan : "transparent"}`,
                transition: "background .2s, border-color .2s", flexWrap: "wrap",
              }}>
              <span className="mono" style={{ fontSize: 11, color: METHOD_COLOR[e.method], width: 42, flexShrink: 0 }}>{e.method}</span>
              <span className="mono" style={{ fontSize: 13, color: COLORS.white }}>{e.path}</span>
              <span className="note" style={{ marginLeft: "auto", textAlign: "right" }}>{e.desc}</span>
              <span className="mono" style={{ fontSize: 10.5, color: "#3F6B80", width: 54, textAlign: "right" }}>{e.time}</span>
            </button>
          ))}
        </div>

        <div style={{ marginTop: 30 }}>
          <div className="label" style={{ marginBottom: 14, display: "flex", alignItems: "center", gap: 8 }}>
            <Terminal size={12} /> Response shape
          </div>
          <Bracket>
            <pre className="mono scroll" style={{
              margin: 0, padding: "22px 24px", fontSize: 12.2, lineHeight: 1.75,
              color: "#A8CBDC", background: "#04141F", overflowX: "auto",
            }}>
{API_SAMPLE}
            </pre>
          </Bracket>
        </div>

        <StageNav onBack={() => go("result")} onNext={() => go("report")} nextLabel="Build the report" />
      </div>

      <aside>
        <div className="label" style={{ marginBottom: 18, display: "flex", alignItems: "center", gap: 8 }}>
          <Server size={12} /> Service
        </div>
        <div style={{ display: "grid", gap: 22 }}>
          <Reading label="Framework" value="FastAPI" size={19} sub="Python 3.11 · Uvicorn" />
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 18 }}>
            <Reading label="Median latency" value="51" unit="ms" size={18} />
            <Reading label="Uptime (30 d)" value="99.7" unit="%" size={18} />
          </div>
          <Reading label="Auth" value="API key + scoped tokens" size={13} />
          <Reading label="Formats" value="JSON · GeoJSON · PDF" size={13} />
        </div>

        <div className="hairline" style={{ margin: "26px 0" }} />
        <Caveat>
          Every response carries the disclaimer field. Downstream systems consume the qualification along with the score.
        </Caveat>
        <div style={{ marginTop: 22 }}><SimTag>Simulated service metrics</SimTag></div>
      </aside>
    </div>
  );
}

/* ==========================================================================
   STAGE 15 — REPORT & EXPORT
   ========================================================================== */
export function ReportStage({ go, onRestart }) {
  const [generated, setGenerated] = useState(false);
  const top = RESULT.topCandidate;

  const rows = [
    ["Case", CASE.id],
    ["Scene", "Sentinel-1 IW GRD · 27 Aug 2026 06:52 UTC"],
    ["Detection", `Spill detected · confidence ${ORCHESTRATOR.confidence.toFixed(2)}`],
    ["Models", "U-Net · DeepLabV3+ · TransUNet (orchestrated)"],
    ["Spill", `${SPILL.area} km² · ${SPILL.shape} · age ${SPILL.age}`],
    ["Ocean forcing", "Wind 14 kn NE · current 0.8 kn E"],
    ["Source zone", DRIFT.originZone],
    ["Source window", DRIFT.originWindow],
    ["Vessels screened", `${CASE.vesselsScreened} · ${CASE.candidates} candidates`],
    ["Top candidate", `${top.name} · MMSI ${top.mmsi}`],
    ["Evidence score", `${top.score.toFixed(2)} / 1.00`],
    ["Status", "Potential source — not confirmed attribution"],
  ];

  return (
    <div>
      <StageHead
        step="15"
        question="Handing it over"
        title="One record an investigator can act on"
        lede="The report collects every stage's output, its confidence and its caveats into a single document, ready to pass to an enforcement authority or archive against the case."
      />

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: 44, alignItems: "start" }}>
        <Bracket>
          <div>
            {rows.map(([k, v], i) => (
              <div key={k} style={{
                display: "flex", justifyContent: "space-between", gap: 24, padding: "14px 22px",
                borderBottom: i < rows.length - 1 ? "1px solid #0F2938" : "none", flexWrap: "wrap",
              }}>
                <span className="label" style={{ fontSize: 10.5 }}>{k}</span>
                <span className="mono" style={{ fontSize: 12.5, color: "#D5EBF5", textAlign: "right" }}>{v}</span>
              </div>
            ))}
          </div>
        </Bracket>

        <div>
          <div className="metrics" style={{ gridTemplateColumns: "1fr 1fr" }}>
            <div><Reading label="Spill area" value={SPILL.area} unit="km²" size={24} /></div>
            <div><Reading label="Detection confidence" value={ORCHESTRATOR.confidence.toFixed(2)} size={24} color={COLORS.cyan} /></div>
            <div><Reading label="Vessels screened" value={CASE.vesselsScreened} size={24} /></div>
            <div><Reading label="Evidence score" value={top.score.toFixed(2)} size={24} color={COLORS.critical} /></div>
          </div>

          <div style={{ marginTop: 30, display: "flex", gap: 12, flexWrap: "wrap" }}>
            <button className="btn btn-primary" onClick={() => setGenerated(true)}>
              {generated ? <><Check size={15} /> Report generated</> : <><FileText size={15} /> Generate report</>}
            </button>
            <button className="btn btn-ghost"><Download size={15} /> Export evidence</button>
          </div>

          {generated && (
            <div className="enter" style={{ marginTop: 20 }}>
              <div style={{ display: "flex", justifyContent: "space-between", padding: "14px 18px", border: "1px solid #1B4A60", flexWrap: "wrap", gap: 10 }}>
                <span className="mono" style={{ fontSize: 12.5 }}>sagardhristi-2026-0417.pdf</span>
                <span className="mono" style={{ fontSize: 11.5, color: "#4E7C93" }}>18 pages · 4.2 MB</span>
              </div>
            </div>
          )}

          <div style={{ marginTop: 30 }}>
            <Caveat tone="warning">
              The report states a correlation and its uncertainty. It does not assert that any vessel caused a discharge,
              and it is not a substitute for physical sampling, inspection or legal process.
            </Caveat>
          </div>

          <div style={{ marginTop: 34, paddingTop: 22, borderTop: "1px solid #0F3040" }}>
            <button className="btn btn-ghost" onClick={onRestart}>
              <RotateCcw size={15} /> Start new investigation
            </button>
          </div>

          <div style={{ marginTop: 26 }}><SimTag /></div>
        </div>
      </div>

      <div style={{ marginTop: 56, paddingTop: 22, borderTop: "1px solid #0F3040", display: "flex", gap: 24, flexWrap: "wrap" }}>
        <span className="label" style={{ fontSize: 10 }}>Cleaner oceans</span>
        <span className="label" style={{ fontSize: 10 }}>Safer ecosystems</span>
        <span className="label" style={{ fontSize: 10 }}>Data-driven enforcement</span>
      </div>
    </div>
  );
}
