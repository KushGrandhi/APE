"""Tool for analyzing camera images at the dock (placeholder with mock data)."""


def inventory_what_you_see(image_path: str) -> str:
    """Analyze a camera image of the dock to identify boxes, containers, and hazard symbols.

    Args:
        image_path: Path to the camera image to analyze.

    Returns:
        A description of what is visible at the dock including containers and hazard symbols.
    """
    # Placeholder: in production this would call a vision model on the actual image
    return (
        "Visible at dock: "
        "8x large drums labeled 'HCL' with Corrosive and Toxic hazard symbols, "
        "5x white bags labeled 'NaOH' with Corrosive hazard symbol, "
        "1x unmarked small box with no visible hazard labels."
    )
