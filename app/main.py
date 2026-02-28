"""Entry point for the Chemical Warehouse Dock Inspection system.

Orchestrates specialist agents by:
1. Calling tool functions directly to gather sensor/mock data
2. Running each specialist agent with its data for interpretation
3. Feeding all agent outputs to the supervisor for final decision
"""

from datetime import datetime

from app.agents.audio_agent import audio_agent
from app.agents.gesture_agent import gesture_agent
from app.agents.inventory_agent import inventory_agent
from app.agents.vision_agent import vision_agent
from app.team.supervisor import supervisor_agent
from app.tools.audio_tools import listen_what_to_expect
from app.tools.gesture_tools import see_what_human_has_to_say
from app.tools.inventory_tools import inventory_expectation
from app.tools.vision_tools import inventory_what_you_see


def run_inspection(time: str = "14:00"):
    """Run a full dock inspection by orchestrating all agents."""

    print(f"\n{'='*60}")
    print(f"  DOCK INSPECTION - {time}")
    print(f"{'='*60}\n")

    # Step 1: Gather data from all sensors/sources (mock tools)
    inventory_data = inventory_expectation(time)
    vision_data = inventory_what_you_see("dock_cam_01.jpg")
    audio_data = listen_what_to_expect("dock_audio_01.wav")
    gesture_data = see_what_human_has_to_say("gesture_cam_01.jpg")

    print("[Data Collected]")
    print(f"  Inventory: {inventory_data}")
    print(f"  Vision:    {vision_data}")
    print(f"  Audio:     {audio_data}")
    print(f"  Gesture:   {gesture_data}")
    print()

    # Step 2: Run each specialist agent to interpret its data
    print("[Running Specialist Agents...]\n")

    inventory_response = inventory_agent.run(
        f"Analyze this expected inventory data for the {time} delivery: {inventory_data}"
    )
    print(f"--- Inventory Agent ---\n{inventory_response.content}\n")

    vision_response = vision_agent.run(
        f"Analyze this dock camera observation: {vision_data}"
    )
    print(f"--- Vision Agent ---\n{vision_response.content}\n")

    audio_response = audio_agent.run(
        f"Analyze this dock worker voice transcription: {audio_data}"
    )
    print(f"--- Audio Agent ---\n{audio_response.content}\n")

    gesture_response = gesture_agent.run(
        f"Analyze this gesture observation: {gesture_data}"
    )
    print(f"--- Gesture Agent ---\n{gesture_response.content}\n")

    # Step 3: Feed all agent outputs to the supervisor for final decision
    print("[Running Supervisor...]\n")

    supervisor_prompt = f"""Produce a dock inspection report. Current timestamp: {datetime.now().isoformat()}

INVENTORY AGENT REPORT:
{inventory_response.content}

VISION AGENT REPORT:
{vision_response.content}

AUDIO AGENT REPORT:
{audio_response.content}

GESTURE AGENT REPORT:
{gesture_response.content}

Compare expected vs actual inventory. Flag any discrepancies. Produce the final DockInspectionReport JSON."""

    supervisor_response = supervisor_agent.run(supervisor_prompt)

    print(f"--- Supervisor Decision ---")
    print(supervisor_response.content)
    print()

    return supervisor_response


def main():
    run_inspection("14:00")


if __name__ == "__main__":
    main()
