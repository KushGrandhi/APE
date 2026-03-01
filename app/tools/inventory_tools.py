"""Inventory lookup tool — mock implementation."""

from app.tools.base import InventorySource

# Mock schedule database
SCHEDULE = {
    "08:00": "5x Sulfuric Acid drums (Corrosive), 3x Acetone containers (Flammable)",
    "10:00": "8x Sodium Hydroxide bags (Corrosive), 2x Methanol drums (Flammable, Toxic)",
    "12:00": "15x Bleach containers (Corrosive), 10x Ammonia tanks (Toxic)",
    "14:00": "10x HCL drums (Corrosive, Toxic), 5x NaOH bags (Corrosive)",
    "16:00": "6x Ethanol drums (Flammable), 4x Phosphoric Acid containers (Corrosive)",
}


class MockInventorySource(InventorySource):
    """Returns expected inventory from a hardcoded schedule."""

    def __init__(self, schedule: dict[str, str] | None = None):
        self.schedule = schedule or SCHEDULE

    def get_expectation(self, time: str) -> str:
        if time in self.schedule:
            return f"Expected at {time}: {self.schedule[time]}"
        available = sorted(self.schedule.keys())
        closest = None
        for slot in available:
            if slot <= time:
                closest = slot
        if closest:
            return f"No exact schedule for {time}. Closest earlier slot ({closest}): {self.schedule[closest]}"
        return f"No shipment scheduled at or before {time}."


# Default instance used by the orchestrator
_default = MockInventorySource()


def inventory_expectation(time: str) -> str:
    """Look up what inventory shipment is expected at the dock for a given time slot."""
    return _default.get_expectation(time)
