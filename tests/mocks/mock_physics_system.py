from components import VelocityComponent, TransformComponent, PhysicsComponent

class MockPhysicsSystem:
    def __init__(self):
        self.gravity = 9.8
        self.friction = 0.1

    def update(self, entities, dt):
        for entity in entities:
            velocity = entity.get_component(VelocityComponent)
            transform = entity.get_component(TransformComponent)
            physics = entity.get_component(PhysicsComponent)
            
            if velocity and transform:
                # Apply gravity if physics component exists
                if physics and physics.use_gravity:
                    velocity.vy += self.gravity * dt
                
                # Apply friction
                if abs(velocity.vx) > 0:
                    velocity.vx *= (1 - self.friction)
                if abs(velocity.vy) > 0:
                    velocity.vy *= (1 - self.friction)
                
                # Update position
                transform.x += velocity.vx * dt
                transform.y += velocity.vy * dt 