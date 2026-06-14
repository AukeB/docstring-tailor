"""Module for generating procedural terrain heightmaps using
fractional Brownian motion.

Implements a layered noise pipeline for producing tileable,
seeded heightmaps suitable for game world generation, fluid
simulation grids, and procedural texture synthesis. Each
octave of noise is summed with decreasing amplitude and
increasing frequency, producing the characteristic self
similar surface detail of natural terrain.

The core output is a 2D array of floats normalised to [0.0,
1.0], where 0.0 represents the lowest point and 1.0 the
highest. Downstream consumers can map this to elevation,
moisture, or any other scalar field.

To generate a heightmap and write it to disk as a PNG:

~~~
from terrain import HeightmapGenerator, export_png

generator = HeightmapGenerator(seed=42, octaves=6, persistence=0.5, lacunarity=2.0)
heightmap = generator.generate(width=512, height=512)
export_png(heightmap, output_path="terrain.png", colormap="viridis")
~~~

The seed guarantees deterministic output across runs. Two
generators with identical parameters and the same seed will
always produce the same heightmap, which is essential for
reproducible world generation in multiplayer or save-file
contexts.

You can also query individual sample points directly from
the REPL for quick inspection:

>>> from terrain import HeightmapGenerator
>>> generator = HeightmapGenerator(seed=42, octaves=4, persistence=0.5, lacunarity=2.0)
>>> heightmap = generator.generate(width=4, height=4)
>>> round(heightmap[0][0], 4)
0.3821
>>> round(heightmap[2][3], 4)
0.6174

Note:
    Increasing octaves beyond 8 yields diminishing visual
    returns and roughly doubles compute time per additional
    octave. For real-time applications, 4 to 6 octaves is
    the recommended range. Persistence controls how quickly
    amplitude fades per octave — values above 0.7 produce
    rough, jagged terrain, while values below 0.4 produce
    smooth, rolling hills. Lacunarity controls frequency
    growth per octave and should generally stay between 1.5
    and 3.0 for natural-looking results.
"""