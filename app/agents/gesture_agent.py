from agno.agent import Agent
from agno.models.ollama import Ollama

gesture_agent = Agent(
    name="Gesture Agent",
    role="Recognize human gestures at the dock to determine approval or rejection",
    model=Ollama(id="gemma3:12b"),
    instructions=[
        "You are the gesture recognition specialist for a chemical warehouse dock.",
        "You will receive a description of the dock worker's gesture.",
        "Interpret the gesture as one of: 'approve', 'review', or 'decline'.",
        "Report the detected gesture and your interpretation clearly.",
    ],
    markdown=True,
)
