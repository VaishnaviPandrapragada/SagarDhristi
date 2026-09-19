import React, { useState } from "react";

import {
  Ship,
  Factory,
  HelpCircle,
} from "lucide-react";

import {
  Bracket,
  Reading,
  Pill,
  Bar,
  StageHead,
  StageNav,
  Caveat,
  SimTag,
  SarTexture,
} from "../components/ui.jsx";

import {
  COLORS,
  SOURCE_TYPES,
  FILTER_FUNNEL,
  VESSELS,
  EVIDENCE_FACTORS,
} from "../data/mock.js";


/* ==========================================================================
   REAL BACKEND DATA HELPERS
   ========================================================================== */

function getCandidates(analysis) {
  if (
    Array.isArray(analysis?.ranked_candidates)
  ) {
    return analysis.ranked_candidates;
  }

  if (
    Array.isArray(analysis?.ais_candidates)
  ) {
    return analysis.ais_candidates;
  }

  return [];
}


function getVesselId(candidate) {
  return (
    candidate?.vessel_id ??
    candidate?.mmsi ??
    "—"
  );
}


function getDistance(candidate) {
  return (
    candidate?.distance_to_source_km ??
    candidate?.distance_to_spill_km ??
    null
  );
}


function getTimeDifference(candidate) {
  return (
    candidate?.time_difference_hours ??
    candidate?.time_diff_hours ??
    null
  );
}


function getSpatial(candidate) {
  return (
    candidate?.evidence?.spatial_score ??
    candidate?.spatial_score ??
    null
  );
}


function getTemporal(candidate) {
  return (
    candidate?.evidence?.temporal_score ??
    candidate?.temporal_score ??
    null
  );
}


function getProximity(candidate) {
  return (
    candidate?.evidence?.proximity_score ??
    candidate?.proximity_score ??
    null
  );
}


function getTrajectory(candidate) {
  return (
    candidate?.evidence?.trajectory_score ??
    candidate?.trajectory_score ??
    null
  );
}


function getBehaviour(candidate) {
  return (
    candidate?.behaviour_score ??
    candidate?.behavior_score ??
    null
  );
}


function getScore(candidate) {
  return (
    candidate?.evidence_score ??
    candidate?.attribution_score ??
    candidate?.score ??
    null
  );
}


function getRank(candidate, index) {
  return (
    candidate?.evidence_rank ??
    candidate?.rank ??
    index + 1
  );
}


function formatScore(value) {
  if (
    value === null ||
    value === undefined ||
    Number.isNaN(Number(value))
  ) {
    return "—";
  }

  return Number(value).toFixed(2);
}


function formatDistance(value) {
  if (
    value === null ||
    value === undefined ||
    Number.isNaN(Number(value))
  ) {
    return "—";
  }

  return `${Number(value).toFixed(2)} km`;
}


function formatTime(value) {
  if (
    value === null ||
    value === undefined ||
    Number.isNaN(Number(value))
  ) {
    return "—";
  }

  const minutes = Math.round(
    Number(value) * 60
  );

  return `${
    minutes >= 0 ? "+" : ""
  }${minutes} min`;
}


/* ==========================================================================
   STAGE 08 — SOURCE TYPE
   ========================================================================== */

const ICONS = {
  vessel: Ship,
  fixed: Factory,
  unknown: HelpCircle,
};


