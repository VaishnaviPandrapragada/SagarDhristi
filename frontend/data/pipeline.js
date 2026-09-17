/* The 15 stages, grouped into the four questions the system answers:
   what did we see, what is it, who was there, what do we hand over. */

export const STAGES = [
  { id: "sar",          num: "01", label: "SAR image",        phase: "Detect",     question: "Our starting point" },
  { id: "preprocess",   num: "02", label: "Preprocessing",    phase: "Detect",     question: "Cleaning the image" },
  { id: "vision",       num: "03", label: "Vision models",    phase: "Detect",     question: "Three models look for a spill" },
  { id: "orchestrator", num: "04", label: "Orchestrator",     phase: "Detect",     question: "Combine the predictions" },

  { id: "characterize", num: "05", label: "Characterize",     phase: "Understand", question: "Understanding the spill" },
  { id: "environment",  num: "06", label: "Ocean & weather",  phase: "Understand", question: "How the sea is moving" },
  { id: "drift",        num: "07", label: "Drift analysis",   phase: "Understand", question: "Where from, where next" },

  { id: "sourcetype",   num: "08", label: "Source type",      phase: "Attribute",  question: "What kind of source" },
  { id: "spacetime",    num: "09", label: "Space-time filter",phase: "Attribute",  question: "Finding candidates" },
  { id: "trajectory",   num: "10", label: "Trajectory (RNN)", phase: "Attribute",  question: "How each vessel moved" },
  { id: "fusion",       num: "11", label: "Evidence fusion",  phase: "Attribute",  question: "Putting the pieces together" },
  { id: "ranking",      num: "12", label: "Vessel ranking",   phase: "Attribute",  question: "Most likely source" },

  { id: "result",       num: "13", label: "Result",           phase: "Deliver",    question: "A clear, explainable output" },
  { id: "api",          num: "14", label: "API layer",        phase: "Deliver",    question: "Making it accessible" },
  { id: "report",       num: "15", label: "Report & export",  phase: "Deliver",    question: "Handing it over" },
];

export const PHASES = ["Detect", "Understand", "Attribute", "Deliver"];

export const stageIndex = (id) => STAGES.findIndex((s) => s.id === id);
export const nextStage = (id) => STAGES[stageIndex(id) + 1];
export const prevStage = (id) => STAGES[stageIndex(id) - 1];
