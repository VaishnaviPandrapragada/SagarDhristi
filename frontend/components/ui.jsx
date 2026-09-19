import React from "react";
import { ChevronRight, ArrowLeft, ArrowRight, Info } from "lucide-react";
import { COLORS } from "../data/mock.js";

/* Viewfinder frame — the one structural device used across the whole app. */
export function Bracket({ children, live = false, style, className = "" }) {
  return (
    <div className={`bracket ${live ? "live" : ""} ${className}`} style={style}>
      {children}
      <span className="bl" />
      <span className="br" />
    </div>
  );
}

/* A single instrument reading. */
export function Reading({ label, value, unit, size = 22, color = COLORS.white, align = "left", sub }) {
  return (
    <div style={{ textAlign: align, minWidth: 0 }}>
      <div className="label" style={{ marginBottom: 7 }}>{label}</div>
      <div className="mono" style={{ fontSize: size, fontWeight: 500, color, lineHeight: 1.15, wordBreak: "break-word" }}>
        {value}
        {unit && <span style={{ fontSize: Math.max(11, size * 0.48), marginLeft: 5, color: "#6FA8C4" }}>{unit}</span>}
      </div>
      {sub && <div className="mono" style={{ fontSize: 11.5, color: "#5C879C", marginTop: 6 }}>{sub}</div>}
    </div>
  );
}

const TONE = {
  cyan: COLORS.cyan,
  baby: COLORS.baby,
  warning: COLORS.warning,
  critical: COLORS.critical,
  oil: COLORS.oil,
  neutral: "#8FB8CC",
};

export function Pill({ tone = "cyan", children, dot = true }) {
  const c = TONE[tone] || TONE.cyan;
  return (
    <span
      className="label"
      style={{
        color: c,
        background: `${c}14`,
        border: `1px solid ${c}55`,
        padding: "6px 12px",
        display: "inline-flex",
        alignItems: "center",
        gap: 7,
        whiteSpace: "nowrap",
      }}
    >
      {dot && (
        <span style={{ width: 5, height: 5, borderRadius: "50%", background: c, animation: "pulseDot 2.4s ease-in-out infinite" }} />
      )}
      {children}
    </span>
  );
}

export function Bar({ value, max = 1, color = COLORS.cyan, height = 5, delay = 0 }) {
  const pct = Math.max(0, Math.min(1, value / max)) * 100;
  return (
    <div style={{ width: "100%", height, background: "#0C2A3A", overflow: "hidden" }}>
      <div
        style={{
          width: `${pct}%`,
          height: "100%",
          background: `linear-gradient(90deg, ${color}77, ${color})`,
          transition: `width 0.9s cubic-bezier(0.16,0.8,0.24,1) ${delay}s`,
        }}
      />
    </div>
  );
}

export function StageHead({ step, title, question, lede }) {
  return (
    <header style={{ marginBottom: 34, maxWidth: 760 }}>
      <div className="label" style={{ color: COLORS.cyan, marginBottom: 12 }}>
        Stage {step}{question ? ` — ${question}` : ""}
      </div>
      <h2 style={{ fontSize: "clamp(24px, 3.2vw, 32px)", lineHeight: 1.15 }}>{title}</h2>
      {lede && <p className="lede" style={{ marginTop: 14, marginBottom: 0 }}>{lede}</p>}
    </header>
  );
}

export function Flow({ items, activeIndex = -1 }) {
  return (
    <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", gap: 2 }}>
      {items.map((it, i) => (
        <React.Fragment key={it}>
          <div className={`chip ${i === activeIndex ? "on" : ""}`}>{it}</div>
          {i < items.length - 1 && <ChevronRight size={14} color="#2C5A70" style={{ margin: "0 3px", flexShrink: 0 }} />}
        </React.Fragment>
      ))}
    </div>
  );
}

export function StageNav({ onBack, onNext, backLabel, nextLabel }) {
  return (
    <div
      style={{
        display: "flex",
        justifyContent: "space-between",
        gap: 14,
        flexWrap: "wrap",
        marginTop: 52,
        paddingTop: 24,
        borderTop: "1px solid #0F3040",
      }}
    >
      {onBack ? (
        <button className="btn btn-ghost" onClick={onBack}>
          <ArrowLeft size={15} /> {backLabel || "Back"}
        </button>
      ) : <span />}
      {onNext && (
        <button className="btn btn-primary" onClick={onNext}>
          {nextLabel || "Continue"} <ArrowRight size={15} />
        </button>
      )}
    </div>
  );
}

export function Caveat({ children, tone = "neutral" }) {
  const c = TONE[tone] || TONE.neutral;
  return (
    <div style={{ display: "flex", gap: 10, padding: "13px 15px", border: `1px solid ${c}33`, background: `${c}0A`, alignItems: "flex-start" }}>
      <Info size={14} color={c} style={{ flexShrink: 0, marginTop: 2 }} />
      <span style={{ fontSize: 12.5, color: "#94BCD0", lineHeight: 1.6 }}>{children}</span>
    </div>
  );
}

/* Simulated-data marker, used once per screen where figures are shown. */
export function SimTag({ children = "Simulated demonstration data" }) {
  return (
    <div className="label" style={{ color: "#3F6B80", display: "flex", alignItems: "center", gap: 7, fontSize: 10 }}>
      <span style={{ width: 12, height: 1, background: "#3F6B80" }} />
      {children}
    </div>
  );
}

/* Procedural SAR-like texture. No external imagery is used anywhere. */
export function SarTexture({ id, frequency = 0.8, seed = 4, tint = "#0B3244" }) {
  return (
    <filter id={id}>
      <feTurbulence type="fractalNoise" baseFrequency={frequency} numOctaves="3" seed={seed} result="n" />
      <feColorMatrix in="n" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.9 0.9 0.9 0 0" result="m" />
      <feComponentTransfer in="m" result="c">
        <feFuncA type="linear" slope="1.7" intercept="-0.3" />
      </feComponentTransfer>
      <feFlood floodColor={tint} result="f" />
      <feComposite in="f" in2="c" operator="in" result="t" />
      <feComposite in="t" in2="SourceGraphic" operator="over" />
    </filter>
  );
}

/* Shared slick outline so the same geometry appears on every screen. */
export const SLICK_PATH =
  "M 118 132 C 146 108, 196 102, 238 116 C 276 128, 296 146, 288 166 C 279 188, 232 196, 186 188 C 142 180, 108 162, 106 148 C 105 140, 110 136, 118 132 Z";
