from agno.agent import Agent
from agno.models.ollama import Ollama

from app.models import InventoryReport

inventory_agent = Agent(
    name="Inventory Lookup Agent",
    role="Look up what inventory is expected at the dock at a given time",
    model=Ollama(id="gemma3:4b"),
    instructions=[
        "You are the inventory lookup specialist for a chemical warehouse dock.",
        "You will receive expected inventory data for a time slot.",
        "Extract each item with its quantity, container type, and hazard classifications.",
    ],
    output_schema=InventoryReport,
)