export function SourceTypeStage({
  go,
}) {
  const top = SOURCE_TYPES[0];

  return (
    <div>

      <StageHead
        step="08"
        question="What kind of source"
        title="Vessel attribution only runs if a vessel is plausible"
        lede="Slick shape, position and surrounding context are weighed against three possibilities."
      />

      <div
        style={{
          display: "grid",
          gridTemplateColumns:
            "repeat(auto-fit, minmax(230px, 1fr))",
          gap: 26,
        }}
      >

        {SOURCE_TYPES.map((source) => {

          const Icon =
            ICONS[source.key];

          const lead =
            source.key === top.key;

          return (
            <Bracket
              key={source.key}
              live={lead}
            >

              <div
                style={{
                  padding: 24,
                  background: lead
                    ? "rgba(53,201,245,0.04)"
                    : "transparent",
                }}
              >

                <Icon
                  size={20}
                  color={
                    lead
                      ? COLORS.cyan
                      : "#3F6B80"
                  }
                  strokeWidth={1.5}
                />

                <div
                  style={{
                    fontSize: 19,
                    marginTop: 18,
                  }}
                >
                  {source.name}
                </div>

                <div
                  className="note"
                  style={{
                    marginBottom: 22,
                  }}
                >
                  {source.desc}
                </div>

                <div
                  style={{
                    display: "flex",
                    justifyContent:
                      "space-between",
                    alignItems:
                      "baseline",
                    marginBottom: 8,
                  }}
                >

                  <span className="label">
                    Likelihood
                  </span>

                  <span
                    className="mono"
                    style={{
                      fontSize: 19,
                      color: lead
                        ? COLORS.cyan
                        : "#7FAEC7",
                    }}
                  >
                    {source.score.toFixed(2)}
                  </span>

                </div>

                <Bar
                  value={source.score}
                  color={
                    lead
                      ? COLORS.cyan
                      : "#2C5A70"
                  }
                />

                <p
                  className="note"
                  style={{
                    marginTop: 16,
                  }}
                >
                  {source.evidence}
                </p>

              </div>

            </Bracket>
          );
        })}

      </div>

      <div
        style={{
          marginTop: 34,
          maxWidth: 640,
        }}
      >

        <Caveat>
          Vessel source is the leading hypothesis.
          That opens the AIS search — it does not
          implicate any particular ship.
        </Caveat>

      </div>

      <div
        style={{
          marginTop: 20,
        }}
      >
        <SimTag />
      </div>

      <StageNav
        onBack={() => go("drift")}
        onNext={() => go("spacetime")}
        nextLabel="Filter AIS traffic"
      />

    </div>
  );
}


/* ==========================================================================
   STAGE 09 — SPACE-TIME FILTER
   ========================================================================== */

