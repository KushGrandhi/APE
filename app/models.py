from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Specialist agent outputs
# ---------------------------------------------------------------------------

class ExpectedItem(BaseModel):
    name: str           # e.g. "HCL", "NaOH"
    quantity: int
    container_type: str  # e.g. "drum", "bag", "tank"
    hazards: list[str]   # e.g. ["Corrosive", "Toxic"]


class InventoryReport(BaseModel):
    time_slot: str
    expected_items: list[ExpectedItem]
    notes: str  # any extra info from the schedule


class HazardSymbol(BaseModel):
    symbol_name: str   # e.g. "Flammable", "Corrosive", "Toxic"
    confidence: float  # 0.0–1.0 how certain the detection is


class ReceivedBox(BaseModel):
    description: str
    quantity: int
    confidence: float          # 0.0–1.0 overall detection confidence
    hazard_symbols: list[HazardSymbol]


class VisionReport(BaseModel):
    boxes_seen: list[ReceivedBox]
    unmarked_items: list[str]
    overall_confidence: float  # 0.0–1.0 overall scene confidence
    notes: str


class AudioReport(BaseModel):
    expected_items: list[ExpectedItem]
    special_instructions: str
    raw_transcription: str
    transcription_confidence: float  # 0.0–1.0 how clear the audio was


class GestureReport(BaseModel):
    gesture_observed: str   # e.g. "thumbs_up", "palm_out", "shrug"
    interpretation: str     # "approve" | "review" | "decline"
    confidence: float       # 0.0–1.0


# ---------------------------------------------------------------------------
# Supervisor outputs — two stages
# ---------------------------------------------------------------------------

class PreliminaryReport(BaseModel):
    """Stage 1: Supervisor compares expected vs received before human confirmation."""
    timestamp: str
    expected_inventory: str
    voice_instruction: str
    boxes_seen: list[ReceivedBox]
    match_status: str        # "match" | "mismatch" | "partial_match"
    discrepancies: list[str]
    confidence_summary: str
    recommended_action: str  # "approve" | "needs_review" | "reject"


class DockInspectionReport(BaseModel):
    """Stage 2: Final report after human gesture confirmation."""
    timestamp: str
    expected_inventory: str
    voice_instruction: str
    boxes_seen: list[ReceivedBox]
    match_status: str        # "match" | "mismatch" | "partial_match"
    discrepancies: list[str]
    confidence_summary: str
    recommended_action: str  # what the system recommended before human input
    human_gesture: str       # "approve" | "review" | "decline"
    final_decision: str      # "approved" | "needs_review" | "rejected"
    priority: str            # "critical" | "high" | "medium" | "low"
    priority_reason: str     # why this priority was assigned
