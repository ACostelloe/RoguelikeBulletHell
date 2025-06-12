"""
AI component for controlling entity behavior.
"""
from dataclasses import dataclass
from typing import Optional, List, Tuple, Dict, Any

@dataclass
class AIComponent:
    """Component for controlling AI behavior."""
    entity: Any  # Reference to the entity this component belongs to
    behavior: str = "idle"  # Current behavior state
    target: Optional[Any] = None  # Current target entity
    patrol_points: List[Tuple[float, float]] = None  # List of patrol points
    current_patrol_index: int = 0  # Current patrol point index
    detection_range: float = 100.0  # Range at which to detect targets
    attack_range: float = 50.0  # Range at which to attack
    attack_cooldown: float = 1.0  # Time between attacks
    last_attack_time: float = 0.0  # Last time an attack was performed
    state_data: Dict[str, Any] = None  # Additional state data for behaviors

    def __post_init__(self):
        """Initialize default values."""
        if self.patrol_points is None:
            self.patrol_points = []
        if self.state_data is None:
            self.state_data = {}

    def update_behavior(self, new_behavior: str):
        """Update the current behavior state."""
        self.behavior = new_behavior
        self.state_data.clear()  # Clear state data when changing behaviors

    def set_target(self, target: Any):
        """Set the current target entity."""
        self.target = target

    def clear_target(self):
        """Clear the current target."""
        self.target = None

    def add_patrol_point(self, x: float, y: float):
        """Add a patrol point."""
        self.patrol_points.append((x, y))

    def get_next_patrol_point(self) -> Optional[Tuple[float, float]]:
        """Get the next patrol point."""
        if not self.patrol_points:
            return None
        point = self.patrol_points[self.current_patrol_index]
        self.current_patrol_index = (self.current_patrol_index + 1) % len(self.patrol_points)
        return point

    def can_attack(self, current_time: float) -> bool:
        """Check if the entity can attack based on cooldown."""
        return current_time - self.last_attack_time >= self.attack_cooldown

    def record_attack(self, current_time: float):
        """Record that an attack was performed."""
        self.last_attack_time = current_time 