export function SpaceTimeStage({
  go,
}) {
  const [step, setStep] =
    useState(
      FILTER_FUNNEL.length - 1
    );

  const visible =
    VESSELS.filter(
      (v, index) =>
        step >= 4
          ? index < 3
          : step >= 3
            ? index < 5
            : step >= 2
              ? index < 7
              : true
    );

  return (
    <div className="split">

      <div>

        <StageHead
          step="09"
          question="Finding candidates"
          title="Who was inside the source zone, during the source window"
          lede="AIS position reports are filtered on two axes at once: space against the hindcast zone and time against the estimated release window."
        />

        <Bracket>

          <div
            style={{
              position: "relative",
              aspectRatio: "16 / 10",
              background: "#051722",
            }}
          >

            <svg
              width="100%"
              height="100%"
              viewBox="0 0 100 62.5"
              preserveAspectRatio="xMidYMid slice"
            >

              <defs>

                <SarTexture
                  id="ais"
                  frequency={0.26}
                  seed={11}
                  tint="#0A2A3A"
                />

              </defs>

              <rect
                width="100"
                height="62.5"
                fill="#07202D"
              />

              <rect
                width="100"
                height="62.5"
                filter="url(#ais)"
                opacity="0.5"
              />

              {Array.from({
                length: 6,
              }).map((_, index) => (
                <line
                  key={`h${index}`}
                  x1="0"
                  y1={index * 12.5}
                  x2="100"
                  y2={index * 12.5}
                  stroke="#0F2938"
                  strokeWidth="0.15"
                />
              ))}

              {Array.from({
                length: 7,
              }).map((_, index) => (
                <line
                  key={`v${index}`}
                  x1={index * 16.6}
                  y1="0"
                  x2={index * 16.6}
                  y2="62.5"
                  stroke="#0F2938"
                  strokeWidth="0.15"
                />
              ))}

              <ellipse
                cx="58"
                cy="44"
                rx="13"
                ry="10"
                fill={COLORS.oil}
                opacity="0.1"
                stroke={COLORS.oil}
                strokeWidth="0.3"
                strokeDasharray="1.2 1"
              />

              <circle
                cx="58"
                cy="44"
                r="1.1"
                fill={COLORS.oil}
              />

              <text
                x="60.5"
                y="42"
                className="mono"
                fontSize="2.3"
                fill={COLORS.oil}
              >
                SOURCE ZONE
              </text>

              {visible.map((v) => {

                const isCandidate =
                  v.tier === "candidate";

                const isTop =
                  v.rank === 1;

                const color =
                  isTop
                    ? COLORS.critical
                    : isCandidate
                      ? COLORS.warning
                      : COLORS.cyan;

                const points =
                  v.track
                    .map(
                      (p) =>
                        `${p[0]},${p[1] * 0.625}`
                    )
                    .join(" ");

                const [cx, cy] =
                  v.track[4];

                return (
                  <g key={v.mmsi}>

                    <polyline
                      points={points}
                      fill="none"
                      stroke={color}
                      strokeWidth="0.25"
                      opacity="0.45"
                      strokeDasharray="1 0.8"
                    />

                    <circle
                      cx={cx}
                      cy={cy * 0.625}
                      r={
                        isTop
                          ? 1.5
                          : 1.1
                      }
                      fill={color}
                    />

                    {isCandidate && (
                      <text
                        x={cx + 2}
                        y={
                          cy * 0.625 + 1
                        }
                        className="mono"
                        fontSize="2"
                        fill={color}
                      >
                        {v.mmsi}
                      </text>
                    )}

                  </g>
                );
              })}

            </svg>

          </div>

        </Bracket>

        <StageNav
          onBack={() =>
            go("sourcetype")
          }
          onNext={() =>
            go("trajectory")
          }
          nextLabel="Analyse trajectories"
        />

      </div>


      <aside>

        <div
          className="label"
          style={{
            marginBottom: 20,
          }}
        >
          Filter funnel
        </div>

        {FILTER_FUNNEL.map(
          (funnel, index) => {

            const active =
              index <= step;

            return (
              <button
                key={funnel.label}
                onClick={() =>
                  setStep(index)
                }
                style={{
                  display: "block",
                  width: "100%",
                  textAlign: "left",
                  background: "none",
                  cursor: "pointer",
                  border: "none",
                  borderLeft:
                    `2px solid ${
                      active
                        ? COLORS.cyan
                        : "#153545"
                    }`,
                  padding:
                    "0 0 0 16px",
                  marginBottom: 20,
                }}
              >

                <div
                  style={{
                    display: "flex",
                    justifyContent:
                      "space-between",
                    alignItems:
                      "baseline",
                    gap: 12,
                  }}
                >

                  <span
                    style={{
                      fontSize: 13.5,
                      color: active
                        ? COLORS.white
                        : "#4E7C93",
                    }}
                  >
                    {funnel.label}
                  </span>

                  <span
                    className="mono"
                    style={{
                      fontSize: 17,
                      color: active
                        ? COLORS.cyan
                        : "#3F6B80",
                    }}
                  >
                    {funnel.count}
                  </span>

                </div>

                <div
                  className="note"
                  style={{
                    marginTop: 5,
                  }}
                >
                  {funnel.note}
                </div>

              </button>
            );
          }
        )}

        <div
          className="hairline"
          style={{
            margin:
              "8px 0 22px",
          }}
        />

        <div
          style={{
            display: "grid",
            gridTemplateColumns:
              "1fr 1fr",
            gap: 18,
          }}
        >

          <Reading
            label="Search radius"
            value="12"
            unit="NM"
            size={17}
          />

          <Reading
            label="Time window"
            value="±3"
            unit="hrs"
            size={17}
          />

        </div>

        <div
          style={{
            marginTop: 22,
          }}
        >
          <SimTag />
        </div>

      </aside>

    </div>
  );
}


/* ==========================================================================
   STAGE 10 — REAL AIS TRAJECTORY EVIDENCE
   ========================================================================== */

