"""Reference implementation for task 06 (csv_stats). Used in _smoke calibration only."""
import csv
import io


def summarize_column(csv_text: str, column: str) -> dict:
    reader = csv.DictReader(io.StringIO(csv_text))
    if column not in (reader.fieldnames or []):
        raise KeyError(column)
    values = [float(row[column]) for row in reader if row[column].strip()]
    if len(values) == 0:
        raise ValueError(f"no data rows for column {column!r}")
    return {"min": min(values), "max": max(values), "mean": sum(values) / len(values)}
