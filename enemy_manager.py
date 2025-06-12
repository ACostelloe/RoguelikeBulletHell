from entities import EntityType
from components import TransformComponent, EnemyComponent, HealthComponent, CollisionComponent, StateComponent
from components import SpriteComponent

ENEMY_TEMPLATES = {
    "grunt": {"health": 50, "size": 32, "state": "patrol"},
    "flyer": {"health": 30, "size": 24, "state": "zigzag"},
    "tank": {"health": 150, "size": 48, "state": "patrol"},
    "boss": {"health": 500, "size": 64, "state": "boss_idle"}
}

class EnemyManager:
    def __init__(self, entity_manager=None):
        self.entity_manager = entity_manager

    def spawn_enemy(self, enemy_type, x, y):
        template = ENEMY_TEMPLATES.get(enemy_type, ENEMY_TEMPLATES["grunt"])
        entity = self.entity_manager.create_entity(EntityType.ENEMY)
        entity.add_component(TransformComponent(entity, x, y))
        entity.add_component(EnemyComponent(entity, enemy_type))
        entity.add_component(HealthComponent(entity, template["health"]))
        entity.add_component(CollisionComponent(entity, width=template["size"], height=template["size"]))
        entity.add_component(StateComponent(entity, template["state"]))
        entity.add_component(SpriteComponent(
            entity,
            image_key=f"enemy_{enemy_type}",  # Example: "enemy_grunt", "enemy_boss"
            frame=0
        ))
        self.entity_manager.add_entity(entity)
        return entity 