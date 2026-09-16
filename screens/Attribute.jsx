import React, { useState } from "react";
import { Ship, Factory, HelpCircle } from "lucide-react";
import { Bracket, Reading, Pill, Bar, StageHead, StageNav, Caveat, SimTag, SarTexture } from "../components/ui.jsx";
import { COLORS, SOURCE_TYPES, FILTER_FUNNEL, VESSELS, EVIDENCE_FACTORS } from "../data/mock.js";

const ICONS = { vessel: Ship, fixed: Factory, unknown: HelpCircle };

/* ==========================================================================
   STAGE 08 — SOURCE TYPE CHECK
   ========================================================================== */
export function SourceTypeStage({ go }) {
  const top = SOURCE_TYPES[0];
  return (
    <div>
      <StageHead
        step="08"
        question="What kind of source"
        title="Vessel attribution only runs if a vessel is plausible"
        lede="Slick shape, position and surrounding context are weighed against three possibilities. If the evidence pointed to a fixed installation or a natural seep, the pipeline would stop here rather than build a case against passing ships."
      />

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(230px, 1fr))", gap: 26 }}>
        {SOURCE_TYPES.map((s) => {
          const Icon = ICONS[s.key];
          const lead = s.key === top.key;
          return (
            <Bracket key={s.key} live={lead}>
              <div style={{ padding: 24, background: lead ? "rgba(53,201,245,0.04)" : "transparent" }}>
                <Icon size={20} color={lead ? COLORS.cyan : "#3F6B80"} strokeWidth={1.5} />
                <div style={{ fontSize: 19, marginTop: 18 }}>{s.name}</div>
                <div className="note" style={{ marginBottom: 22 }}>{s.desc}</div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 8 }}>
                  <span className="label">Likelihood</span>
                  <span className="mono" style={{ fontSize: 19, color: lead ? COLORS.cyan : "#7FAEC7" }}>{s.score.toFixed(2)}</span>
                </div>
                <Bar value={s.score} color={lead ? COLORS.cyan : "#2C5A70"} />
                <p className="note" style={{ marginTop: 16 }}>{s.evidence}</p>
              </div>
            </Bracket>
          );
        })}
      </div>

      <div style={{ marginTop: 34, maxWidth: 640 }}>
        <Caveat>
          Vessel source is the leading hypothesis at {top.score.toFixed(2)}. That opens the AIS search — it does not
          implicate any particular ship.
        </Caveat>
      </div>
      <div style={{ marginTop: 20 }}><SimTag /></div>

      <StageNav onBack={() => go("drift")} onNext={() => go("spacetime")} nextLabel="Filter AIS traffic" />
    </div>
  );
}

/* ==========================================================================
   STAGE 09 — SPACE-TIME FILTER
   ========================================================================== */
