from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class AnalyzeResponse(BaseModel):
    spill_detected: bool

    segmentation: Dict[str, Any]
    geometry: Dict[str, Any]
    attribution: Dict[str, Any]

    phase: Optional[str] = None
    status: Optional[str] = None

    spill: Optional[Dict[str, Any]] = None
    environment: Optional[Dict[str, Any]] = None
    hindcast: Optional[Dict[str, Any]] = None
    source_zone: Optional[Dict[str, Any]] = None
    source_time: Optional[Dict[str, Any]] = None
    forward_prediction: Optional[Dict[str, Any]] = None

    ais_candidates: List[Dict[str, Any]] = []
    ranked_candidates: List[Dict[str, Any]] = []

    alert: Optional[Dict[str, Any]] = None
    prototype_note: Optional[str] = None