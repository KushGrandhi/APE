from agno.agent import Agent
from agno.models.ollama import Ollama

vision_agent = Agent(
    name="Vision Agent",
    role="Analyze camera images of the dock to identify boxes, containers, and hazard symbols",
    model=Ollama(id="gemma3:12b"),
    instructions=[
        "You are the vision specialist for a chemical warehouse dock.",
        "You will receive a description of what is visible at the dock from the camera feed.",
        "Report all visible containers, their labels, quantities, and any hazard symbols detected.",
        "Pay special attention to hazardous material symbols: Flammable, Corrosive, Toxic, Oxidizer, etc.",
    ],
    markdown=True,
)
