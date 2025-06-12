class MockLootSystem:
    def drop_loot(self, entity):
        loot = entity.get_component("LootComponent")
        if loot:
            return loot.loot_table
        return [] 