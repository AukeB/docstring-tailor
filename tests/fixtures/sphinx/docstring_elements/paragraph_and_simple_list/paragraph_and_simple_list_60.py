"""Summarises the configured processing steps for the input
data. The steps run in this order:
- Loads the raw records from the configured source and
  validates each of them against the schema. Invalid records
  are skipped with a warning.
- Normalises the values so that every numeric field lies
  between zero and one.
- Removes duplicate records based on the identifier field.
- Writes the cleaned records to the configured output
  destination, one file per batch.
"""