export function TrajectoryStage({
  go,
  analysis,
}) {
  const candidates =
    getCandidates(analysis);

  const top =
    candidates[0] || null;

  return (
    <div className="split">

      <div>

        <StageHead
          step="10"
          question="How each vessel moved"
          title="Recorded AIS movement"
          lede="Historical AIS movement is used as supporting evidence for candidate ranking."
        />

        <Bracket>

          <div
            style={{
              padding: "30px 26px",
            }}
          >

            {!top ? (

              <div
                style={{
                  padding: 30,
                  textAlign: "center",
                  color: "#4E7C93",
                }}
              >
                No AIS trajectory evidence
                returned for this investigation.
              </div>

            ) : (

              <>

                <div
                  className="label"
                  style={{
                    marginBottom: 18,
                  }}
                >
                  TOP AIS CANDIDATE
                </div>

                <div
                  style={{
                    fontSize: 25,
                    marginBottom: 6,
                  }}
                >
                  Vessel ID{" "}
                  {getVesselId(top)}
                </div>

                <div
                  className="mono"
                  style={{
                    fontSize: 12,
                    color: "#5C879C",
                    marginBottom: 28,
                  }}
                >
                  Recorded AIS position
                </div>

                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns:
                      "repeat(auto-fit, minmax(150px, 1fr))",
                    gap: 26,
                  }}
                >

                  <Reading
                    label="Distance"
                    value={formatDistance(
                      getDistance(top)
                    )}
                    size={17}
                  />

                  <Reading
                    label="Time offset"
                    value={formatTime(
                      getTimeDifference(top)
                    )}
                    size={17}
                  />

                  <Reading
                    label="Trajectory"
                    value={formatScore(
                      getTrajectory(top)
                    )}
                    size={17}
                    color={COLORS.cyan}
                  />

                  <Reading
                    label="Evidence"
                    value={formatScore(
                      getScore(top)
                    )}
                    size={17}
                    color={COLORS.cyan}
                  />

                </div>

              </>

            )}

          </div>

        </Bracket>

        <div
          style={{
            marginTop: 22,
          }}
        >

          <Caveat>
            Only evidence returned by the AIS
            investigation is displayed. No synthetic
            trajectory is drawn.
          </Caveat>

        </div>

        <StageNav
          onBack={() =>
            go("spacetime")
          }
          onNext={() =>
            go("fusion")
          }
          nextLabel="Fuse the evidence"
        />

      </div>


      <aside>

        <div
          className="label"
          style={{
            marginBottom: 20,
          }}
        >
          AIS candidates
        </div>

        <Reading
          label="Candidates returned"
          value={candidates.length}
          size={34}
          color={COLORS.cyan}
        />

        {top && (
          <>
            <div
              className="hairline"
              style={{
                margin:
                  "26px 0",
              }}
            />

            <Reading
              label="Evidence rank"
              value={getRank(
                top,
                0
              )}
              size={28}
              color={COLORS.cyan}
            />
          </>
        )}

      </aside>

    </div>
  );
}


/* ==========================================================================
   STAGE 11 — EVIDENCE FUSION
   ========================================================================== */

