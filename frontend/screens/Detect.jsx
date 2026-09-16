// import React, { useState, useEffect } from "react";
import React, { useState } from "react";
import { CheckCircle2, Circle, Loader2 } from "lucide-react";
import { Bracket, Reading, Pill, Bar, StageHead, StageNav, Caveat, SimTag, SarTexture, SLICK_PATH } from "../components/ui.jsx";
import { COLORS, SAR, PREPROCESS, VISION_MODELS, ORCHESTRATOR, CASE } from "../data/mock.js";

/* ==========================================================================
   STAGE 01 — SAR IMAGE
   ========================================================================== */
export function SarStage({ go }) {
 const [image, setImage] = useState(null);
  const [fileName, setFileName] = useState("");

  const handleUpload = (e) => {
    const file = e.target.files[0];

    if (!file) return;

    setFileName(file.name);
    setImage(URL.createObjectURL(file));
  };

  return (
    <div className="stage-content">

      <div className="stage-kicker">
        STAGE 01 · DETECTION
      </div>

      <h1>SAR Image Acquisition</h1>

      <p className="stage-description">
        Upload a Sentinel-1 SAR image to begin oil-spill detection.
        The uploaded image will be used for the demonstration pipeline.
      </p>

      {/* UPLOAD CARD */}
      <div className="upload-card">

        <div className="upload-icon">
          ↑
        </div>

        <h2>Upload SAR Image</h2>

        <p>
          Supported formats: JPG, JPEG, PNG, TIFF
        </p>

        <label className="upload-button">
          Choose Image
          <input
            type="file"
            accept="image/png,image/jpeg,image/jpg,image/tiff"
            onChange={handleUpload}
            hidden
          />
        </label>

        {fileName && (
          <div className="file-name">
            ✓ {fileName}
          </div>
        )}

      </div>

      {/* IMAGE PREVIEW */}
      {image && (
        <div className="image-preview-card">

          <div className="preview-header">
            <span>UPLOADED SAR IMAGE</span>
            <span className="status">READY</span>
          </div>

          <img
            src={image}
            alt="Uploaded SAR"
            className="sar-preview"
          />

        </div>
      )}

      {/* BOTTOM BUTTONS */}
      <div className="stage-actions">

        <button
          className="secondary-button"
          onClick={() => go("overview")}
        >
          ← Back
        </button>

        <button
          className="primary-button"
         onClick={() => {
          if (image) {
            go("preprocess");
          }
        }}
        disabled={!image}
      >
          Continue to preprocessing →
        </button>

      </div>

    </div>
  );
}

/* ==========================================================================
   STAGE 02 — PREPROCESSING
   ========================================================================== */
