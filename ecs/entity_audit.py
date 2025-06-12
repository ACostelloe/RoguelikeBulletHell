"""
Entity audit utilities for ECS system — now fully decoupled from EntityManager.
"""

from components import HealthComponent

def audit_components(entities: list):
    """
    Audit that each entity has required components.
    """
    for entity in entities:
        missing = []
        if not entity.has_component("TransformComponent"):
            missing.append("TransformComponent")
        if not entity.has_component("SpriteComponent"):
            missing.append("SpriteComponent")
        if missing:
            print(f"[Audit] Entity {entity.id} missing components: {missing}")

def audit_health_states(entities: list):
    """
    Audit that HealthComponents have valid state.
    """
    for entity in entities:
        health = entity.get_component(HealthComponent)
        if health:
            if health.current_health < 0 or health.current_health > health.max_health:
                print(f"[Audit] Entity {entity.id} has invalid health state: {health.current_health}/{health.max_health}") 