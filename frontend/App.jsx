import React, {
  useState,
  useCallback,
  useEffect,
} from "react";

import {
  AnimatePresence,
  motion,
} from "framer-motion";

import Landing from "./screens/Landing.jsx";
import Overview from "./screens/Overview.jsx";
import Rail from "./components/Rail.jsx";
import Alerts from "./screens/Alerts.jsx";

import {
  SarStage,
  PreprocessStage,
  VisionStage,
  OrchestratorStage,
} from "./screens/Detect.jsx";

import {
  CharacterizeStage,
  EnvironmentStage,
  DriftStage,
} from "./screens/Understand.jsx";

import {
  SourceTypeStage,
  SpaceTimeStage,
  TrajectoryStage,
  FusionStage,
  RankingStage,
} from "./screens/Attribute.jsx";

import {
  ResultStage,
  ReportStage,
} from "./screens/Deliver.jsx";

import {
  STAGES,
  stageIndex,
} from "./data/pipeline.js";

import { CASE } from "./data/mock.js";


const SCREENS = {
  overview: Overview,
  alerts: Alerts,

  sar: SarStage,
  preprocess: PreprocessStage,
  vision: VisionStage,
  orchestrator: OrchestratorStage,

  characterize: CharacterizeStage,
  environment: EnvironmentStage,
  drift: DriftStage,

  sourcetype: SourceTypeStage,
  spacetime: SpaceTimeStage,
  trajectory: TrajectoryStage,
  fusion: FusionStage,
  ranking: RankingStage,

  result: ResultStage,
  report: ReportStage,
};


export default function App() {
  const [view, setView] =
    useState("landing");

  const [analysis, setAnalysis] =
    useState(null);

  const [uploadedFile, setUploadedFile] =
    useState(null);

  const [uploadedImage, setUploadedImage] =
    useState(null);


  const go = useCallback(
    (id) => {
      setView(id);
    },
    []
  );


  useEffect(() => {
    if (!uploadedFile) {
      setUploadedImage(null);
      return undefined;
    }

    const url =
      URL.createObjectURL(uploadedFile);

    setUploadedImage(url);

    return () => {
      URL.revokeObjectURL(url);
    };
  }, [uploadedFile]);


  useEffect(() => {
    if (view !== "landing") {
      window.scrollTo({
        top: 0,
      });
    }
  }, [view]);


  const startNewInvestigation =
    useCallback(() => {
      setAnalysis(null);
      setUploadedFile(null);
      setUploadedImage(null);
      go("sar");
    }, [go]);


  if (view === "landing") {
    return (
      <Landing
        onStart={() => {
          setAnalysis(null);
          setUploadedFile(null);
          setUploadedImage(null);
          go("overview");
        }}
      />
    );
  }


  const Screen =
    SCREENS[view] || Overview;


  const stage =
    STAGES.find(
      (item) => item.id === view
    );


  const idx =
    stageIndex(view);


  const progress =
    idx > -1
      ? ((idx + 1) / STAGES.length) * 100
      : 0;


  const headerId =
    analysis?.spill?.timestamp
      ? "LIVE INVESTIGATION"
      : CASE.id;


  const headerTime =
    analysis?.spill?.timestamp ||
    CASE.acquired;


  return (
    <div className="shell">

      <Rail
        active={view}
        go={go}
      />


      <main className="stage">

        {/* Progress bar */}

        <div
          style={{
            height: 2,
            background: "#0A2434",
          }}
        >
          <div
            style={{
              height: "100%",
              width: `${progress}%`,
              background:
                "linear-gradient(90deg, #1FA8DE, #8DDCF7)",
              transition:
                "width .5s cubic-bezier(.16,.8,.24,1)",
            }}
          />
        </div>


        {/* Header */}

        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            gap: 16,
            padding:
              "22px clamp(20px, 4vw, 44px) 0",
            flexWrap: "wrap",
          }}
        >

          <div
            className="mono"
            style={{
              fontSize: 11,
              color: "#4E7C93",
              letterSpacing: "0.09em",
            }}
          >
            {headerId}

            {stage
              ? ` · STAGE ${stage.num} OF 14`
              : view === "alerts"
                ? " · ALERTS"
                : " · OVERVIEW"}
          </div>


          <div
            className="mono"
            style={{
              fontSize: 11,
              color: "#3F6B80",
            }}
          >
            {headerTime}
          </div>

        </div>


        {/* Main content */}

        <div className="pad">

          <AnimatePresence mode="wait">

            <motion.div
              key={view}
              initial={{
                opacity: 0,
                y: 14,
              }}
              animate={{
                opacity: 1,
                y: 0,
              }}
              exit={{
                opacity: 0,
                y: -8,
              }}
              transition={{
                duration: 0.35,
                ease: [
                  0.16,
                  0.8,
                  0.24,
                  1,
                ],
              }}
            >

              <Screen
                go={go}
                analysis={analysis}
                setAnalysis={setAnalysis}
                uploadedFile={uploadedFile}
                setUploadedFile={
                  setUploadedFile
                }
                uploadedImage={
                  uploadedImage
                }
                onRestart={
                  startNewInvestigation
                }
              />

            </motion.div>

          </AnimatePresence>

        </div>

      </main>

    </div>
  );
}