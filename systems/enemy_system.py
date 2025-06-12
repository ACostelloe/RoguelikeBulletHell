from components import TransformComponent, EnemyComponent, StateComponent
from entities import EntityType

class EnemySystem:
    def __init__(self, entity_manager):
        self.entity_manager = entity_manager

    def update(self, delta_time):
        for entity in self.entity_manager.get_entities_by_type(EntityType.ENEMY):
            transform = entity.get_component(TransformComponent)
            state = entity.get_component(StateComponent)

            if state.state == "patrol":
                transform.x += 20 * delta_time
            elif state.state == "zigzag":
                transform.x += 40 * delta_time
                transform.y += 20 * delta_time
            elif state.state == "boss_idle":
                pass  # boss logic will come later 