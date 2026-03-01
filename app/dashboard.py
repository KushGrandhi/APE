"""Streamlit dashboard for Chemical Warehouse Dock Inspection."""

import json
import os
from datetime import datetime
from pathlib import Path

import streamlit as st

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

st.set_page_config(page_title="Dock Inspection", layout="wide")

# ---------------------------------------------------------------------------
# Fixed config
# ---------------------------------------------------------------------------
time_slot = "14:00"
vision_source = os.getenv("VISION_IMAGE_DIR", "/Users/kush/Pictures/screenshots/test.png")
audio_source = "mic"
gesture_source = os.getenv("GESTURE_CAMERA_URL", "0")

os.environ.setdefault("VISION_SOURCE", "images")
os.environ.setdefault("AUDIO_SOURCE", "mic")
os.environ.setdefault("GESTURE_SOURCE", "camera")

# ---------------------------------------------------------------------------
# Session state defaults
# ---------------------------------------------------------------------------
defaults = {
    "vision_input": None,
    "vision_output": None,
    "audio_input": None,
    "audio_output": None,
    "inventory_output": None,
    "preliminary_output": None,
    "gesture_raw": None,
    "gesture_output": None,
    "final_output": None,
    "phase": None,
    "run_id": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ---------------------------------------------------------------------------
# Title + Start button
# ---------------------------------------------------------------------------
st.title("Chemical Warehouse Dock Inspection")
start = st.button("Start Inspection", type="primary", use_container_width=True)

if st.session_state.phase:
    st.caption(f"Run: `{st.session_state.run_id}` — Phase: **{st.session_state.phase}**")

# ---------------------------------------------------------------------------
# Static layout — always visible
# ---------------------------------------------------------------------------

# Row 1: Vision + Audio
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Vision Agent")
    with st.container(border=True):
        st.markdown("**Input**")
        if Path(vision_source).is_file():
            st.image(vision_source, use_container_width=True)
        else:
            st.caption(f"`{vision_source}`")
        if st.session_state.vision_input is not None:
            st.divider()
            st.markdown("**Output** — Agent analysis")
            try:
                st.json(json.loads(st.session_state.vision_output))
            except (json.JSONDecodeError, TypeError):
                st.code(st.session_state.vision_output or "", language="json")

with col2:
    st.markdown("### Audio Agent")
    with st.container(border=True):
        if st.session_state.audio_input is not None:
            st.markdown("**Input** — Raw transcription")
            st.text(st.session_state.audio_input)
            st.divider()
            st.markdown("**Output** — Agent analysis")
            try:
                st.json(json.loads(st.session_state.audio_output))
            except (json.JSONDecodeError, TypeError):
                st.code(st.session_state.audio_output or "", language="json")
        else:
            st.caption("Waiting for inspection...")

# Row 2: Inventory + Preliminary Report
col3, col4 = st.columns(2)

with col3:
    st.markdown("### Inventory Agent")
    with st.container(border=True):
        if st.session_state.inventory_output is not None:
            try:
                st.json(json.loads(st.session_state.inventory_output))
            except (json.JSONDecodeError, TypeError):
                st.code(st.session_state.inventory_output or "", language="json")
        else:
            st.caption("Waiting for inspection...")

with col4:
    st.markdown("### Preliminary Report")
    with st.container(border=True):
        if st.session_state.preliminary_output is not None:
            try:
                st.json(json.loads(st.session_state.preliminary_output))
            except (json.JSONDecodeError, TypeError):
                st.code(st.session_state.preliminary_output or "", language="json")
        else:
            st.caption("Waiting for inspection...")

# Row 3: Human Confirmation
st.divider()
st.subheader("Human Confirmation")
gcol1, gcol2 = st.columns(2)

with gcol1:
    st.markdown("### Gesture Agent")
    with st.container(border=True):
        if st.session_state.gesture_output is not None:
            st.markdown(f"**Raw:** {st.session_state.gesture_raw}")
            st.divider()
            try:
                st.json(json.loads(st.session_state.gesture_output))
            except (json.JSONDecodeError, TypeError):
                st.code(st.session_state.gesture_output or "", language="json")
        else:
            st.caption("Waiting for inspection...")

with gcol2:
    st.markdown("### Final Inspection Report")
    with st.container(border=True):
        if st.session_state.final_output is not None:
            try:
                report = json.loads(st.session_state.final_output)
                priority = report.get("priority", "unknown")
                priority_colors = {
                    "critical": "red",
                    "high": "orange",
                    "medium": "blue",
                    "low": "green",
                }
                color = priority_colors.get(priority, "gray")
                decision = report.get("final_decision", "unknown")
                st.markdown(
                    f"**Decision:** `{decision}` &nbsp; | &nbsp; "
                    f"**Priority:** :{color}[{priority.upper()}]"
                )
                st.json(report)
            except (json.JSONDecodeError, TypeError):
                st.code(st.session_state.final_output or "", language="json")
        else:
            st.caption("Waiting for inspection...")

# ---------------------------------------------------------------------------
# Run inspection when button is clicked
# ---------------------------------------------------------------------------
if start:
    vision_mode = os.getenv("VISION_SOURCE", "mock")
    gesture_mode = os.getenv("GESTURE_SOURCE", "mock")
    run_ts = datetime.now()
    run_id = run_ts.strftime("%Y%m%d_%H%M%S")
    st.session_state.run_id = run_id

    run_log: dict = {
        "run_id": run_id,
        "timestamp": run_ts.isoformat(),
        "config": {
            "time_slot": time_slot,
            "vision_source": vision_source,
            "audio_source": audio_source,
            "gesture_source": gesture_source,
            "vision_mode": vision_mode,
            "audio_mode": os.getenv("AUDIO_SOURCE", "mock"),
            "gesture_mode": gesture_mode,
        },
        "phases": {},
    }

    # === Phase 1: Collect sensor data ===
    st.session_state.phase = "1 — Collecting sensor data"
    with st.spinner("Phase 1 — Collecting sensor data..."):
        inventory_data = inventory_expectation(time_slot)
        vision_data = inventory_what_you_see(vision_source)
        audio_data = listen_what_to_expect(audio_source)

        run_log["phases"]["1_sensor_data"] = {
            "inventory_raw": inventory_data,
            "vision_raw": vision_data,
            "audio_raw": audio_data,
        }

    # === Phase 2: Specialist agents ===
    st.session_state.phase = "2 — Running specialist agents"
    with st.spinner("Phase 2 — Running specialist agents..."):
        inv_resp = inventory_agent.run(
            f"Analyze this expected inventory data for the {time_slot} delivery: {inventory_data}"
        )
        inventory_json = inv_resp.content

        if vision_mode == "mock":
            vis_resp = vision_agent.run(
                f"Analyze this dock camera observation: {vision_data}"
            )
            vision_json = vis_resp.content
        else:
            vision_json = vision_data

        aud_resp = audio_agent.run(
            f"A dock worker said the following about an incoming delivery. "
            f"Extract what packages are being delivered, quantities, and any hazard warnings:\n\n{audio_data}"
        )
        audio_json = aud_resp.content

        run_log["phases"]["2_agent_reports"] = {
            "inventory_agent": inventory_json,
            "vision_agent": vision_json,
            "audio_agent": audio_json,
        }

    # Store results so boxes update
    st.session_state.vision_input = vision_data
    st.session_state.vision_output = vision_json
    st.session_state.audio_input = audio_data
    st.session_state.audio_output = audio_json
    st.session_state.inventory_output = inventory_json

    # === Phase 3: Preliminary report ===
    st.session_state.phase = "3 — Preliminary report"
    with st.spinner("Phase 3 — Supervisor preliminary report..."):
        preliminary_prompt = f"""Produce a preliminary inspection report. Current timestamp: {run_ts.isoformat()}

INVENTORY AGENT REPORT (JSON):
{inventory_json}

VISION AGENT REPORT (JSON):
{vision_json}

AUDIO AGENT REPORT (JSON):
{audio_json}

Compare expected vs actual inventory. Flag any discrepancies. Recommend an action."""

        prelim_resp = preliminary_agent.run(preliminary_prompt)
        preliminary_json = prelim_resp.content
        run_log["phases"]["3_preliminary_report"] = preliminary_json

    st.session_state.preliminary_output = preliminary_json

    # === Phase 4: Gesture confirmation ===
    st.session_state.phase = "4 — Gesture confirmation"
    with st.spinner("Phase 4 — Awaiting gesture confirmation..."):
        gesture_data = see_what_human_has_to_say(gesture_source)

        if gesture_mode == "mock":
            gest_resp = gesture_agent.run(
                f"Analyze this gesture observation: {gesture_data}"
            )
            gesture_json = gest_resp.content
        else:
            gesture_json = gesture_data

        run_log["phases"]["4_gesture"] = {
            "gesture_raw": gesture_data,
            "gesture_agent": gesture_json,
        }

    st.session_state.gesture_raw = gesture_data
    st.session_state.gesture_output = gesture_json

    # === Phase 5: Final report ===
    st.session_state.phase = "5 — Finalizing report"
    with st.spinner("Phase 5 — Finalizing report..."):
        final_prompt = f"""Finalize this dock inspection report.

PRELIMINARY REPORT (JSON):
{preliminary_json}

HUMAN GESTURE CONFIRMATION (JSON):
{gesture_json}

Incorporate the human gesture and produce the final DockInspectionReport."""

        final_resp = final_agent.run(final_prompt)
        final_json = final_resp.content
        run_log["phases"]["5_final_report"] = final_json

    st.session_state.final_output = final_json
    st.session_state.phase = "Complete"

    # Save log
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / f"{run_id}.json"
    log_path.write_text(json.dumps(run_log, indent=2, default=str))

    st.rerun()
