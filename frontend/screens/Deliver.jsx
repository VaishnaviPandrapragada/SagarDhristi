import React, {
  useState,
} from "react";

import {
  FileText,
  Download,
  RotateCcw,
  Check,
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
} from "../components/ui.jsx";

import {
  COLORS,
  CASE,
  RESULT,
  VESSELS,
  SPILL,
  DRIFT,
  ORCHESTRATOR,
} from "../data/mock.js";


/* ==========================================================================
   HELPERS
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


function getScore(candidate) {
  return (
    candidate?.evidence_score ??
    candidate?.attribution_score ??
    candidate?.score ??
    null
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
   STAGE 13 — INVESTIGATION RESULT
   ========================================================================== */

export function ResultStage({
  go,
  analysis,
}) {
  const candidates =
    getCandidates(analysis);

  const top =
    candidates[0] || null;

  const topScore =
    getScore(top);


  const chain = [
    "SAR scene",
    "Preprocessing",
    "Three vision models",
    "Orchestrated detection",
    "Spill geometry",
    "Ocean forcing",
    "Drift hindcast",
    "Source type",
    "Space-time filter",
    "Trajectory analysis",
    "Evidence fusion",
    "Ranking",
  ];


  return (
    <div className="split">

      <div>

        <StageHead
          step="13"
          question="A clear, explainable output"
          title="Investigation result"
          lede="The result combines the reconstructed source zone, source window and ranked AIS candidates into one investigation record."
        />


        <Bracket live>

          <div
            style={{
              padding:
                "28px 26px",
            }}
          >

            <div
              style={{
                display: "flex",
                justifyContent:
                  "space-between",
                gap: 20,
                flexWrap: "wrap",
                alignItems:
                  "flex-start",
              }}
            >

              <div>

                <div
                  className="label"
                  style={{
                    marginBottom: 10,
                  }}
                >
                  Top AIS candidate
                </div>


                <div
                  className="mono"
                  style={{
                    fontSize: 27,
                    color: COLORS.cyan,
                  }}
                >
                  {top
                    ? getVesselId(top)
                    : "No candidate"}
                </div>


                <div
                  className="mono"
                  style={{
                    fontSize: 12,
                    color: "#5C879C",
                    marginTop: 7,
                  }}
                >
                  Vessel ID / MMSI
                </div>

              </div>


              <div
                style={{
                  textAlign: "right",
                }}
              >

                <div
                  className="label"
                  style={{
                    marginBottom: 8,
                  }}
                >
                  Evidence score
                </div>


                <div
                  className="mono"
                  style={{
                    fontSize: 44,
                    lineHeight: 1,
                    color:
                      COLORS.cyan,
                  }}
                >
                  {formatScore(
                    topScore
                  )}
                </div>

              </div>

            </div>


            <div
              style={{
                marginTop: 24,
              }}
            >

              <Bar
                value={
                  topScore ?? 0
                }
                color={COLORS.cyan}
                height={6}
              />

            </div>


            <div
              style={{
                display: "grid",
                gridTemplateColumns:
                  "repeat(auto-fit, minmax(160px, 1fr))",
                gap: 24,
                marginTop: 30,
              }}
            >

              <Reading
                label="Distance to source"
                value={
                  top
                    ? formatDistance(
                        getDistance(top)
                      )
                    : "—"
                }
                size={17}
              />


              <Reading
                label="Time offset"
                value={
                  top
                    ? formatTime(
                        getTimeDifference(
                          top
                        )
                      )
                    : "—"
                }
                size={17}
              />


              <Reading
                label="Evidence rank"
                value={
                  top?.evidence_rank ??
                  top?.rank ??
                  "—"
                }
                size={17}
                color={
                  COLORS.cyan
                }
              />

            </div>


            <div
              style={{
                marginTop: 26,
                display: "flex",
                gap: 10,
                flexWrap: "wrap",
              }}
            >

              <Pill tone="warning">
                Investigation candidate
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


        <p
          style={{
            fontSize: 15.5,
            color: "#A8CBDC",
            lineHeight: 1.75,
            marginTop: 30,
            maxWidth: 620,
          }}
        >
          The highest-ranked AIS candidate has
          the strongest combined evidence in this
          investigation. The score is an evidence
          index, not a probability of responsibility.
        </p>


        <div
          style={{
            marginTop: 34,
          }}
        >

          <div
            className="label"
            style={{
              marginBottom: 16,
            }}
          >
            Reasoning chain
          </div>


          <div
            style={{
              display: "flex",
              flexWrap: "wrap",
              gap: 6,
            }}
          >

            {chain.map(
              (item, index) => (

                <span
                  key={item}
                  className="chip"
                  style={{
                    fontSize: 11.5,
                    padding:
                      "7px 11px",
                  }}
                >

                  <span
                    className="mono"
                    style={{
                      color: "#3F6B80",
                      marginRight: 7,
                    }}
                  >
                    {String(
                      index + 1
                    ).padStart(
                      2,
                      "0"
                    )}
                  </span>

                  {item}

                </span>

              )
            )}

          </div>

        </div>


        <StageNav
          onBack={() =>
            go("ranking")
          }
          onNext={() =>
            go("report")
          }
          nextLabel="Build the report"
        />

      </div>


      <aside>

        <div
          className="label"
          style={{
            marginBottom: 20,
          }}
        >
          Ranked candidates
        </div>


        {candidates
          .slice(0, 5)
          .map(
            (candidate, index) => {

              const rank =
                candidate.evidence_rank ??
                candidate.rank ??
                index + 1;

              const score =
                getScore(candidate);

              return (
                <div
                  key={
                    candidate.vessel_id ||
                    `${rank}-${index}`
                  }
                  style={{
                    paddingBottom:
                      16,
                    marginBottom:
                      16,
                    borderBottom:
                      "1px solid #0F2938",
                  }}
                >

                  <div
                    style={{
                      display: "flex",
                      justifyContent:
                        "space-between",
                      gap: 10,
                      marginBottom: 8,
                    }}
                  >

                    <span
                      className="mono"
                      style={{
                        fontSize: 13.5,
                        color:
                          Number(rank) === 1
                            ? COLORS.critical
                            : "#D5EBF5",
                      }}
                    >
                      #{rank}{" "}
                      {getVesselId(
                        candidate
                      )}
                    </span>


                    <span
                      className="mono"
                      style={{
                        fontSize: 14,
                        color:
                          COLORS.cyan,
                      }}
                    >
                      {formatScore(
                        score
                      )}
                    </span>

                  </div>


                  <Bar
                    value={
                      score ?? 0
                    }
                    color={
                      Number(rank) === 1
                        ? COLORS.critical
                        : COLORS.cyan
                    }
                    height={3}
                  />

                </div>
              );
            }
          )}


        <div
          style={{
            marginTop: 26,
          }}
        >

          <Caveat>
            The shortlist supports investigation.
            It does not establish responsibility.
          </Caveat>

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
   STAGE 14 — REPORT & EXPORT
   ========================================================================== */

export function ReportStage({
  go,
  onRestart,
  analysis,
}) {
  const [
    generated,
    setGenerated,
  ] = useState(false);


  const candidates =
    getCandidates(analysis);

  const top =
    candidates[0] || null;

  const score =
    getScore(top);


  const rows = [
    [
      "Case",
      CASE.id,
    ],

    [
      "Scene",
      "Sentinel-1 SAR investigation",
    ],

    [
      "Detection",
      `Spill detected · confidence ${ORCHESTRATOR.confidence.toFixed(2)}`,
    ],

    [
      "Models",
      "U-Net · DeepLabV3+ · TransUNet",
    ],

    [
      "Spill",
      `${SPILL.area} km² · ${SPILL.shape} · age ${SPILL.age}`,
    ],

    [
      "Ocean forcing",
      "Wind and current fields",
    ],

    [
      "Source zone",
      DRIFT.originZone,
    ],

    [
      "Source window",
      DRIFT.originWindow,
    ],

    [
      "Top candidate",
      top
        ? `Vessel ID ${getVesselId(top)}`
        : "No AIS candidate",
    ],

    [
      "Distance to source",
      top
        ? formatDistance(
            getDistance(top)
          )
        : "—",
    ],

    [
      "Evidence score",
      formatScore(score),
    ],

    [
      "Status",
      "Investigation candidate — not confirmed attribution",
    ],
  ];


  return (
    <div>

      <StageHead
        step="14"
        question="Handing it over"
        title="One record an investigator can act on"
        lede="The report collects the investigation output, evidence and caveats into a single record."
      />


      <div
        style={{
          display: "grid",
          gridTemplateColumns:
            "repeat(auto-fit, minmax(300px, 1fr))",
          gap: 44,
          alignItems: "start",
        }}
      >

        <Bracket>

          <div>

            {rows.map(
              ([key, value], index) => (

                <div
                  key={key}
                  style={{
                    display: "flex",
                    justifyContent:
                      "space-between",
                    gap: 24,
                    padding:
                      "14px 22px",
                    borderBottom:
                      index <
                      rows.length - 1
                        ? "1px solid #0F2938"
                        : "none",
                    flexWrap: "wrap",
                  }}
                >

                  <span
                    className="label"
                    style={{
                      fontSize: 10.5,
                    }}
                  >
                    {key}
                  </span>


                  <span
                    className="mono"
                    style={{
                      fontSize: 12.5,
                      color: "#D5EBF5",
                      textAlign:
                        "right",
                    }}
                  >
                    {value}
                  </span>

                </div>

              )
            )}

          </div>

        </Bracket>


        <div>

          <div
            className="metrics"
            style={{
              gridTemplateColumns:
                "1fr 1fr",
            }}
          >

            <div>

              <Reading
                label="Spill area"
                value={SPILL.area}
                unit="km²"
                size={24}
              />

            </div>


            <div>

              <Reading
                label="Detection confidence"
                value={
                  ORCHESTRATOR.confidence.toFixed(
                    2
                  )
                }
                size={24}
                color={
                  COLORS.cyan
                }
              />

            </div>


            <div>

              <Reading
                label="Vessels screened"
                value={
                  analysis?.ais_candidates
                    ?.length ??
                  CASE.vesselsScreened
                }
                size={24}
              />

            </div>


            <div>

              <Reading
                label="Evidence score"
                value={
                  formatScore(score)
                }
                size={24}
                color={
                  COLORS.cyan
                }
              />

            </div>

          </div>


          <div
            style={{
              marginTop: 30,
              display: "flex",
              gap: 12,
              flexWrap: "wrap",
            }}
          >

            <button
              className="btn btn-primary"
              onClick={() =>
                setGenerated(true)
              }
            >

              {generated ? (
                <>
                  <Check
                    size={15}
                  />
                  Report generated
                </>
              ) : (
                <>
                  <FileText
                    size={15}
                  />
                  Generate report
                </>
              )}

            </button>


            <button
              className="btn btn-ghost"
            >
              <Download
                size={15}
              />
              Export evidence
            </button>

          </div>


          {generated && (

            <div
              className="enter"
              style={{
                marginTop: 20,
              }}
            >

              <div
                style={{
                  display: "flex",
                  justifyContent:
                    "space-between",
                  padding:
                    "14px 18px",
                  border:
                    "1px solid #1B4A60",
                  flexWrap: "wrap",
                  gap: 10,
                }}
              >

                <span
                  className="mono"
                  style={{
                    fontSize: 12.5,
                  }}
                >
                  sagardhristi-report.pdf
                </span>


                <span
                  className="mono"
                  style={{
                    fontSize: 11.5,
                    color: "#4E7C93",
                  }}
                >
                  Investigation report
                </span>

              </div>

            </div>

          )}


          <div
            style={{
              marginTop: 30,
            }}
          >

            <Caveat tone="warning">
              The report describes evidence and
              uncertainty. It does not assert that
              any vessel caused a discharge.
            </Caveat>

          </div>


          <div
            style={{
              marginTop: 34,
              paddingTop: 22,
              borderTop:
                "1px solid #0F3040",
            }}
          >

            <button
              className="btn btn-ghost"
              onClick={
                onRestart ||
                (() => go("sar"))
              }
            >
              <RotateCcw
                size={15}
              />
              Start new investigation
            </button>

          </div>


          <div
            style={{
              marginTop: 26,
            }}
          >
            <SimTag />
          </div>

        </div>

      </div>


      <div
        style={{
          marginTop: 56,
          paddingTop: 22,
          borderTop:
            "1px solid #0F3040",
          display: "flex",
          gap: 24,
          flexWrap: "wrap",
        }}
      >

        <span
          className="label"
          style={{
            fontSize: 10,
          }}
        >
          Cleaner oceans
        </span>

        <span
          className="label"
          style={{
            fontSize: 10,
          }}
        >
          Safer ecosystems
        </span>

        <span
          className="label"
          style={{
            fontSize: 10,
          }}
        >
          Data-driven investigation
        </span>

      </div>

    </div>
  );
}