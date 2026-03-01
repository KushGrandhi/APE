"""Entry point for the Chemical Warehouse Dock Inspection system.

Orchestrates specialist agents by:
1. Calling tool functions directly to gather sensor/mock data
2. Running each specialist agent with its data for interpretation
3. Feeding all agent outputs to the supervisor for final decision
"""

import json
import os
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


def _agent_json(response) -> str:
    """Extract structured JSON string from an agent response."""
    return response.content


def run_inspection(
    time: str = "14:00",
    vision_source: str = "dock_cam_01.jpg",
    audio_source: str = "dock_audio_01.wav",
    gesture_source: str = "gesture_cam_01.jpg",
):
    """Run a full dock inspection by orchestrating all agents."""

    print(f"\n{'='*60}")
    print(f"  DOCK INSPECTION - {time}")
    print(f"{'='*60}\n")

    vision_mode = os.getenv("VISION_SOURCE", "mock")
    audio_mode = os.getenv("AUDIO_SOURCE", "mock")
    gesture_mode = os.getenv("GESTURE_SOURCE", "mock")

    # Step 1: Gather data from all sensors/sources
    inventory_data = inventory_expectation(time)
    vision_data = inventory_what_you_see(vision_source)
    audio_data = listen_what_to_expect(audio_source)
    gesture_data = see_what_human_has_to_say(gesture_source)

    print("[Data Collected]")
    print(f"  Inventory: {inventory_data}")
    print(f"  Vision:    {vision_data[:120]}...")
    print(f"  Audio:     {audio_data[:120]}...")
    print(f"  Gesture:   {gesture_data[:120]}...")
    print()

    # Step 2: Run each specialist agent to interpret its data
    print("[Running Specialist Agents...]\n")

    inventory_response = inventory_agent.run(
        f"Analyze this expected inventory data for the {time} delivery: {inventory_data}"
    )
    inventory_json = _agent_json(inventory_response)
    print(f"--- Inventory Agent ---\n{inventory_json}\n")

    # In real vision modes, the tool already ran gemma3 on the actual image.
    # In mock mode, let the vision agent add reasoning on top.
    if vision_mode == "mock":
        vision_response = vision_agent.run(
            f"Analyze this dock camera observation: {vision_data}"
        )
        vision_json = _agent_json(vision_response)
    else:
        vision_json = vision_data

    print(f"--- Vision Agent ---\n{vision_json}\n")

    # Audio agent always runs — extracts structured info from transcription.
    audio_response = audio_agent.run(
        f"A dock worker said the following about an incoming delivery. "
        f"Extract what packages are being delivered, quantities, and any hazard warnings:\n\n{audio_data}"
    )
    audio_json = _agent_json(audio_response)
    print(f"--- Audio Agent ---\n{audio_json}\n")

    # In real gesture modes, the tool already ran gemma3 on the image.
    # In mock mode, let the gesture agent add reasoning on top.
    if gesture_mode == "mock":
        gesture_response = gesture_agent.run(
            f"Analyze this gesture observation: {gesture_data}"
        )
        gesture_json = _agent_json(gesture_response)
    else:
        gesture_json = gesture_data

    print(f"--- Gesture Agent ---\n{gesture_json}\n")

    # Step 3: Feed all agent outputs to the supervisor for final decision
    print("[Running Supervisor...]\n")

    supervisor_prompt = f"""Produce a dock inspection report. Current timestamp: {datetime.now().isoformat()}

INVENTORY AGENT REPORT (JSON):
{inventory_json}

VISION AGENT REPORT (JSON):
{vision_json}

AUDIO AGENT REPORT (JSON):
{audio_json}

GESTURE AGENT REPORT (JSON):
{gesture_json}

Compare expected vs actual inventory. Flag any discrepancies. Produce the final DockInspectionReport JSON."""

    supervisor_response = supervisor_agent.run(supervisor_prompt)

    print(f"--- Supervisor Decision ---")
    print(supervisor_response.content)
    print()

    return supervisor_response


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Chemical Warehouse Dock Inspection")
    parser.add_argument("--time", default="14:00", help="Delivery time slot (default: 14:00)")
    parser.add_argument("--vision", default=None, help="Image directory or camera index/URL")
    parser.add_argument("--audio", default=None, help="Audio file path (for file mode)")
    parser.add_argument("--gesture", default=None, help="Gesture image/directory or camera index/URL")
    args = parser.parse_args()

    # Default vision source based on mode
    if args.vision is None:
        mode = os.getenv("VISION_SOURCE", "mock")
        if mode == "images":
            parser.error("VISION_SOURCE=images requires --vision <directory>")
        args.vision = "0" if mode == "camera" else "dock_cam_01.jpg"

    # Default audio source based on mode
    if args.audio is None:
        mode = os.getenv("AUDIO_SOURCE", "mock")
        if mode == "file":
            parser.error("AUDIO_SOURCE=file requires --audio <file.wav>")
        args.audio = "" if mode == "mic" else "dock_audio_01.wav"

    # Default gesture source based on mode
    if args.gesture is None:
        mode = os.getenv("GESTURE_SOURCE", "mock")
        if mode == "image":
            parser.error("GESTURE_SOURCE=image requires --gesture <path>")
        args.gesture = "0" if mode == "camera" else "gesture_cam_01.jpg"

    run_inspection(
        time=args.time,
        vision_source=args.vision,
        audio_source=args.audio,
        gesture_source=args.gesture,
    )


if __name__ == "__main__":
    main()