export function SpaceTimeStage({ go }) {
  const [step, setStep] = useState(FILTER_FUNNEL.length - 1);
  const visible = VESSELS.filter((v, i) => (step >= 4 ? i < 3 : step >= 3 ? i < 5 : step >= 2 ? i < 7 : true));

  return (
    <div className="split">
      <div>
        <StageHead
          step="09"
          question="Finding candidates"
          title="Who was inside the source zone, during the source window"
          lede="AIS position reports are filtered on two axes at once: space, against the hindcast zone, and time, against the estimated release window. Everything outside either bound drops out."
        />

        <Bracket>
          <div style={{ position: "relative", aspectRatio: "16 / 10", background: "#051722" }}>
            <svg width="100%" height="100%" viewBox="0 0 100 62.5" preserveAspectRatio="xMidYMid slice">
              <defs><SarTexture id="ais" frequency={0.26} seed={11} tint="#0A2A3A" /></defs>
              <rect width="100" height="62.5" fill="#07202D" />
              <rect width="100" height="62.5" filter="url(#ais)" opacity="0.5" />
              {Array.from({ length: 6 }).map((_, i) => (
                <line key={`h${i}`} x1="0" y1={i * 12.5} x2="100" y2={i * 12.5} stroke="#0F2938" strokeWidth="0.15" />
              ))}
              {Array.from({ length: 7 }).map((_, i) => (
                <line key={`v${i}`} x1={i * 16.6} y1="0" x2={i * 16.6} y2="62.5" stroke="#0F2938" strokeWidth="0.15" />
              ))}

              <ellipse cx="58" cy="44" rx="13" ry="10" fill={COLORS.oil} opacity="0.1" stroke={COLORS.oil} strokeWidth="0.3" strokeDasharray="1.2 1" />
              <circle cx="58" cy="44" r="1.1" fill={COLORS.oil} />
              <text x="60.5" y="42" className="mono" fontSize="2.3" fill={COLORS.oil}>SOURCE ZONE</text>

              {visible.map((v) => {
                const isCand = v.tier === "candidate";
                const isTop = v.rank === 1;
                const col = isTop ? COLORS.critical : isCand ? COLORS.warning : COLORS.cyan;
                const pts = v.track.map((p) => `${p[0]},${p[1] * 0.625}`).join(" ");
                const [cx, cy] = v.track[4];
                return (
                  <g key={v.mmsi}>
                    <polyline points={pts} fill="none" stroke={col} strokeWidth="0.25" opacity="0.45" strokeDasharray="1 0.8" />
                    <circle cx={cx} cy={cy * 0.625} r={isTop ? 1.5 : 1.1} fill={col} />
                    {isCand && <text x={cx + 2} y={cy * 0.625 + 1} className="mono" fontSize="2" fill={col}>{v.mmsi}</text>}
                  </g>
                );
              })}
            </svg>

            <div style={{ position: "absolute", top: 12, right: 14, display: "flex", gap: 14, flexWrap: "wrap" }}>
              {[["Other vessels", COLORS.cyan], ["Candidates", COLORS.warning], ["Top candidate", COLORS.critical]].map(([l, c]) => (
                <span key={l} style={{ display: "flex", alignItems: "center", gap: 6 }}>
                  <span style={{ width: 6, height: 6, borderRadius: "50%", background: c }} />
                  <span className="label" style={{ fontSize: 9 }}>{l}</span>
                </span>
              ))}
            </div>
          </div>
        </Bracket>

        <StageNav onBack={() => go("sourcetype")} onNext={() => go("trajectory")} nextLabel="Analyse trajectories" />
      </div>

      <aside>
        <div className="label" style={{ marginBottom: 20 }}>Filter funnel</div>
        {FILTER_FUNNEL.map((f, i) => {
          const on = i <= step;
          return (
            <button key={f.label} onClick={() => setStep(i)}
              style={{
                display: "block", width: "100%", textAlign: "left", background: "none", cursor: "pointer",
                border: "none", borderLeft: `2px solid ${on ? COLORS.cyan : "#153545"}`,
                padding: "0 0 0 16px", marginBottom: 20, transition: "border-color .25s",
              }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", gap: 12 }}>
                <span style={{ fontSize: 13.5, color: on ? COLORS.white : "#4E7C93" }}>{f.label}</span>
                <span className="mono" style={{ fontSize: 17, color: on ? COLORS.cyan : "#3F6B80" }}>{f.count}</span>
              </div>
              <div className="note" style={{ marginTop: 5 }}>{f.note}</div>
            </button>
          );
        })}

        <div className="hairline" style={{ margin: "8px 0 22px" }} />
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 18 }}>
          <Reading label="Search radius" value="12" unit="NM" size={17} />
          <Reading label="Time window" value="±3" unit="hrs" size={17} />
        </div>
        <div style={{ marginTop: 22 }}><SimTag /></div>
      </aside>
    </div>
  );
}

/* ==========================================================================
   STAGE 10 — VESSEL TRAJECTORY ANALYSIS (RNN)
   ========================================================================== */
