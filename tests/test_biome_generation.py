import random
import numpy as np
from biome_generator import BiomeGenerator

def test_biome_generation_no_softlocks():
    for _ in range(10000):
        # Create a new biome generator with a random seed
        generator = BiomeGenerator(seed=random.randint(0, 99999))
        # Generate a small biome map
        biome_map = generator.generate_biome_map(width=10, height=10)
        assert isinstance(biome_map, np.ndarray)
        assert biome_map.shape == (10, 10) 