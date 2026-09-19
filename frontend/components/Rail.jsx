import React, { useEffect, useState } from "react";
import {
  Waves,
  LayoutGrid,
  Bell,
  X,
  CheckCheck,
  AlertTriangle,
  Info,
  Radio,
} from "lucide-react";

import { STAGES, PHASES, stageIndex } from "../data/pipeline.js";
import { COLORS, CASE, VESSELS } from "../data/mock.js";
import { Pill } from "./ui.jsx";

const ALERT_DASHBOARD_COUNT = VESSELS.filter((v) => v.tier === "candidate").length;

const ALERTS = [
  {
    id: 1,
    type: "critical",
    title: "Oil spill detected",
    message: "2.4 km² slick detected with 95% confidence.",
    meta: "22.4°N · 69.1°E",
    time: "2 min ago",
    stage: "sar",
  },
  {
    id: 2,
    type: "warning",
    title: "Potential source identified",
    message: "MV Kestrel shows strong spatio-temporal correlation.",
    meta: "Attribution score 87/100",
    time: "8 min ago",
    stage: "ranking",
  },
  {
    id: 3,
    type: "info",
    title: "Drift analysis updated",
    message: "Hindcast completed with high confidence.",
    meta: "Origin uncertainty ±1.1 NM",
    time: "15 min ago",
    stage: "drift",
  },
];

const ALERT_ICON = {
  critical: AlertTriangle,
  warning: AlertTriangle,
  info: Info,
};

