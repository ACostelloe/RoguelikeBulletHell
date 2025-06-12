from components import AIComponent, TransformComponent, VelocityComponent
from entities import EntityType

class MockAISystem:
    def __init__(self):
        self.behavior_states = {
            "idle": self._update_idle,
            "patrol": self._update_patrol,
            "chase": self._update_chase,
            "attack": self._update_attack
        }
        self.patrol_points = []
        self.current_patrol_index = 0

    def update(self, entities, dt):
        for entity in entities:
            ai = entity.get_component(AIComponent)
            if ai:
                # Get current behavior state
                behavior = getattr(ai, 'behavior', 'idle')
                if behavior in self.behavior_states:
                    self.behavior_states[behavior](entity, dt)

    def _update_idle(self, entity, dt):
        # Simple idle behavior - just stand still
        velocity = entity.get_component(VelocityComponent)
        if velocity:
            velocity.vx = 0
            velocity.vy = 0

    def _update_patrol(self, entity, dt):
        # Simple patrol behavior - move between points
        transform = entity.get_component(TransformComponent)
        velocity = entity.get_component(VelocityComponent)
        if transform and velocity and self.patrol_points:
            target = self.patrol_points[self.current_patrol_index]
            dx = target[0] - transform.x
            dy = target[1] - transform.y
            dist = (dx * dx + dy * dy) ** 0.5
            
            if dist < 5:  # Reached patrol point
                self.current_patrol_index = (self.current_patrol_index + 1) % len(self.patrol_points)
            else:
                velocity.vx = dx / dist * 2
                velocity.vy = dy / dist * 2

    def _update_chase(self, entity, dt):
        # Simple chase behavior - move towards player
        transform = entity.get_component(TransformComponent)
        velocity = entity.get_component(VelocityComponent)
        if transform and velocity:
            # Find player entity
            player = None
            for other in entity.world.entities:
                if other.type == EntityType.PLAYER:
                    player = other
                    break
            
            if player:
                player_transform = player.get_component(TransformComponent)
                if player_transform:
                    dx = player_transform.x - transform.x
                    dy = player_transform.y - transform.y
                    dist = (dx * dx + dy * dy) ** 0.5
                    if dist > 0:
                        velocity.vx = dx / dist * 3
                        velocity.vy = dy / dist * 3

    def _update_attack(self, entity, dt):
        # Simple attack behavior - stop and attack
        velocity = entity.get_component(VelocityComponent)
        if velocity:
            velocity.vx = 0
            velocity.vy = 0
            # Attack logic would go here 