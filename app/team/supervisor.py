from agno.agent import Agent
from agno.models.ollama import Ollama

from app.models import DockInspectionReport, PreliminaryReport

# Stage 1: Compare expected vs received, produce preliminary report
preliminary_agent = Agent(
    name="Dock Inspection Supervisor — Preliminary",
    model=Ollama(id="gemma3:12b"),
    instructions=[
        "You are the dock supervisor for a chemical warehouse.",
        "You will receive JSON reports from three specialist agents: Inventory, Vision, and Audio.",
        "Each report includes confidence scores. Your job is to:",
        "1. Compare expected inventory against what was actually seen at the dock",
        "2. Note any discrepancies in quantities, labels, or hazard symbols",
        "3. Cross-reference the audio instruction with the inventory schedule",
        "4. Weigh confidence scores: flag low-confidence detections (<0.8) as needing review",
        "5. Summarize confidence levels in confidence_summary",
        "6. Recommend an action: 'approve', 'needs_review', or 'reject'",
        "If any agent confidence is below 0.7, recommend 'needs_review' regardless of match.",
        "Do NOT make a final decision yet — that requires human confirmation.",
    ],
    output_schema=PreliminaryReport,
    markdown=True,
)

# Stage 2: Incorporate human gesture, produce final report
final_agent = Agent(
    name="Dock Inspection Supervisor — Final",
    model=Ollama(id="gemma3:12b"),
    instructions=[
        "You are the dock supervisor finalizing an inspection report.",
        "You will receive a preliminary report and a human gesture confirmation.",
        "Your job is to:",
        "1. Keep all fields from the preliminary report",
        "2. Incorporate the human gesture (approve/review/decline)",
        "3. Determine final_decision based on both the recommendation and the gesture:",
        "   - If gesture is 'approve' AND recommendation is 'approve' → 'approved'",
        "   - If gesture is 'decline' → 'rejected' regardless of recommendation",
        "   - Otherwise → 'needs_review'",
        "4. Assign a priority for processing this shipment:",
        "   - 'critical': contains highly dangerous materials (Toxic, Explosive, Radioactive) or has discrepancies with hazardous items",
        "   - 'high': contains hazardous materials (Corrosive, Flammable) and is fully matched",
        "   - 'medium': non-hazardous or partially matched shipment with minor discrepancies",
        "   - 'low': non-hazardous, fully matched, no special handling needed",
        "5. Explain the priority assignment in priority_reason",
    ],
    output_schema=DockInspectionReport,
    markdown=True,
)