export function PreprocessStage({ go }) {
  const [done, setDone] = useState(0);
  const [running, setRunning] = useState(true);

  useEffect(() => {
    if (!running || done >= PREPROCESS.length) { if (done >= PREPROCESS.length) setRunning(false); return; }
    const id = setTimeout(() => setDone((d) => d + 1), 520);
    return () => clearTimeout(id);
  }, [done, running]);

  const cleaned = done >= PREPROCESS.length;

  return (
    <div className="split">
      <div>
        <StageHead
          step="02"
          question="Cleaning and preparing"
          title="Raw backscatter becomes an analysis-ready scene"
          lede="Five corrections run in sequence. Each one removes a source of variation that would otherwise be read as signal by the models downstream."
        />

        <div style={{ display: "grid", gridTemplateColumns: "1fr auto 1fr", gap: 18, alignItems: "center" }}>
          <Bracket>
            <div style={{ aspectRatio: "4 / 3", background: "#051722", position: "relative", overflow: "hidden" }}>
              <svg width="100%" height="100%" viewBox="0 0 200 150" preserveAspectRatio="xMidYMid slice">
                <defs><SarTexture id="rawtex" frequency={1.4} seed={9} tint="#1A4257" /></defs>
                <rect width="200" height="150" fill="#0A2A3A" />
                <rect width="200" height="150" filter="url(#rawtex)" />
                <ellipse cx="108" cy="82" rx="38" ry="22" fill="#05161F" opacity="0.7" />
              </svg>
              <div className="label" style={{ position: "absolute", bottom: 9, left: 11, fontSize: 9.5 }}>Raw SAR</div>
            </div>
          </Bracket>

          <div className="mono" style={{ color: COLORS.cyan, fontSize: 18 }}>→</div>

          <Bracket live={cleaned}>
            <div style={{ aspectRatio: "4 / 3", background: "#051722", position: "relative", overflow: "hidden" }}>
              <svg width="100%" height="100%" viewBox="0 0 200 150" preserveAspectRatio="xMidYMid slice">
                <defs><SarTexture id="cleantex" frequency={0.32} seed={3} tint="#13394C" /></defs>
                <rect width="200" height="150" fill="#0C3145" />
                <rect width="200" height="150" filter="url(#cleantex)" opacity={cleaned ? 1 : 0.35} style={{ transition: "opacity .6s" }} />
                <ellipse cx="108" cy="82" rx="38" ry="22" fill="#04121B" opacity={cleaned ? 0.92 : 0.6} />
              </svg>
              <div className="label" style={{ position: "absolute", bottom: 9, left: 11, fontSize: 9.5 }}>Preprocessed</div>
            </div>
          </Bracket>
        </div>

        <StageNav onBack={() => go("sar")} onNext={() => go("vision")} nextLabel="Run the vision models" />
      </div>

      <aside>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
          <span className="label">Correction chain</span>
          {running ? <Loader2 size={13} color={COLORS.cyan} className="spin" style={{ animation: "spin 1s linear infinite" }} /> : <Pill tone="cyan">Ready</Pill>}
        </div>

        {PREPROCESS.map((p, i) => {
          const isDone = i < done;
          const isActive = i === done && running;
          return (
            <div key={p.key} style={{ display: "flex", gap: 12, paddingBottom: 18, marginBottom: 18, borderBottom: i < PREPROCESS.length - 1 ? "1px solid #0F2938" : "none" }}>
              <div style={{ paddingTop: 2 }}>
                {isDone ? <CheckCircle2 size={15} color={COLORS.cyan} />
                  : isActive ? <Circle size={15} color={COLORS.warning} style={{ animation: "pulseDot 1s infinite" }} />
                  : <Circle size={15} color="#204A5F" />}
              </div>
              <div style={{ minWidth: 0 }}>
                <div style={{ display: "flex", justifyContent: "space-between", gap: 10, alignItems: "baseline" }}>
                  <span style={{ fontSize: 14, color: isDone ? COLORS.white : "#7FAEC7" }}>{p.name}</span>
                  {isDone && <span className="mono" style={{ fontSize: 10.5, color: "#3F6B80" }}>{p.ms} ms</span>}
                </div>
                <p className="note" style={{ margin: "7px 0 0" }}>{p.detail}</p>
              </div>
            </div>
          );
        })}

        <button className="btn btn-ghost" style={{ width: "100%", justifyContent: "center", marginTop: 4 }}
          onClick={() => { setDone(0); setRunning(true); }}>
          Re-run chain
        </button>
        <div style={{ marginTop: 22 }}><SimTag /></div>
      </aside>
    </div>
  );
}

/* ==========================================================================
   STAGE 03 — VISION MODEL LAYER
   ========================================================================== */
export function VisionStage({ go }) {
  const [focus, setFocus] = useState(null);

  return (
    <div>
      <StageHead
        step="03"
        question="Three models, one scene"
        title="Each architecture sees the slick slightly differently"
        lede="The same preprocessed scene goes to three segmentation models. They are kept independent on purpose: their disagreements are the signal that stage 04 uses to decide how much to trust the detection."
      />

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: 26 }}>
        {VISION_MODELS.map((m, i) => (
          <Bracket key={m.key} live={focus === m.key} className="enter" style={{ animationDelay: `${i * 0.08}s` }}>
            <div
              onMouseEnter={() => setFocus(m.key)}
              onMouseLeave={() => setFocus(null)}
              style={{ padding: 22, background: focus === m.key ? "rgba(53,201,245,0.04)" : "transparent", transition: "background .25s" }}
            >
              <div style={{ aspectRatio: "4 / 3", background: "#04121B", marginBottom: 20, position: "relative" }}>
                <svg width="100%" height="100%" viewBox="0 0 200 150">
                  <rect width="200" height="150" fill="#04121B" />
                  <g transform="translate(-40,-60) scale(0.62)" fill="#DDF3FB">
                    <path d={SLICK_PATH} transform={`translate(${i * 4},${i * 3}) scale(${1 + i * 0.03})`} />
                  </g>
                  <text x="10" y="142" className="mono" fontSize="8" fill="#3F6B80">PREDICTED MASK</text>
                </svg>
              </div>

              <div style={{ fontSize: 18, marginBottom: 6 }}>{m.name}</div>
              <div className="note" style={{ marginBottom: 20 }}>{m.role}</div>

              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 8 }}>
                <span className="label">Confidence</span>
                <span className="mono" style={{ fontSize: 20, color: COLORS.baby }}>{m.confidence.toFixed(2)}</span>
              </div>
              <Bar value={m.confidence} color={COLORS.baby} delay={i * 0.1} />

              <div style={{ marginTop: 20, display: "grid", gap: 10 }}>
                <div>
                  <span className="label" style={{ color: "#4E7C93" }}>Strength</span>
                  <p className="note" style={{ margin: "5px 0 0" }}>{m.strength}</p>
                </div>
                <div>
                  <span className="label" style={{ color: "#4E7C93" }}>Limitation</span>
                  <p className="note" style={{ margin: "5px 0 0" }}>{m.weakness}</p>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", paddingTop: 10, borderTop: "1px solid #0F2938" }}>
                  <span className="label">Mask area</span>
                  <span className="mono" style={{ fontSize: 13 }}>{m.area} km²</span>
                </div>
              </div>
            </div>
          </Bracket>
        ))}
      </div>

      <div style={{ marginTop: 30, maxWidth: 620 }}>
        <Caveat>
          Mask areas differ by 1.3 km² across the three models. That spread is carried forward as uncertainty rather than averaged away.
        </Caveat>
      </div>
      <div style={{ marginTop: 20 }}><SimTag /></div>

      <StageNav onBack={() => go("preprocess")} onNext={() => go("orchestrator")} nextLabel="Combine predictions" />
    </div>
  );
}

