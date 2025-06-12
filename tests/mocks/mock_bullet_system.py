from components import VelocityComponent, TransformComponent, HealthComponent
from entities import EntityType

class MockBulletSystem:
    def __init__(self):
        self.bullet_lifetime = 5.0  # seconds
        self.bullet_damage = 10

    def update(self, entities, dt):
        # Simulate bullet travel and lifetime
        for entity in entities:
            if getattr(entity, 'type', None) == EntityType.BULLET:
                transform = entity.get_component(TransformComponent)
                velocity = entity.get_component(VelocityComponent)
                
                if transform and velocity:
                    # Update position
                    transform.x += velocity.vx * dt
                    transform.y += velocity.vy * dt
                    
                    # Check for collisions with other entities
                    for other in entities:
                        if other != entity and hasattr(other, 'rect'):
                            if transform.rect.colliderect(other.rect):
                                # Apply damage if other entity has health
                                health = other.get_component(HealthComponent)
                                if health:
                                    health.current_health -= self.bullet_damage
                                # Remove bullet after hit
                                entity.mark_for_deletion = True
                                break
                    
                    # Remove bullet after lifetime
                    if hasattr(entity, 'age'):
                        entity.age += dt
                        if entity.age >= self.bullet_lifetime:
                            entity.mark_for_deletion = True 