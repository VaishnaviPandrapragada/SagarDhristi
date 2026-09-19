import React, { useState } from "react";
import {
  CheckCircle2,
  Circle,
  Loader2,
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
  SLICK_PATH,
} from "../components/ui.jsx";

import {
  COLORS,
  SAR,
  PREPROCESS,
  VISION_MODELS,
  ORCHESTRATOR,
  CASE,
} from "../data/mock.js";


const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/analyze";


/* ==========================================================================
   HELPERS
   ========================================================================== */

function formatNumber(value, digits = 2) {
  if (value === null || value === undefined) {
    return "—";
  }

  const number = Number(value);

  if (Number.isNaN(number)) {
    return "—";
  }

  return number.toFixed(digits);
}


/* ==========================================================================
   STAGE 01 — SAR IMAGE
   ========================================================================== */

export function SarStage({
  go,
  analysis,
  setAnalysis,
  uploadedFile,
  setUploadedFile,
  uploadedImage,
}) {
  const [localImage, setLocalImage] = useState(
    uploadedImage || null
  );

  const [localFileName, setLocalFileName] = useState(
    uploadedFile?.name || ""
  );

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");


  const [form, setForm] = useState({
    spill_timestamp: "2022-03-04T06:30:27Z",
    spill_latitude: "13.46321",
    spill_longitude: "144.65858",
    wind_speed_knots: "20",
    wind_direction_deg: "90",
    current_speed_knots: "1.5",
    current_direction_deg: "90",
    lookback_hours: "6",
    forecast_hours: "6",
    time_step_hours: "1",
  });


  const updateField = (key, value) => {
    setForm((previous) => ({
      ...previous,
      [key]: value,
    }));
  };


  const handleUpload = (event) => {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    const previewUrl = URL.createObjectURL(file);

    setLocalFileName(file.name);
    setLocalImage(previewUrl);

    if (setUploadedFile) {
      setUploadedFile(file);
    }

    if (setAnalysis) {
      setAnalysis(null);
    }

    setError("");
  };


  const runAnalysis = async () => {
    const file = uploadedFile;

    if (!file) {
      setError("Please upload a SAR image first.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const formData = new FormData();

      formData.append("file", file);

      Object.entries(form).forEach(
        ([key, value]) => {
          formData.append(key, value);
        }
      );


      const response = await fetch(
        API_URL,
        {
          method: "POST",
          body: formData,
        }
      );


      if (!response.ok) {
        throw new Error(
          `Backend returned HTTP ${response.status}`
        );
      }


      const data = await response.json();


      if (data.status === "error") {
        throw new Error(
          data.error ||
          "Backend analysis failed."
        );
      }


      if (setAnalysis) {
        setAnalysis(data);
      }


      go("preprocess");

    } catch (err) {
      console.error(err);

      setError(
        err.message ||
        "Failed to analyze SAR image."
      );

    } finally {
      setLoading(false);
    }
  };


  return (
    <div className="stage-content">

      <div className="stage-kicker">
        STAGE 01 · DETECTION
      </div>

      <h1>
        SAR Image Acquisition
      </h1>

      <p className="stage-description">
        Upload a Sentinel-1 SAR image to begin oil-spill detection.
        The uploaded image will be used for the demonstration pipeline.
      </p>


      {/* UPLOAD CARD */}

      <div className="upload-card">

        <div className="upload-icon">
          ↑
        </div>

        <h2>
          Upload SAR Image
        </h2>

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


        {localFileName && (
          <div className="file-name">
            ✓ {localFileName}
          </div>
        )}

      </div>


      {/* IMAGE PREVIEW */}

      {localImage && (
        <div className="image-preview-card">

          <div className="preview-header">

            <span>
              UPLOADED SAR IMAGE
            </span>

            <span className="status">
              READY
            </span>

          </div>

          <img
            src={localImage}
            alt="Uploaded SAR"
            className="sar-preview"
          />

        </div>
      )}


      {/* BACKEND ERROR */}

      {error && (
        <div
          style={{
            marginTop: "18px",
            padding: "12px 16px",
            border: "1px solid rgba(255,100,100,0.35)",
            color: "#FF9B9B",
            fontSize: "13px",
          }}
        >
          {error}
        </div>
      )}


      {/* ANALYSIS METADATA */}

      {localImage && (
        <Bracket>
          <div
            style={{
              padding: "22px",
              marginTop: "24px",
            }}
          >

            <div
              className="label"
              style={{
                color: COLORS.cyan,
                marginBottom: "18px",
              }}
            >
              INVESTIGATION PARAMETERS
            </div>


            <div
              style={{
                display: "grid",
                gridTemplateColumns:
                  "repeat(auto-fit, minmax(180px, 1fr))",
                gap: "14px",
              }}
            >

              <label>
                Timestamp

                <input
                  value={form.spill_timestamp}
                  onChange={(e) =>
                    updateField(
                      "spill_timestamp",
                      e.target.value
                    )
                  }
                />

              </label>


              <label>
                Latitude

                <input
                  value={form.spill_latitude}
                  onChange={(e) =>
                    updateField(
                      "spill_latitude",
                      e.target.value
                    )
                  }
                />

              </label>


              <label>
                Longitude

                <input
                  value={form.spill_longitude}
                  onChange={(e) =>
                    updateField(
                      "spill_longitude",
                      e.target.value
                    )
                  }
                />

              </label>


              <label>
                Wind speed

                <input
                  value={form.wind_speed_knots}
                  onChange={(e) =>
                    updateField(
                      "wind_speed_knots",
                      e.target.value
                    )
                  }
                />

              </label>


              <label>
                Wind direction

                <input
                  value={form.wind_direction_deg}
                  onChange={(e) =>
                    updateField(
                      "wind_direction_deg",
                      e.target.value
                    )
                  }
                />

              </label>


              <label>
                Current speed

                <input
                  value={form.current_speed_knots}
                  onChange={(e) =>
                    updateField(
                      "current_speed_knots",
                      e.target.value
                    )
                  }
                />

              </label>


              <label>
                Current direction

                <input
                  value={form.current_direction_deg}
                  onChange={(e) =>
                    updateField(
                      "current_direction_deg",
                      e.target.value
                    )
                  }
                />

              </label>


              <label>
                Lookback hours

                <input
                  value={form.lookback_hours}
                  onChange={(e) =>
                    updateField(
                      "lookback_hours",
                      e.target.value
                    )
                  }
                />

              </label>


              <label>
                Forecast hours

                <input
                  value={form.forecast_hours}
                  onChange={(e) =>
                    updateField(
                      "forecast_hours",
                      e.target.value
                    )
                  }
                />

              </label>


              <label>
                Time step

                <input
                  value={form.time_step_hours}
                  onChange={(e) =>
                    updateField(
                      "time_step_hours",
                      e.target.value
                    )
                  }
                />

              </label>

            </div>

          </div>
        </Bracket>
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
          onClick={runAnalysis}
          disabled={
            loading ||
            !uploadedFile
          }
        >

          {loading ? (
            <>
              <Loader2
                size={16}
                className="spin"
              />

              Running analysis...
            </>
          ) : (
            "Run analysis →"
          )}

        </button>

      </div>

    </div>
  );
}


/* ==========================================================================
   STAGE 02 — PREPROCESSING
   ========================================================================== */

export function PreprocessStage({
  go,
  analysis,
  uploadedImage,
}) {
  const segmentation =
    analysis?.segmentation || {};

  const geometry =
    analysis?.geometry || {};


  if (!analysis) {
    return (
      <div className="screen">

        <StageHead
          eyebrow="02 / PREPROCESS"
          title="Awaiting SAR Analysis"
          description="Run the investigation to generate the segmentation result."
        />

        <Bracket>

          <div
            style={{
              padding: "48px",
              textAlign: "center",
            }}
          >

            <div
              style={{
                fontSize: "18px",
                marginBottom: "12px",
              }}
            >
              NO ANALYSIS RESULT
            </div>

            <button
              onClick={() => go("sar")}
            >
              BACK TO SAR
            </button>

          </div>

        </Bracket>

      </div>
    );
  }


  const maskImage =
    segmentation.mask_image;


  const spillPixels =
    segmentation.spill_pixels ??
    geometry.area_pixels ??
    0;


  const coverage =
    segmentation.coverage_ratio ??
    geometry.coverage_ratio ??
    0;


  const maskShape =
    segmentation.mask_shape;


  return (
    <div className="screen">

      <StageHead
        eyebrow="02 / PREPROCESS"
        title="SAR scene and segmentation mask"
        description="The uploaded scene is transformed into a pixel-level spill mask for downstream analysis."
      />


      <div
        style={{
          display: "grid",
          gridTemplateColumns:
            "repeat(auto-fit, minmax(320px, 1fr))",
          gap: "24px",
        }}
      >

        {/* ORIGINAL SAR */}

        <Bracket>

          <div
            style={{
              padding: "20px",
            }}
          >

            <div
              className="mono"
              style={{
                fontSize: "11px",
                color: "#4E7C93",
                letterSpacing: "0.09em",
                marginBottom: "14px",
              }}
            >
              INPUT SAR SCENE
            </div>


            {uploadedImage ? (

              <div
                style={{
                  background: "#02090D",
                  minHeight: "340px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  overflow: "hidden",
                }}
              >

                <img
                  src={uploadedImage}
                  alt="Uploaded SAR scene"
                  style={{
                    width: "100%",
                    height: "340px",
                    objectFit: "contain",
                  }}
                />

              </div>

            ) : (

              <div
                style={{
                  minHeight: "340px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  border: "1px solid #163B4E",
                  color: "#4E7C93",
                }}
              >
                SAR IMAGE UNAVAILABLE
              </div>

            )}

          </div>

        </Bracket>


        {/* REAL U-NET MASK */}

        <Bracket>

          <div
            style={{
              padding: "20px",
            }}
          >

            <div
              className="mono"
              style={{
                fontSize: "11px",
                color: "#4E7C93",
                letterSpacing: "0.09em",
                marginBottom: "14px",
              }}
            >
              U-NET SEGMENTATION
            </div>


            {maskImage ? (

              <div
                style={{
                  background: "#02090D",
                  minHeight: "340px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  padding: "12px",
                }}
              >

                <img
                  src={maskImage}
                  alt="U-Net oil spill segmentation mask"
                  style={{
                    width: "100%",
                    height: "316px",
                    objectFit: "contain",
                    imageRendering: "pixelated",
                  }}
                />

              </div>

            ) : (

              <div
                style={{
                  minHeight: "340px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  border: "1px solid #163B4E",
                  color: "#4E7C93",
                }}
              >
                MASK UNAVAILABLE
              </div>

            )}

          </div>

        </Bracket>

      </div>


      {/* REAL MEASUREMENTS */}

      <div
        style={{
          display: "grid",
          gridTemplateColumns:
            "repeat(auto-fit, minmax(160px, 1fr))",
          gap: "18px",
          marginTop: "24px",
        }}
      >

        <Bracket>

          <div style={{ padding: "18px" }}>

            <Reading
              label="SPILL PIXELS"
              value={
                Number(
                  spillPixels
                ).toLocaleString()
              }
            />

          </div>

        </Bracket>


        <Bracket>

          <div style={{ padding: "18px" }}>

            <Reading
              label="MASK COVERAGE"
              value={`${(
                Number(coverage) * 100
              ).toFixed(2)}%`}
            />

          </div>

        </Bracket>


        <Bracket>

          <div style={{ padding: "18px" }}>

            <Reading
              label="MASK SIZE"
              value={
                Array.isArray(maskShape)
                  ? `${maskShape[1]} × ${maskShape[0]}`
                  : "—"
              }
            />

          </div>

        </Bracket>


        <Bracket>

          <div style={{ padding: "18px" }}>

            <Reading
              label="STATUS"
              value={
                segmentation.mask_available
                  ? "READY"
                  : "UNAVAILABLE"
              }
            />

          </div>

        </Bracket>

      </div>


      <StageNav
        onNext={() => go("vision")}
      />

    </div>
  );
}


/* ==========================================================================
   STAGE 03 — VISION
   ========================================================================== */

export function VisionStage({
  go,
  analysis,
}) {
  if (!analysis) {
    return (
      <div className="screen">

        <StageHead
          eyebrow="03 / VISION"
          title="Awaiting Investigation"
          description="Run the SAR analysis before entering the vision stage."
        />

        <Bracket>

          <div
            style={{
              padding: "48px",
              textAlign: "center",
            }}
          >

            <div
              style={{
                marginBottom: "20px",
              }}
            >
              NO ANALYSIS RESULT
            </div>

            <button
              onClick={() => go("sar")}
            >
              BACK TO DETECT
            </button>

          </div>

        </Bracket>

      </div>
    );
  }


  const models =
    analysis.vision_models || {};


  const modelEntries = [
    models.unet,
    models.deeplabv3,
    models.transunet,
  ].filter(Boolean);


  return (
    <div className="screen">

      <StageHead
        eyebrow="03 / VISION"
        title="Three models examine the spill"
        description="The trained segmentation models provide independent views of the SAR scene."
      />


      <div
        style={{
          display: "grid",
          gridTemplateColumns:
            "repeat(auto-fit, minmax(280px, 1fr))",
          gap: "20px",
        }}
      >

        {modelEntries.map(
          (model) => (

            <Bracket key={model.key}>

              <div
                style={{
                  padding: "20px",
                }}
              >

                <div
                  className="mono"
                  style={{
                    color: COLORS.cyan,
                    marginBottom: "14px",
                  }}
                >
                  {model.name}
                </div>


                {model.mask_image ? (

                  <img
                    src={model.mask_image}
                    alt={`${model.name} segmentation mask`}
                    style={{
                      width: "100%",
                      height: "240px",
                      objectFit: "contain",
                      background: "#02090D",
                      imageRendering: "pixelated",
                    }}
                  />

                ) : (

                  <div
                    style={{
                      height: "240px",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      border: "1px solid #163B4E",
                      color: "#4E7C93",
                    }}
                  >
                    MASK UNAVAILABLE
                  </div>

                )}


                <div
                  style={{
                    marginTop: "18px",
                    display: "grid",
                    gap: "10px",
                  }}
                >

                  <Reading
                    label="DETECTED"
                    value={
                      model.detected
                        ? "YES"
                        : "NO"
                    }
                  />

                  <Reading
                    label="CONFIDENCE"
                    value={
                      model.confidence !== null &&
                      model.confidence !== undefined
                        ? `${(
                            Number(
                              model.confidence
                            ) * 100
                          ).toFixed(2)}%`
                        : "—"
                    }
                  />

                  <Reading
                    label="SPILL AREA"
                    value={
                      model.area !== undefined
                        ? Number(
                            model.area
                          ).toLocaleString()
                        : "—"
                    }
                  />

                </div>

              </div>

            </Bracket>

          )
        )}

      </div>


      <StageNav
        onNext={() =>
          go("orchestrator")
        }
      />

    </div>
  );
}


/* ==========================================================================
   STAGE 04 — ORCHESTRATOR
   ========================================================================== */

export function OrchestratorStage({
  go,
  analysis,
}) {
  if (!analysis) {
    return (
      <div className="screen">

        <StageHead
          eyebrow="04 / ORCHESTRATOR"
          title="Awaiting Investigation"
          description="The downstream pipeline starts after the SAR analysis returns a result."
        />

        <Bracket>

          <div
            style={{
              padding: "52px",
              textAlign: "center",
            }}
          >

            <div
              style={{
                fontSize: "20px",
                marginBottom: "12px",
              }}
            >
              NO INVESTIGATION RESULT
            </div>

            <button
              onClick={() => go("sar")}
            >
              BACK TO DETECT
            </button>

          </div>

        </Bracket>

      </div>
    );
  }


  const orchestrator =
    analysis.orchestrator || {};

  const segmentation =
    analysis.segmentation || {};


  const models =
    analysis.vision_models || {};


  const modelEntries = [
    models.unet,
    models.deeplabv3,
    models.transunet,
  ].filter(Boolean);


  const verdict =
    orchestrator.verdict ||
    orchestrator.decision ||
    (
      analysis.spill_detected
        ? "MAJORITY_SPILL"
        : "NO_SPILL"
    );


  return (
    <div className="screen">

      <StageHead
        step="04"
        question="Decision point"
        title="One verdict from three opinions"
        lede="The orchestrator compares the model outputs and determines whether the investigation continues."
      />


      <div
        style={{
          display: "grid",
          gridTemplateColumns:
            "repeat(auto-fit, minmax(260px, 1fr))",
          gap: 40,
          alignItems: "start",
        }}
      >

        <div>

          <svg
            viewBox="0 0 320 260"
            width="100%"
            style={{
              maxWidth: 360,
              display: "block",
            }}
          >

            {modelEntries.map(
              (model, i) => (

                <g key={model.key || i}>

                  <rect
                    x="6"
                    y={14 + i * 58}
                    width="108"
                    height="40"
                    fill="none"
                    stroke="#1B4A60"
                  />

                  <text
                    x="18"
                    y={34 + i * 58}
                    className="mono"
                    fontSize="10"
                    fill="#A8CBDC"
                  >
                    {model.name}
                  </text>

                  <text
                    x="18"
                    y={47 + i * 58}
                    className="mono"
                    fontSize="8.5"
                    fill="#4E7C93"
                  >
                    {model.confidence != null
                      ? Number(
                          model.confidence
                        ).toFixed(2)
                      : "—"}
                  </text>

                  <path
                    d={`M 114 ${
                      34 + i * 58
                    } C 150 ${
                      34 + i * 58
                    }, 158 148, 196 148`}
                    fill="none"
                    stroke={COLORS.cyan}
                    strokeWidth="1"
                    opacity="0.5"
                    className="flow-dash"
                  />

                </g>

              )
            )}


            <rect
              x="198"
              y="124"
              width="112"
              height="48"
              fill="rgba(53,201,245,0.07)"
              stroke={COLORS.cyan}
            />

            <text
              x="212"
              y="145"
              className="mono"
              fontSize="9.5"
              fill={COLORS.cyan}
            >
              ORCHESTRATOR
            </text>

            <text
              x="212"
              y="160"
              className="mono"
              fontSize="8.5"
              fill="#7FAEC7"
            >
              majority vote
            </text>


            <line
              x1="254"
              y1="172"
              x2="254"
              y2="206"
              stroke="#1B4A60"
              strokeWidth="1"
            />

            <polygon
              points="250,206 258,206 254,214"
              fill="#1B4A60"
            />

            <text
              x="214"
              y="236"
              className="mono"
              fontSize="10"
              fill={
                analysis.spill_detected
                  ? COLORS.warning
                  : COLORS.cyan
              }
            >
              {analysis.spill_detected
                ? "SPILL DETECTED"
                : "NO SPILL"}
            </text>

          </svg>


          <p
            className="note"
            style={{
              marginTop: 24,
              maxWidth: 380,
            }}
          >
            The orchestrator combines the independent
            model outputs into one investigation decision.
          </p>

        </div>


        <div>

          <Bracket live>

            <div
              style={{
                padding: "30px 28px",
              }}
            >

              <div
                className="label"
                style={{
                  color: COLORS.cyan,
                  marginBottom: 16,
                }}
              >
                Combined result
              </div>


              <div
                style={{
                  fontSize: 22,
                  color: analysis.spill_detected
                    ? COLORS.warning
                    : COLORS.cyan,
                  marginBottom: 20,
                }}
              >
                {verdict}
              </div>


              <div
                style={{
                  display: "flex",
                  gap: 34,
                  flexWrap: "wrap",
                }}
              >

                <Reading
                  label="Confidence"
                  value={
                    orchestrator.confidence != null
                      ? Number(
                          orchestrator.confidence
                        ).toFixed(2)
                      : "—"
                  }
                  size={34}
                  color={COLORS.cyan}
                />


                <Reading
                  label="Model agreement"
                  value={
                    orchestrator.agreement != null
                      ? Number(
                          orchestrator.agreement
                        ).toFixed(2)
                      : "—"
                  }
                  size={34}
                />


                <Reading
                  label="Mask IoU"
                  value={
                    orchestrator.iou != null
                      ? Number(
                          orchestrator.iou
                        ).toFixed(2)
                      : "—"
                  }
                  size={34}
                />

              </div>

            </div>

          </Bracket>


          <div
            style={{
              marginTop: 28,
            }}
          >

            <Reading
              label="MASK STATUS"
              value={
                segmentation.mask_available
                  ? "AVAILABLE"
                  : "UNAVAILABLE"
              }
            />

          </div>


          <div
            style={{
              marginTop: 24,
            }}
          >
            <SimTag />
          </div>

        </div>

      </div>


      <StageNav
        onBack={() => go("vision")}
        onNext={() =>
          go("characterize")
        }
        nextLabel="Characterize the spill"
      />

    </div>
  );
}


/* ==========================================================================
   MAIN DETECT SCREEN
   ========================================================================== */

export default function Detect({
  go,
  analysis,
  setAnalysis,
  uploadedFile,
  setUploadedFile,
  uploadedImage,
}) {
  const [stage, setStage] =
    useState("sar");


  const renderStage = () => {

    switch (stage) {

      case "sar":

        return (
          <SarStage
            go={go}
            analysis={analysis}
            setAnalysis={setAnalysis}
            uploadedFile={uploadedFile}
            setUploadedFile={setUploadedFile}
            uploadedImage={uploadedImage}
          />
        );


      case "preprocess":

        return (
          <PreprocessStage
            go={go}
            analysis={analysis}
            uploadedImage={uploadedImage}
          />
        );


      case "vision":

        return (
          <VisionStage
            go={go}
            analysis={analysis}
          />
        );


      case "orchestrator":

        return (
          <OrchestratorStage
            go={go}
            analysis={analysis}
          />
        );


      default:

        return (
          <SarStage
            go={go}
            analysis={analysis}
            setAnalysis={setAnalysis}
            uploadedFile={uploadedFile}
            setUploadedFile={setUploadedFile}
            uploadedImage={uploadedImage}
          />
        );

    }
  };


  return (
    <div>

      {renderStage()}


      <div
        style={{
          display: "flex",
          gap: "8px",
          marginTop: "24px",
          justifyContent: "center",
        }}
      >

        {[
          ["sar", "01"],
          ["preprocess", "02"],
          ["vision", "03"],
          ["orchestrator", "04"],
        ].map(
          ([value, label]) => (

            <button
              key={value}
              onClick={() =>
                setStage(value)
              }
              style={{
                minWidth: "48px",
              }}
            >
              {label}
            </button>

          )
        )}

      </div>

    </div>
  );
}