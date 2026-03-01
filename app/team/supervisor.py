from agno.agent import Agent
from agno.models.ollama import Ollama

from app.models import DockInspectionReport

supervisor_agent = Agent(
    name="Dock Inspection Supervisor",
    model=Ollama(id="gemma3:12b"),
    instructions=[
        "You are the dock supervisor for a chemical warehouse.",
        "You will receive JSON reports from four specialist agents: Inventory, Vision, Audio, and Gesture.",
        "Each report includes confidence scores. Your job is to:",
        "1. Compare expected inventory against what was actually seen at the dock",
        "2. Note any discrepancies in quantities, labels, or hazard symbols",
        "3. Incorporate the dock worker's voice instruction and gesture as confirmation",
        "4. Weigh confidence scores: flag low-confidence detections (<0.8) as needing review",
        "5. Summarize confidence levels in confidence_summary",
        "6. Produce a final inspection decision: 'approved', 'needs_review', or 'rejected'",
        "If any agent confidence is below 0.7, set final_decision to 'needs_review' regardless of match.",
    ],
    output_schema=DockInspectionReport,
    markdown=True,
)
