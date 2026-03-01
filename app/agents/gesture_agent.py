from agno.agent import Agent
from agno.models.ollama import Ollama

from app.models import GestureReport

gesture_agent = Agent(
    name="Gesture Agent",
    role="Recognize human gestures at the dock to determine approval or rejection",
    model=Ollama(id="gemma3:12b"),
    instructions=[
        "You are the gesture recognition specialist for a chemical warehouse dock.",
        "You will receive a description of the dock worker's gesture.",
        "Identify the gesture and interpret it as: 'approve', 'review', or 'decline'.",
        "Provide a confidence score between 0.0 and 1.0.",
    ],
    output_schema=GestureReport,
)