export function FusionStage({
  go,
}) {
  const candidates =
    VESSELS.filter(
      (v) =>
        v.tier === "candidate"
    );

  const [selected, setSelected] =
    useState(
      candidates[0]?.mmsi
    );

  const vessel =
    candidates.find(
      (v) =>
        v.mmsi === selected
    ) ||
    candidates[0];

  return (
    <div>

      <StageHead
        step="11"
        question="Putting the pieces together"
        title="Evidence fusion"
        lede="Spatial, temporal, proximity, trajectory and behavioural signals are combined into an investigation score."
      />

      <div
        style={{
          display: "flex",
          gap: 8,
          marginBottom: 32,
          flexWrap: "wrap",
        }}
      >

        {candidates.map(
          (candidate) => (

            <button
              key={candidate.mmsi}
              onClick={() =>
                setSelected(
                  candidate.mmsi
                )
              }
              className="chip"
              style={{
                cursor: "pointer",
                borderColor:
                  selected ===
                  candidate.mmsi
                    ? "#2C7A9E"
                    : "#163B4E",
                color:
                  selected ===
                  candidate.mmsi
                    ? COLORS.cyan
                    : "#9AC4DA",
                background:
                  selected ===
                  candidate.mmsi
                    ? "rgba(53,201,245,0.06)"
                    : "#061826",
              }}
            >
              {candidate.name} ·{" "}
              {candidate.score.toFixed(2)}
            </button>

          )
        )}

      </div>


      <div
        style={{
          display: "grid",
          gridTemplateColumns:
            "repeat(auto-fit, minmax(280px, 1fr))",
          gap: 44,
          alignItems: "start",
        }}
      >

        <div>

          {EVIDENCE_FACTORS.map(
            (factor, index) => (

              <div
                key={factor.key}
                style={{
                  marginBottom: 26,
                }}
              >

                <div
                  style={{
                    display: "flex",
                    justifyContent:
                      "space-between",
                    alignItems:
                      "baseline",
                    gap: 12,
                    marginBottom: 7,
                  }}
                >

                  <span
                    style={{
                      fontSize: 14,
                    }}
                  >
                    {factor.label}
                  </span>

                  <span
                    className="mono"
                    style={{
                      fontSize: 15,
                      color: COLORS.cyan,
                    }}
                  >
                    {vessel?.[factor.key] != null
                      ? vessel[
                          factor.key
                        ].toFixed(2)
                      : "—"}
                  </span>

                </div>

                <Bar
                  value={
                    vessel?.[factor.key] ??
                    0
                  }
                  color={COLORS.cyan}
                  delay={
                    index * 0.07
                  }
                />

                <div
                  className="note"
                  style={{
                    marginTop: 7,
                  }}
                >
                  {factor.question}
                </div>

              </div>
            )
          )}

        </div>


        <Bracket live>

          <div
            style={{
              padding:
                "30px 26px",
            }}
          >

            <div
              className="label"
              style={{
                marginBottom: 14,
              }}
            >
              Combined evidence score
            </div>

            <div
              className="mono"
              style={{
                fontSize: 56,
                lineHeight: 1,
                color: COLORS.cyan,
              }}
            >
              {vessel?.score != null
                ? vessel.score.toFixed(2)
                : "—"}
            </div>

            <div
              style={{
                marginTop: 20,
              }}
            >
              <Bar
                value={
                  vessel?.score ?? 0
                }
                color={COLORS.cyan}
                height={7}
              />
            </div>

            <div
              style={{
                marginTop: 22,
                display: "flex",
                gap: 10,
                flexWrap: "wrap",
              }}
            >

              <Pill tone="neutral">
                Evidence score
              </Pill>

              <Pill
                tone="neutral"
                dot={false}
              >
                Not confirmed attribution
              </Pill>

            </div>

          </div>

        </Bracket>

      </div>


      <div
        style={{
          marginTop: 26,
        }}
      >

        <Caveat>
          A high evidence score supports further
          investigation. It is not proof of discharge
          or responsibility.
        </Caveat>

      </div>


      <StageNav
        onBack={() =>
          go("trajectory")
        }
        onNext={() =>
          go("ranking")
        }
        nextLabel="Rank candidates"
      />

    </div>
  );
}


/* ==========================================================================
   STAGE 12 — REAL VESSEL RANKING
   ========================================================================== */

