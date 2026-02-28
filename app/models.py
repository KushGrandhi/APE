from pydantic import BaseModel


class HazardSymbol(BaseModel):
    symbol_name: str  # e.g. "Flammable", "Corrosive", "Toxic"
    confidence: float


class ReceivedBox(BaseModel):
    description: str
    hazard_symbols: list[HazardSymbol]


class DockInspectionReport(BaseModel):
    timestamp: str
    expected_inventory: str  # What was expected per schedule
    voice_instruction: str  # What audio agent heard
    boxes_seen: list[ReceivedBox]  # What vision agent detected
    human_gesture: str  # "approve" | "review" | "decline"
    match_status: str  # "match" | "mismatch" | "partial_match"
    discrepancies: list[str]  # List of mismatches found
    final_decision: str  # "approved" | "needs_review" | "rejected"
