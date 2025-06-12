"""
EntityManager for ECS system
"""

from ecs.entity_audit import audit_components, audit_health_states

class EntityManager:
    def __init__(self):
        self.entities = {}  # dict: id -> entity

    def add_entity(self, entity):
        self.entities[entity.id] = entity
        print(f"[EntityManager] Entity {entity.id} added.")

    def remove_entity(self, entity_id):
        if entity_id in self.entities:
            del self.entities[entity_id]
            print(f"[EntityManager] Entity {entity_id} removed.")

    def get_entity(self, entity_id):
        return self.entities.get(entity_id, None)

    def get_all_entities(self):
        return list(self.entities.values())

    def get_entities_by_type(self, entity_type):
        """
        Return a list of all entities of the given type.
        """
        return [entity for entity in self.entities.values() if getattr(entity, 'type', None) == entity_type]

    def run_audits(self):
        all_entities = self.get_all_entities()
        audit_components(all_entities)
        audit_health_states(all_entities)

    def create_entity(self, entity_type, name=""):
        """
        Factory method to create and register a new entity.
        """
        from entities import Entity  # Local import to avoid circular dependency
        entity = Entity(entity_type, name)
        self.add_entity(entity)
        return entity 