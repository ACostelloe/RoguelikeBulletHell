from entities import Entity

class MockEntityManager:
    def __init__(self):
        self.entities = {}

    def create_entity(self, entity_type):
        entity = Entity(entity_type)
        self.entities[entity.id] = entity
        return entity

    def get_entity(self, entity_id):
        return self.entities.get(entity_id)

    def remove_entity(self, entity_id):
        if entity_id in self.entities:
            del self.entities[entity_id]

    def get_all_entities(self):
        return list(self.entities.values())

    def run_audits(self):
        pass  # No-op for mocks 