export function TrajectoryStage({ go }) {
  const candidates = VESSELS.filter((v) => v.tier === "candidate");
  const [sel, setSel] = useState(candidates[0].mmsi);
  const v = candidates.find((c) => c.mmsi === sel);

  return (
    <div className="split">
      <div>
        <StageHead
          step="10"
          question="How each vessel moved"
          title="A sequence model, not a nearest-ship shortcut"
          lede="For every candidate, twelve timesteps of seven AIS features — position, speed, course, rate of turn and their deltas — are fed to a recurrent model. It predicts the vessel's likely movement and checks whether that movement is consistent with the slick's geometry and timing."
        />

        <div style={{ display: "flex", gap: 8, marginBottom: 22, flexWrap: "wrap" }}>
          {candidates.map((c) => (
            <button key={c.mmsi} onClick={() => setSel(c.mmsi)} className="chip"
              style={{
                cursor: "pointer",
                borderColor: sel === c.mmsi ? "#2C7A9E" : "#163B4E",
                color: sel === c.mmsi ? COLORS.cyan : "#9AC4DA",
                background: sel === c.mmsi ? "rgba(53,201,245,0.06)" : "#061826",
              }}>
              {c.name}
            </button>
          ))}
        </div>

        <Bracket>
          <div style={{ padding: "26px 24px", background: "#051722" }}>
            <svg viewBox="0 0 520 190" width="100%">
              {/* observed AIS track */}
              <text x="6" y="16" className="mono" fontSize="9" fill="#4E7C93">OBSERVED AIS TRACK (12 STEPS)</text>
              <polyline
                points={v.track.map((p, i) => `${20 + i * 34},${150 - p[1] * 0.9}`).join(" ")}
                fill="none" stroke={COLORS.cyan} strokeWidth="1.4"
              />
              {v.track.map((p, i) => (
                <circle key={i} cx={20 + i * 34} cy={150 - p[1] * 0.9} r="2.6" fill={COLORS.cyan} />
              ))}

              {/* RNN block */}
              <rect x="270" y="52" width="92" height="76" fill="rgba(53,201,245,0.06)" stroke="#2C7A9E" />
              <text x="298" y="78" className="mono" fontSize="11" fill={COLORS.cyan}>RNN</text>
              <text x="282" y="94" className="mono" fontSize="7.5" fill="#7FAEC7">12 × 7 features</text>
              {[0, 1, 2].map((r) =>
                [0, 1, 2].map((c) => (
                  <circle key={`${r}${c}`} cx={286 + c * 26} cy={106 + r * 7} r="1.6" fill="#2C7A9E" opacity="0.7" />
                ))
              )}

              {/* predicted continuation */}
              <text x="378" y="16" className="mono" fontSize="9" fill="#4E7C93">PREDICTED MOVEMENT</text>
              <polyline
                points={v.track.slice(3).map((p, i) => `${378 + i * 32},${150 - p[1] * 0.9 - 8}`).join(" ")}
                fill="none" stroke={COLORS.warning} strokeWidth="1.4" strokeDasharray="5 4" className="flow-dash"
              />
              <line x1="230" y1="90" x2="266" y2="90" stroke="#1B4A60" strokeWidth="1" />
              <line x1="366" y1="90" x2="374" y2="90" stroke="#1B4A60" strokeWidth="1" />
              <line x1="6" y1="168" x2="514" y2="168" stroke="#0F2938" strokeWidth="1" />
              <text x="6" y="182" className="mono" fontSize="8" fill="#3F6B80">−6 h</text>
              <text x="478" y="182" className="mono" fontSize="8" fill="#3F6B80">+2 h</text>
            </svg>
          </div>
        </Bracket>

        <p className="note" style={{ marginTop: 22, maxWidth: 620 }}>{v.rnn.note}</p>

        <StageNav onBack={() => go("spacetime")} onNext={() => go("fusion")} nextLabel="Fuse the evidence" />
      </div>

      <aside>
        <div style={{ fontSize: 20, marginBottom: 4 }}>{v.name}</div>
        <div className="mono" style={{ fontSize: 12.5, color: "#5C879C", marginBottom: 24 }}>{v.type} · {v.length} m</div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
          <Reading label="MMSI" value={v.mmsi} size={13} />
          <Reading label="IMO" value={v.imo} size={13} />
          <Reading label="Distance" value={v.distance} unit="NM" size={18} />
          <Reading label="Time offset" value={`${v.timeOffset > 0 ? "+" : ""}${v.timeOffset}`} unit="min" size={18}
            color={v.timeOffset < 0 ? COLORS.warning : COLORS.baby} />
          <Reading label="Speed" value={v.speed} unit="kn" size={18} />
          <Reading label="Heading" value={v.heading} unit="°" size={18} />
        </div>

        <div className="hairline" style={{ margin: "26px 0" }} />

        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
          <span className="label">Trajectory match</span>
          <span className="mono" style={{ fontSize: 15, color: COLORS.cyan }}>{v.rnn.match.toFixed(2)}</span>
        </div>
        <Bar value={v.rnn.match} color={COLORS.cyan} />

        <div style={{ marginTop: 24 }}>
          <div className="label" style={{ marginBottom: 9 }}>Behaviour note</div>
          <p className="note" style={{ margin: 0 }}>{v.anomaly}</p>
        </div>

        <div style={{ marginTop: 22 }}>
          <Reading label="AIS gap in window" value={v.aisGap} size={16} color={v.aisGap === "0 min" ? COLORS.white : COLORS.warning} />
        </div>
        <div style={{ marginTop: 22 }}><SimTag /></div>
      </aside>
    </div>
  );
}

