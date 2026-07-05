"""



Example:




    >>> from terrain import HeightmapGenerator
    >>> generator = HeightmapGenerator(
    ...     seed=42,
    ...     octaves=4,
    ...     persistence=0.5,
    ...     lacunarity=2.0,
    ... )
    >>> width, height = 4, 4
    >>> heightmap = generator.generate(
    ...     width=width,
    ...     height=height
    ... )
    >>> round(heightmap[0][0], 4)
    0.3821
    >>> round(heightmap[2][3], 4)
    0.6174
    >>> # verify deterministic structure
    >>> all(len(row) == width for row in heightmap)
    True
    >>> # inspect a small slice
    >>> [round(v, 3) for v in heightmap[1]]
    [0.45, 0.512, 0.589, 0.601]



    
"""