export function RankingStage({
  go,
  analysis,
}) {
  const candidates =
    getCandidates(analysis);

  /*
   * IMPORTANT:
   * Backend already returns evidence_rank.
   * Rank 1 must appear first.
   */
  const rows =
    [...candidates].sort(
      (a, b) =>
        Number(
          a.evidence_rank ??
          a.rank ??
          999999
        ) -
        Number(
          b.evidence_rank ??
          b.rank ??
          999999
        )
    );

  return (
    <div>

      <StageHead
        step="12"
        question="Candidate vessels"
        title="Vessel ranking"
        lede="AIS candidates are ordered using the evidence returned by the investigation pipeline."
      />

      {!analysis ||
      rows.length === 0 ? (

        <Bracket>

          <div
            style={{
              padding: 48,
              textAlign: "center",
              color: "#4E7C93",
            }}
          >
            No AIS candidates returned
            for this investigation.
          </div>

        </Bracket>

      ) : (

        <Bracket>

          <div
            style={{
              overflowX: "auto",
            }}
          >

            <table
              className="data"
              style={{
                minWidth: 900,
              }}
            >

              <thead>

                <tr>

                  {[
                    "Rank",
                    "Vessel ID",
                    "Distance",
                    "Time offset",
                    "Spatial",
                    "Temporal",
                    "Proximity",
                    "Trajectory",
                    "Score",
                  ].map(
                    (heading) => (

                      <th
                        key={heading}
                        className="label"
                      >
                        {heading}
                      </th>

                    )
                  )}

                </tr>

              </thead>


              <tbody>

                {rows.map(
                  (candidate, index) => {

                    const rank =
                      getRank(
                        candidate,
                        index
                      );

                    const score =
                      getScore(
                        candidate
                      );

                    const distance =
                      getDistance(
                        candidate
                      );

                    const time =
                      getTimeDifference(
                        candidate
                      );

                    const spatial =
                      getSpatial(
                        candidate
                      );

                    const temporal =
                      getTemporal(
                        candidate
                      );

                    const proximity =
                      getProximity(
                        candidate
                      );

                    const trajectory =
                      getTrajectory(
                        candidate
                      );

                    const isTop =
                      Number(rank) === 1;

                    return (
                      <tr
                        key={
                          candidate.vessel_id ||
                          `${rank}-${index}`
                        }
                        style={{
                          background:
                            isTop
                              ? "rgba(255,91,91,0.05)"
                              : "transparent",
                        }}
                      >

                        <td
                          className="mono"
                          style={{
                            fontSize: 14,
                            color:
                              isTop
                                ? COLORS.critical
                                : "#5C879C",
                          }}
                        >
                          {String(
                            rank
                          ).padStart(
                            2,
                            "0"
                          )}
                        </td>


                        <td>

                          <div
                            className="mono"
                            style={{
                              fontSize: 14,
                              color:
                                isTop
                                  ? COLORS.critical
                                  : "#D5EBF5",
                            }}
                          >
                            {getVesselId(
                              candidate
                            )}
                          </div>

                        </td>


                        <td
                          className="mono"
                          style={{
                            fontSize: 13,
                          }}
                        >
                          {formatDistance(
                            distance
                          )}
                        </td>


                        <td
                          className="mono"
                          style={{
                            fontSize: 13,
                          }}
                        >
                          {formatTime(
                            time
                          )}
                        </td>


                        <td
                          className="mono"
                          style={{
                            fontSize: 13,
                          }}
                        >
                          {formatScore(
                            spatial
                          )}
                        </td>


                        <td
                          className="mono"
                          style={{
                            fontSize: 13,
                          }}
                        >
                          {formatScore(
                            temporal
                          )}
                        </td>


                        <td
                          className="mono"
                          style={{
                            fontSize: 13,
                          }}
                        >
                          {formatScore(
                            proximity
                          )}
                        </td>


                        <td
                          className="mono"
                          style={{
                            fontSize: 13,
                          }}
                        >
                          {formatScore(
                            trajectory
                          )}
                        </td>


                        <td>

                          <span
                            className="mono"
                            style={{
                              fontSize: 17,
                              color:
                                isTop
                                  ? COLORS.critical
                                  : COLORS.cyan,
                            }}
                          >
                            {formatScore(
                              score
                            )}
                          </span>

                        </td>

                      </tr>
                    );
                  }
                )}

              </tbody>

            </table>

          </div>

        </Bracket>

      )}


      <div
        style={{
          marginTop: 28,
          maxWidth: 680,
        }}
      >

        <Caveat tone="warning">
          The ranking is an evidence-based
          investigation shortlist. A high score is
          not proof that a vessel caused the spill.
        </Caveat>

      </div>


      <StageNav
        onBack={() =>
          go("fusion")
        }
        onNext={() =>
          go("result")
        }
        nextLabel="View result"
      />

    </div>
  );
}