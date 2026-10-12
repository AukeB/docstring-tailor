"""Summarises the configured processing steps for the input data.
The steps run in this order:
- Loads the raw records from the configured source and validates each of them against the schema.
  Invalid records are skipped with a warning.
- Normalises the values so that every numeric field lies between zero and one.
1. Removes duplicate records based on the identifier field.
2. Writes the cleaned records to the configured output destination, one file per batch.
"""
