"""
>>> from terrain import HeightmapGenerator
>>> generator = HeightmapGenerator(seed=42, octaves=3)
>>> hm = generator.generate(width=3, height=3)
>>> round(hm[0][0], 4)
0.3819
>>> round(hm[1][1], 4)
0.5442

>>> from terrain import normalize_heightmap
>>> data = [[0.1, 0.5], [0.3, 0.9]]
>>> normalized = normalize_heightmap(data)
>>> normalized[0][1]
0.5
>>> normalized[1][1]
1.0

>>> from terrain import HeightmapGenerator
>>> generator = HeightmapGenerator(
...     seed=7,
...     octaves=2,
... )
>>> hm = generator.generate(width=2, height=2)
>>> hm[0][1]
0.6123
>>> hm[1][0]
0.4788
"""