export default function Rail({ active, go }) {
  const activeIdx = stageIndex(active);
  const [alertsOpen, setAlertsOpen] = useState(false);
  const [readIds, setReadIds] = useState([]);
  const [toastVisible, setToastVisible] = useState(true);

  const unreadCount = ALERTS.filter((a) => !readIds.includes(a.id)).length;

  useEffect(() => {
    const timer = window.setTimeout(() => setToastVisible(false), 6500);
    return () => window.clearTimeout(timer);
  }, []);

  const openAlert = (alert) => {
    setReadIds((ids) => ids.includes(alert.id) ? ids : [...ids, alert.id]);
    setAlertsOpen(false);
    setToastVisible(false);
    go(alert.stage);
  };

  const markAllRead = () => setReadIds(ALERTS.map((a) => a.id));

  return (
    <nav className="rail scroll" aria-label="Investigation pipeline">
      <button
        onClick={() => go("overview")}
        style={{
          display: "flex", alignItems: "center", gap: 11, padding: "0 22px 22px",
          background: "none", border: "none", cursor: "pointer", textAlign: "left", color: "inherit",
        }}
      >
        <Waves size={17} color={COLORS.cyan} />
        <span>
          <span style={{ display: "block", fontSize: 14, letterSpacing: "0.01em" }}>Sagar Dhristi</span>
          <span className="label" style={{ fontSize: 9, display: "block", marginTop: 2 }}>Marine intelligence</span>
        </span>
      </button>

      <div className="rail-alert-wrap">
        <button
          className={`rail-alert-button ${alertsOpen ? "open" : ""}`}
          onClick={() => setAlertsOpen((v) => !v)}
          aria-label={`Open alerts${unreadCount ? `, ${unreadCount} unread` : ""}`}
          aria-expanded={alertsOpen}
        >
          <span className="rail-alert-icon">
            <Bell size={15} />
            {unreadCount > 0 && <span className="alert-badge">{unreadCount}</span>}
          </span>
          <span>
            <span className="rail-alert-label">Investigation alerts</span>
            <span className="rail-alert-sub">Live monitoring</span>
          </span>
          <span className="rail-alert-status" />
        </button>

        {alertsOpen && (
          <div className="alert-panel" role="dialog" aria-label="Investigation alerts">
            <div className="alert-panel-head">
              <div>
                <div className="label">Alert centre</div>
                <div className="alert-panel-title">
                  {unreadCount ? `${unreadCount} unread alert${unreadCount > 1 ? "s" : ""}` : "All alerts read"}
                </div>
              </div>
              <button className="alert-close" onClick={() => setAlertsOpen(false)} aria-label="Close alerts">
                <X size={15} />
              </button>
            </div>

            <div className="alert-list">
              {ALERTS.map((alert) => {
                const Icon = ALERT_ICON[alert.type];
                const isRead = readIds.includes(alert.id);
                return (
                  <button
                    key={alert.id}
                    className={`alert-item ${alert.type} ${isRead ? "read" : ""}`}
                    onClick={() => openAlert(alert)}
                  >
                    <span className="alert-type-icon"><Icon size={15} /></span>
                    <span className="alert-copy">
                      <span className="alert-item-top">
                        <span className="alert-item-title">{alert.title}</span>
                        {!isRead && <span className="alert-unread-dot" />}
                      </span>
                      <span className="alert-message">{alert.message}</span>
                      <span className="alert-meta">{alert.meta} · {alert.time}</span>
                    </span>
                  </button>
                );
              })}
            </div>

            <button className="alert-mark-read" onClick={markAllRead}>
              <CheckCheck size={14} /> Mark all as read
            </button>
          </div>
        )}
      </div>

      {toastVisible && unreadCount > 0 && (
        <button className="alert-toast" onClick={() => openAlert(ALERTS[0])}>
          <span className="alert-toast-icon"><Radio size={15} /></span>
          <span>
            <span className="alert-toast-label">NEW INVESTIGATION ALERT</span>
            <span className="alert-toast-title">Oil spill detected</span>
            <span className="alert-toast-text">95% detection confidence · 2.4 km²</span>
          </span>
          <span
            className="alert-toast-dismiss"
            role="button"
            aria-label="Dismiss notification"
            onClick={(e) => { e.stopPropagation(); setToastVisible(false); }}
          >
            <X size={13} />
          </span>
        </button>
      )}

      <div className="hairline" style={{ margin: "0 22px 14px" }} />

      <div className="rail-scroll" style={{ display: "flex", flexDirection: "column", gap: 2, padding: "0 10px" }}>
        <button className={`rail-item ${active === "overview" ? "active" : ""}`} onClick={() => go("overview")}>
          <span className="rail-num"><LayoutGrid size={12} /></span>
          <span>Case overview</span>
        </button>

        <button
          className={`rail-item ${active === "alerts" ? "active" : ""}`}
          onClick={() => go("alerts")}
          style={{ justifyContent: "space-between" }}
        >
          <span style={{ display: "flex", alignItems: "center", gap: 11 }}>
            <span className="rail-num" style={{ color: COLORS.critical }}>🚨</span>
            <span>Alerts</span>
          </span>
          {ALERT_DASHBOARD_COUNT > 0 && (
            <span
              className="mono"
              style={{
                fontSize: 10,
                padding: "2px 6px",
                background: "rgba(255,91,91,0.14)",
                border: `1px solid ${COLORS.critical}55`,
                color: COLORS.critical,
              }}
            >
              {String(ALERT_DASHBOARD_COUNT).padStart(2, "0")}
            </span>
          )}
        </button>

        {PHASES.map((phase) => (
          <React.Fragment key={phase}>
            <div
              className="rail-group-title label"
              style={{ padding: "18px 14px 7px", fontSize: 9, color: "#2F5C72" }}
            >
              {phase}
            </div>
            {STAGES.filter((s) => s.phase === phase).map((s) => {
              const idx = stageIndex(s.id);
              const isActive = s.id === active;
              const isDone = activeIdx > -1 && idx < activeIdx;
              return (
                <button
                  key={s.id}
                  className={`rail-item ${isActive ? "active" : ""} ${isDone ? "done" : ""}`}
                  onClick={() => go(s.id)}
                  aria-current={isActive ? "step" : undefined}
                >
                  <span className="rail-num">{s.num}</span>
                  <span>{s.label}</span>
                </button>
              );
            })}
          </React.Fragment>
        ))}
      </div>

      <div className="rail-foot" style={{ marginTop: "auto", padding: "22px 22px 0" }}>
        <div className="hairline" style={{ marginBottom: 16 }} />
        <div className="mono" style={{ fontSize: 11, color: "#4E7C93", marginBottom: 12 }}>{CASE.id}</div>
        <Pill tone="cyan">Active</Pill>
      </div>
    </nav>
  );
}
