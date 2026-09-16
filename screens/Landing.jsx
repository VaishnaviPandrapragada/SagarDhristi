import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { ArrowRight, Waves } from "lucide-react";
import OceanScene from "../three/OceanScene.jsx";
import { COLORS } from "../data/mock.js";

const rise = {
  hidden: { opacity: 0, y: 18 },
  show: (i) => ({
    opacity: 1,
    y: 0,
    transition: { delay: 0.25 + i * 0.12, duration: 0.8, ease: [0.16, 0.8, 0.24, 1] },
  }),
};

export default function Landing({ onStart, onExplore }) {
  const [showTech, setShowTech] = useState(false);

  useEffect(() => {
    if (!showTech) return;
    const el = document.getElementById("technology");
    if (el) el.scrollIntoView({ behavior: "smooth" });
  }, [showTech]);

  return (
    <div>
      <section style={{ position: "relative", height: "100vh", minHeight: 620, overflow: "hidden" }}>
        <OceanScene />

        {/* Kept deliberately light — the water is the hero, not the copy. */}
        <div
          style={{
            position: "absolute",
            inset: 0,
            pointerEvents: "none",
            background:
              "radial-gradient(ellipse at 50% 34%, transparent 30%, rgba(3,16,24,0.5) 100%), linear-gradient(180deg, rgba(3,16,24,0.62) 0%, transparent 20%, transparent 66%, rgba(3,16,24,0.82) 100%)",
          }}
        />

        <div style={{ position: "relative", zIndex: 2, height: "100%", display: "flex", flexDirection: "column" }}>
          <motion.header
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1.2, delay: 0.4 }}
            style={{
              display: "flex", justifyContent: "space-between", alignItems: "center",
              gap: 16, padding: "26px clamp(20px, 4vw, 48px)", flexWrap: "wrap",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <Waves size={17} color={COLORS.cyan} />
              <span className="label" style={{ color: COLORS.baby, fontSize: 11.5 }}>Sagar Dhristi</span>
            </div>
            <span className="label" style={{ fontSize: 10 }}>Sentinel-1 · AI · Ocean dynamics · AIS</span>
          </motion.header>

          <div
            style={{
              flex: 1, display: "flex", flexDirection: "column", justifyContent: "center",
              alignItems: "center", textAlign: "center", padding: "0 20px",
            }}
          >
            <motion.h1
              custom={0}
              variants={rise}
              initial="hidden"
              animate="show"
              style={{
                fontSize: "clamp(42px, 9vw, 104px)",
                fontWeight: 200,
                lineHeight: 0.98,
                letterSpacing: "-0.01em",
                textShadow: "0 0 60px rgba(53,201,245,0.28)",
              }}
            >
              Sagar <span style={{ color: COLORS.cyan, fontWeight: 300 }}>Dhristi</span>
            </motion.h1>

            <motion.p
              custom={1}
              variants={rise}
              initial="hidden"
              animate="show"
              style={{ fontSize: "clamp(16px, 2.3vw, 23px)", color: COLORS.baby, marginTop: 24, marginBottom: 0, fontWeight: 200 }}
            >
              See the spill. Trace the source.
            </motion.p>

            <motion.p
              custom={2}
              variants={rise}
              initial="hidden"
              animate="show"
              className="lede"
              style={{ maxWidth: 480, marginTop: 16, textAlign: "center" }}
            >
              AI-powered satellite intelligence for marine oil spill detection and vessel attribution.
            </motion.p>

            <motion.div
              custom={3}
              variants={rise}
              initial="hidden"
              animate="show"
              style={{ display: "flex", gap: 14, marginTop: 42, flexWrap: "wrap", justifyContent: "center" }}
            >
              <button className="btn btn-primary" onClick={onStart}>
                Start investigation <ArrowRight size={16} />
              </button>
              <button className="btn btn-ghost" onClick={() => { setShowTech(true); onExplore && onExplore(); }}>
                Explore the technology
              </button>
            </motion.div>

            <motion.div
              custom={4}
              variants={rise}
              initial="hidden"
              animate="show"
              className="mono"
              style={{ marginTop: 34, fontSize: 11.5, color: "#4E7C93", letterSpacing: "0.1em" }}
            >
              Detect → Trace → Correlate → Rank
            </motion.div>
          </div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.6, duration: 1 }}
            style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 9, paddingBottom: 28 }}
          >
            <span className="label" style={{ fontSize: 9.5 }}>Scroll to investigate</span>
            <div style={{ width: 1, height: 28, background: "linear-gradient(180deg, #35C9F5, transparent)", animation: "bob 2.4s ease-in-out infinite" }} />
          </motion.div>
        </div>
      </section>

      <TechnologySection onStart={onStart} />
    </div>
  );
}

/* A single scroll section explaining the pipeline shape, so "Explore the
   technology" leads somewhere real instead of jumping into the case. */
function TechnologySection({ onStart }) {
  const phases = [
    { n: "01–04", t: "Detect", d: "A Sentinel-1 SAR scene is calibrated, de-speckled and land-masked, then read by U-Net, DeepLabV3+ and TransUNet. An orchestrator reconciles the three masks into one decision." },
    { n: "05–07", t: "Understand", d: "The slick is measured — area, shape, estimated age. Wind, current and wave data then drive a particle model backwards to a source zone and forwards to a predicted path." },
    { n: "08–12", t: "Attribute", d: "Source type is inferred, AIS traffic is filtered by space and time, an RNN checks whether each candidate's movement fits, and the evidence is fused into a ranked list." },
    { n: "13–15", t: "Deliver", d: "Findings become an explainable record: candidate scores, source zone, time window and confidence — served over an API and exportable as a report." },
  ];

  return (
    <section id="technology" style={{ padding: "clamp(60px, 9vw, 120px) clamp(20px, 6vw, 96px)", borderTop: "1px solid #0F3040" }}>
      <div className="label" style={{ color: COLORS.cyan, marginBottom: 16 }}>From space to accountability</div>
      <h2 style={{ fontSize: "clamp(26px, 4vw, 40px)", maxWidth: 680, lineHeight: 1.2 }}>
        Fifteen stages between a satellite pass and a name on a shortlist.
      </h2>
      <p className="lede" style={{ marginTop: 18 }}>
        Each stage narrows the question and records why. Nothing is asserted that the evidence does not support —
        the output is a ranked set of candidates with the reasoning attached, not a verdict.
      </p>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(230px, 1fr))",
          gap: 0,
          marginTop: 58,
          borderTop: "1px solid #0F3040",
        }}
      >
        {phases.map((p) => (
          <div key={p.t} style={{ padding: "26px 26px 26px 0", borderRight: "1px solid #0F3040" }}>
            <div className="mono" style={{ fontSize: 11, color: COLORS.cyan, letterSpacing: "0.1em", marginBottom: 12 }}>{p.n}</div>
            <div style={{ fontSize: 19, marginBottom: 12 }}>{p.t}</div>
            <p className="note" style={{ margin: 0 }}>{p.d}</p>
          </div>
        ))}
      </div>

      <div style={{ marginTop: 56 }}>
        <button className="btn btn-primary" onClick={onStart}>
          Open case 2026-0417 <ArrowRight size={15} />
        </button>
      </div>

      <div
        className="label"
        style={{ marginTop: 70, paddingTop: 22, borderTop: "1px solid #0F3040", fontSize: 10, display: "flex", gap: 22, flexWrap: "wrap" }}
      >
        <span>Cleaner oceans</span>
        <span>Safer ecosystems</span>
        <span>Data-driven enforcement</span>
      </div>
    </section>
  );
}
