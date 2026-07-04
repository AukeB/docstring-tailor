"""


Args:
    seed (int): Random seed used 
     to ensure deterministic generation.
    octaves (int): Number 
        of noise layers combined to 
                        produce detail
                 in             the
        output.
    persistence (float): 
        Controls amplitude reduction across octaves (typically 0–1).
    lacunarity (float):
        Controls frequency increase between successive octaves.


Raises:
    ValueError: If the provided 
     input is empty or cannot be
        parsed into a valid structure.
    TypeError: If the input
         type is not supported (e.g.,
        expecting str but received      list).
    RuntimeError: If an unexpected 
        failure occurs during
                    processing of the input data.


"""