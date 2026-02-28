from agno.agent import Agent
from agno.models.ollama import Ollama

audio_agent = Agent(
    name="Audio Agent",
    role="Process voice commands from dock workers about expected shipments",
    model=Ollama(id="gemma3:4b"),
    instructions=[
        "You are the audio processing specialist for a chemical warehouse dock.",
        "You will receive a transcription of what the dock worker said.",
        "Extract key information: expected items, quantities, and any special handling instructions.",
    ],
    markdown=True,
)
