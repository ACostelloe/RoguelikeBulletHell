from dataclasses import dataclass

@dataclass
class VelocityComponent:
    """Component for velocity-related properties."""
    entity: object
    vx: float = 0
    vy: float = 0

    def __repr__(self):
        return f"<Velocity vx={self.vx}, vy={self.vy}>" 