/* ==========================================================================
   STAGE 11 — EVIDENCE FUSION
   ========================================================================== */
export function FusionStage({ go }) {
  const candidates = VESSELS.filter((v) => v.tier === "candidate");
  const [sel, setSel] = useState(candidates[0].mmsi);
  const v = candidates.find((c) => c.mmsi === sel);

  return (
    <div>
      <StageHead
        step="11"
        question="Putting the pieces together"
        title="Five independent signals, one weighted score"
        lede="No single factor decides anything. Each answers a different question about a candidate, carries its own weight, and contributes to a combined evidence score that stays inspectable."
      />

      <div style={{ display: "flex", gap: 8, marginBottom: 32, flexWrap: "wrap" }}>
        {candidates.map((c) => (
          <button key={c.mmsi} onClick={() => setSel(c.mmsi)} className="chip"
            style={{
              cursor: "pointer",
              borderColor: sel === c.mmsi ? "#2C7A9E" : "#163B4E",
              color: sel === c.mmsi ? COLORS.cyan : "#9AC4DA",
              background: sel === c.mmsi ? "rgba(53,201,245,0.06)" : "#061826",
            }}>
            {c.name} · {c.score.toFixed(2)}
          </button>
        ))}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 44, alignItems: "start" }}>
        <div>
          {EVIDENCE_FACTORS.map((f, i) => (
            <div key={f.key} style={{ marginBottom: 26 }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", gap: 12, marginBottom: 7 }}>
                <span style={{ fontSize: 14 }}>{f.label}</span>
                <span style={{ display: "flex", alignItems: "baseline", gap: 12 }}>
                  <span className="mono" style={{ fontSize: 10, color: "#3F6B80" }}>w {f.weight.toFixed(2)}</span>
                  <span className="mono" style={{ fontSize: 15, color: COLORS.cyan }}>{v[f.key].toFixed(2)}</span>
                </span>
              </div>
              <Bar value={v[f.key]} color={COLORS.cyan} delay={i * 0.07} />
              <div className="note" style={{ marginTop: 7, color: "#4E7C93" }}>{f.question}</div>
            </div>
          ))}
        </div>

        <div>
          <Bracket live>
            <div style={{ padding: "30px 26px" }}>
              <div className="label" style={{ marginBottom: 14 }}>Combined evidence score</div>
              <div style={{ display: "flex", alignItems: "baseline", gap: 10 }}>
                <span className="mono" style={{ fontSize: 56, lineHeight: 1, color: v.rank === 1 ? COLORS.critical : COLORS.baby }}>
                  {v.score.toFixed(2)}
                </span>
                <span className="mono" style={{ fontSize: 14, color: "#4E7C93" }}>/ 1.00</span>
              </div>
              <div style={{ marginTop: 20 }}>
                <Bar value={v.score} color={v.rank === 1 ? COLORS.critical : COLORS.baby} height={7} />
              </div>
              <div style={{ marginTop: 22, display: "flex", gap: 10, flexWrap: "wrap" }}>
                <Pill tone={v.rank === 1 ? "warning" : "neutral"}>{v.rank === 1 ? "Potential source" : "Candidate"}</Pill>
                <Pill tone="neutral" dot={false}>Not confirmed attribution</Pill>
              </div>
            </div>
          </Bracket>

          <div style={{ marginTop: 26 }}>
            <Caveat>
              A high score means the vessel's recorded movement correlates strongly with the reconstructed source zone
              and window. Correlation is a reason to investigate further — it is not evidence of discharge.
            </Caveat>
          </div>
          <div style={{ marginTop: 22 }}><SimTag /></div>
        </div>
      </div>

      <StageNav onBack={() => go("trajectory")} onNext={() => go("ranking")} nextLabel="Rank candidates" />
    </div>
  );
}