/* ==========================================================================
   STAGE 04 — ORCHESTRATOR
   ========================================================================== */
export function OrchestratorStage({ go }) {
  return (
    <div>
      <StageHead
        step="04"
        question="Decision point"
        title="One verdict from three opinions"
        lede="The orchestrator compares the masks, measures agreement, and decides whether the pipeline continues. If the models disagreed, the case would close here with no detection."
      />

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: 40, alignItems: "start" }}>
        <div>
          {/* Convergence diagram: three inputs collapsing into one output. */}
          <svg viewBox="0 0 320 260" width="100%" style={{ maxWidth: 360, display: "block" }}>
            {VISION_MODELS.map((m, i) => (
              <g key={m.key}>
                <rect x="6" y={14 + i * 58} width="108" height="40" fill="none" stroke="#1B4A60" />
                <text x="18" y={34 + i * 58} className="mono" fontSize="10" fill="#A8CBDC">{m.name}</text>
                <text x="18" y={47 + i * 58} className="mono" fontSize="8.5" fill="#4E7C93">{m.confidence.toFixed(2)}</text>
                <path
                  d={`M 114 ${34 + i * 58} C 150 ${34 + i * 58}, 158 148, 196 148`}
                  fill="none" stroke={COLORS.cyan} strokeWidth="1" opacity="0.5" className="flow-dash"
                />
              </g>
            ))}
            <rect x="198" y="124" width="112" height="48" fill="rgba(53,201,245,0.07)" stroke={COLORS.cyan} />
            <text x="212" y="145" className="mono" fontSize="9.5" fill={COLORS.cyan}>ORCHESTRATOR</text>
            <text x="212" y="160" className="mono" fontSize="8.5" fill="#7FAEC7">majority vote</text>
            <line x1="254" y1="172" x2="254" y2="206" stroke="#1B4A60" strokeWidth="1" />
            <polygon points="250,206 258,206 254,214" fill="#1B4A60" />
            <text x="214" y="236" className="mono" fontSize="10" fill={COLORS.warning}>SPILL DETECTED</text>
          </svg>

          <p className="note" style={{ marginTop: 24, maxWidth: 380 }}>{ORCHESTRATOR.rule}</p>
        </div>

        <div>
          <Bracket live>
            <div style={{ padding: "30px 28px" }}>
              <div className="label" style={{ color: COLORS.cyan, marginBottom: 16 }}>Combined result</div>
              <div style={{ fontSize: 22, color: COLORS.warning, marginBottom: 20 }}>{ORCHESTRATOR.verdict}</div>
              <div style={{ display: "flex", gap: 34, flexWrap: "wrap" }}>
                <Reading label="Confidence" value={ORCHESTRATOR.confidence.toFixed(2)} size={34} color={COLORS.cyan} />
                <Reading label="Model agreement" value={ORCHESTRATOR.agreement.toFixed(2)} size={34} />
                <Reading label="Mask IoU" value={ORCHESTRATOR.iou.toFixed(2)} size={34} />
              </div>
            </div>
          </Bracket>

          <div style={{ marginTop: 28 }}>
            {ORCHESTRATOR.decisions.map((d, i) => (
              <div key={i} style={{ padding: "15px 0", borderBottom: "1px solid #0F2938", display: "flex", justifyContent: "space-between", gap: 20, flexWrap: "wrap" }}>
                <span style={{ fontSize: 13.5, color: "#7FAEC7" }}>{d.q}</span>
                <span className="mono" style={{ fontSize: 13, color: COLORS.white, textAlign: "right" }}>{d.a}</span>
              </div>
            ))}
          </div>

          <div style={{ marginTop: 24 }}><SimTag /></div>
        </div>
      </div>

      <StageNav onBack={() => go("vision")} onNext={() => go("characterize")} nextLabel="Characterize the spill" />
    </div>
  );
}
