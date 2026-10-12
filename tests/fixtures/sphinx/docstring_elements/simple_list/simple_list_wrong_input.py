"""Lists the supported output formats.

- json: writes one object per record, serialised with the standard library encoder.
- csv: writes a header row followed by one row per record, with comma separators.
- parquet:  writes a columnar file that keeps the original column types.

1. Use json for interchange with other tools.
2. Use parquet for large datasets that are read repeatedly.
"""
