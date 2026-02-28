"""Tool for processing voice commands from dock workers (placeholder with mock data)."""


def listen_what_to_expect(audio_path: str) -> str:
    """Process an audio recording from a dock worker describing the expected shipment.

    Args:
        audio_path: Path to the audio file to transcribe and process.

    Returns:
        Transcribed and interpreted voice instruction about the expected shipment.
    """
    # Placeholder: in production this would transcribe real audio
    return (
        "Dock worker said: 'We're expecting the HCL shipment today, "
        "should be 10 drums plus 5 bags of sodium hydroxide. "
        "All hazardous, make sure the labels are checked.'"
    )
