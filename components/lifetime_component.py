from dataclasses import dataclass

@dataclass
class LifetimeComponent:
    """Component for lifetime-related properties."""
    frames_left: int 