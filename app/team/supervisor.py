from agno.agent import Agent
from agno.models.ollama import Ollama

from app.models import DockInspectionReport

supervisor_agent = Agent(
    name="Dock Inspection Supervisor",
    model=Ollama(id="gemma3:12b"),
    instructions=[
        "You are the dock supervisor for a chemical warehouse.",
        "You will receive reports from four specialist agents: Inventory, Vision, Audio, and Gesture.",
        "Your job is to:",
        "1. Compare expected inventory against what was actually seen at the dock",
        "2. Note any discrepancies in quantities, labels, or hazard symbols",
        "3. Incorporate the dock worker's voice instruction and gesture as confirmation",
        "4. Produce a final inspection decision: 'approved', 'needs_review', or 'rejected'",
        "5. Output your response as JSON matching the DockInspectionReport schema exactly",
    ],
    output_schema=DockInspectionReport,
    markdown=True,
)
