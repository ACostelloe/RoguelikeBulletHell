from dataclasses import dataclass

class LootComponent:
    def __init__(self, entity, loot_table=None):
        self.entity = entity
        self.loot_table = loot_table or []

    def __repr__(self):
        return f"<LootComponent loot_table={self.loot_table}>" 