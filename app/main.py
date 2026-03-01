"""Entry point for the Chemical Warehouse Dock Inspection system.

Flow:
1. Collect sensor data (inventory schedule, camera, audio)
2. Specialist agents analyze each data source
3. Supervisor produces preliminary report (expected vs received)
4. Present report to dock worker → collect gesture confirmation
5. Supervisor finalizes report incorporating human gesture
6. Log the full run to logs/
"""

import json
import os
from datetime import datetime
from pathlib import Path

from app.agents.audio_agent import audio_agent
from app.agents.gesture_agent import gesture_agent
from app.agents.inventory_agent import inventory_agent
from app.agents.vision_agent import vision_agent
from app.team.supervisor import final_agent, preliminary_agent
from app.tools.audio_tools import listen_what_to_expect
from app.tools.gesture_tools import see_what_human_has_to_say
from app.tools.inventory_tools import inventory_expectation
from app.tools.vision_tools import inventory_what_you_see

LOG_DIR = Path(os.getenv("LOG_DIR", "logs"))


def _agent_json(response) -> str:
    """Extract structured JSON string from an agent response."""
    return response.content


def _save_log(run_log: dict, run_id: str) -> Path:
    """Write the full run log to a JSON file."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / f"{run_id}.json"
    log_path.write_text(json.dumps(run_log, indent=2, default=str))
    return log_path


def run_inspection(
    time: str = "14:00",
    vision_source: str = "dock_cam_01.jpg",
    audio_source: str = "dock_audio_01.wav",
    gesture_source: str = "gesture_cam_01.jpg",
):
    """Run a full dock inspection by orchestrating all agents."""

    run_ts = datetime.now()
    run_id = run_ts.strftime("%Y%m%d_%H%M%S")

    run_log: dict = {
        "run_id": run_id,
        "timestamp": run_ts.isoformat(),
        "config": {
            "time_slot": time,
            "vision_source": vision_source,
            "audio_source": audio_source,
            "gesture_source": gesture_source,
            "vision_mode": os.getenv("VISION_SOURCE", "mock"),
            "audio_mode": os.getenv("AUDIO_SOURCE", "mock"),
            "gesture_mode": os.getenv("GESTURE_SOURCE", "mock"),
        },
        "phases": {},
    }

    print(f"\n{'='*60}")
    print(f"  DOCK INSPECTION - {time}  (run: {run_id})")
    print(f"{'='*60}\n")

    vision_mode = os.getenv("VISION_SOURCE", "mock")
    gesture_mode = os.getenv("GESTURE_SOURCE", "mock")

    # =================================================================
    # PHASE 1: Collect sensor data (inventory, vision, audio)
    # =================================================================
    print("[Phase 1] Collecting sensor data...\n")

    inventory_data = inventory_expectation(time)
    vision_data = inventory_what_you_see(vision_source)
    audio_data = listen_what_to_expect(audio_source)

    run_log["phases"]["1_sensor_data"] = {
        "inventory_raw": inventory_data,
        "vision_raw": vision_data,
        "audio_raw": audio_data,
    }

    print(f"  Inventory: {inventory_data}")
    print(f"  Vision:    {vision_data[:120]}...")
    print(f"  Audio:     {audio_data[:120]}...")
    print()

    # =================================================================
    # PHASE 2: Specialist agents analyze data
    # =================================================================
    print("[Phase 2] Running specialist agents...\n")

    inventory_response = inventory_agent.run(
        f"Analyze this expected inventory data for the {time} delivery: {inventory_data}"
    )
    inventory_json = _agent_json(inventory_response)
    print(f"--- Inventory Agent ---\n{inventory_json}\n")

    if vision_mode == "mock":
        vision_response = vision_agent.run(
            f"Analyze this dock camera observation: {vision_data}"
        )
        vision_json = _agent_json(vision_response)
    else:
        vision_json = vision_data
    print(f"--- Vision Agent ---\n{vision_json}\n")

    audio_response = audio_agent.run(
        f"A dock worker said the following about an incoming delivery. "
        f"Extract what packages are being delivered, quantities, and any hazard warnings:\n\n{audio_data}"
    )
    audio_json = _agent_json(audio_response)
    print(f"--- Audio Agent ---\n{audio_json}\n")

    run_log["phases"]["2_agent_reports"] = {
        "inventory_agent": inventory_json,
        "vision_agent": vision_json,
        "audio_agent": audio_json,
    }

    # =================================================================
    # PHASE 3: Supervisor produces preliminary report
    # =================================================================
    print("[Phase 3] Supervisor comparing expected vs received...\n")

    preliminary_prompt = f"""Produce a preliminary inspection report. Current timestamp: {run_ts.isoformat()}

INVENTORY AGENT REPORT (JSON):
{inventory_json}

VISION AGENT REPORT (JSON):
{vision_json}

AUDIO AGENT REPORT (JSON):
{audio_json}

Compare expected vs actual inventory. Flag any discrepancies. Recommend an action."""

    preliminary_response = preliminary_agent.run(preliminary_prompt)
    preliminary_json = _agent_json(preliminary_response)

    run_log["phases"]["3_preliminary_report"] = preliminary_json

    print(f"--- Preliminary Report ---\n{preliminary_json}\n")

    # =================================================================
    # PHASE 4: Collect human gesture confirmation
    # =================================================================
    print("[Phase 4] Awaiting dock worker confirmation...\n")

    gesture_data = see_what_human_has_to_say(gesture_source)
    print(f"  Gesture raw: {gesture_data[:120]}...")

    if gesture_mode == "mock":
        gesture_response = gesture_agent.run(
            f"Analyze this gesture observation: {gesture_data}"
        )
        gesture_json = _agent_json(gesture_response)
    else:
        gesture_json = gesture_data

    run_log["phases"]["4_gesture"] = {
        "gesture_raw": gesture_data,
        "gesture_agent": gesture_json,
    }

    print(f"\n--- Gesture Agent ---\n{gesture_json}\n")

    # =================================================================
    # PHASE 5: Supervisor finalizes report with human confirmation
    # =================================================================
    print("[Phase 5] Supervisor finalizing with human confirmation...\n")

    final_prompt = f"""Finalize this dock inspection report.

PRELIMINARY REPORT (JSON):
{preliminary_json}

HUMAN GESTURE CONFIRMATION (JSON):
{gesture_json}

Incorporate the human gesture and produce the final DockInspectionReport."""

    final_response = final_agent.run(final_prompt)

    run_log["phases"]["5_final_report"] = final_response.content

    print(f"--- FINAL INSPECTION REPORT ---")
    print(final_response.content)
    print()

    # =================================================================
    # Save log
    # =================================================================
    log_path = _save_log(run_log, run_id)
    print(f"[Log saved] {log_path}\n")

    return final_response


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
