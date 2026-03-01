from agno.agent import Agent
from agno.models.ollama import Ollama

from app.models import VisionReport

vision_agent = Agent(
    name="Vision Agent",
    role="Analyze camera images of the dock to identify boxes, containers, and hazard symbols",
    model=Ollama(id="gemma3:12b"),
    instructions=[
        "You are the vision specialist for a chemical warehouse dock.",
        "You will receive a description of what is visible at the dock from the camera feed.",
        "For each container report: description, quantity, and hazard symbols with confidence.",
        "Flag any unmarked or suspicious items separately.",
    ],
    output_schema=VisionReport,
    debug_mode=True,
)