/* ==========================================================================
   STAGE 12 — VESSEL RANKING
   ========================================================================== */
export function RankingStage({ go }) {
  const [onlyCandidates, setOnlyCandidates] = useState(false);
  const rows = (onlyCandidates ? VESSELS.filter((v) => v.tier === "candidate") : VESSELS)
    .slice()
    .sort((a, b) => b.score - a.score);

  return (
    <div>
      <StageHead
        step="12"
        question="Most likely source"
        title="A shortlist, with every score shown"
        lede="Candidates are ordered by combined evidence score. Lower-ranked vessels stay visible: showing the spread is what makes the top result interpretable rather than authoritative."
      />

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 16, marginBottom: 22, flexWrap: "wrap" }}>
        <button className="btn btn-ghost" style={{ padding: "9px 18px", fontSize: 12.5 }} onClick={() => setOnlyCandidates((v) => !v)}>
          {onlyCandidates ? "Show all screened vessels" : "Show candidates only"}
        </button>
        <SimTag>Fictional vessel identities</SimTag>
      </div>

      <div style={{ overflowX: "auto" }} className="scroll">
        <table className="data" style={{ minWidth: 820 }}>
          <thead>
            <tr>
              {["Rank", "Vessel", "Distance", "Time offset", "Trajectory", "Behaviour", "AIS gap", "Score"].map((h) => (
                <th key={h} className="label">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((v) => {
              const top = v.rank === 1;
              const cand = v.tier === "candidate";
              return (
                <tr key={v.mmsi} style={{ background: top ? "rgba(255,91,91,0.05)" : "transparent" }}>
                  <td className="mono" style={{ fontSize: 13, color: top ? COLORS.critical : "#5C879C" }}>
                    {String(v.rank).padStart(2, "0")}
                  </td>
                  <td>
                    <div style={{ fontSize: 14 }}>{v.name}</div>
                    <div className="mono" style={{ fontSize: 11, color: "#4E7C93", marginTop: 3 }}>
                      MMSI {v.mmsi} · {v.type}
                    </div>
                  </td>
                  <td className="mono" style={{ fontSize: 13 }}>{v.distance} NM</td>
                  <td className="mono" style={{ fontSize: 13, color: v.timeOffset < 0 ? COLORS.warning : "#7FAEC7" }}>
                    {v.timeOffset > 0 ? "+" : ""}{v.timeOffset} min
                  </td>
                  <td style={{ width: 110 }}><Bar value={v.trajectory} color={COLORS.baby} height={4} /></td>
                  <td style={{ width: 110 }}><Bar value={v.behaviour} color={COLORS.oil} height={4} /></td>
                  <td className="mono" style={{ fontSize: 13, color: v.aisGap === "0 min" ? "#5C879C" : COLORS.warning }}>{v.aisGap}</td>
                  <td>
                    <span className="mono" style={{ fontSize: 17, color: top ? COLORS.critical : cand ? COLORS.warning : COLORS.baby }}>
                      {v.score.toFixed(2)}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div style={{ marginTop: 34, maxWidth: 680 }}>
        <Caveat tone="warning">
          Ranked highest does not mean responsible. These are attribution correlation scores intended to prioritise
          which vessels an investigator should examine, with physical inspection and sampling still required.
        </Caveat>
      </div>

      <StageNav onBack={() => go("fusion")} onNext={() => go("result")} nextLabel="View result" />
    </div>
  );
}
