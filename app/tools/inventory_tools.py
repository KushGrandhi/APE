"""Tool for looking up expected inventory by time slot."""

# Mock schedule database
SCHEDULE = {
    "08:00": "5x Sulfuric Acid drums (Corrosive), 3x Acetone containers (Flammable)",
    "10:00": "8x Sodium Hydroxide bags (Corrosive), 2x Methanol drums (Flammable, Toxic)",
    "12:00": "15x Bleach containers (Corrosive), 10x Ammonia tanks (Toxic)",
    "14:00": "10x HCL drums (Corrosive, Toxic), 5x NaOH bags (Corrosive)",
    "16:00": "6x Ethanol drums (Flammable), 4x Phosphoric Acid containers (Corrosive)",
}


def inventory_expectation(time: str) -> str:
    """Look up what inventory shipment is expected at the dock for a given time slot.

    Args:
        time: The time slot to check, e.g. "14:00".

    Returns:
        A description of the expected shipment for that time slot.
    """
    if time in SCHEDULE:
        return f"Expected at {time}: {SCHEDULE[time]}"
    # Find the closest earlier time slot
    available = sorted(SCHEDULE.keys())
    closest = None
    for slot in available:
        if slot <= time:
            closest = slot
    if closest:
        return f"No exact schedule for {time}. Closest earlier slot ({closest}): {SCHEDULE[closest]}"
    return f"No shipment scheduled at or before {time}."
