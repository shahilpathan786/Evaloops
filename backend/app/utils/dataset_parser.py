
import csv
import io
import json


def parse_csv(content: bytes) -> list[dict]:
    """
    Parse CSV bytes into a list of dictionaries.
    """

    try:
        decoded_content = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise ValueError("CSV file must use UTF-8 encoding")

    reader = csv.DictReader(io.StringIO(decoded_content))

    if not reader.fieldnames:
        raise ValueError("CSV file is empty or has no header")

    required_fields = {"input"}
    available_fields = set(reader.fieldnames)

    if not required_fields.issubset(available_fields):
        raise ValueError("CSV must contain an 'input' column")

    records = []

    for row in reader:
        if not row.get("input") or not row["input"].strip():
            raise ValueError("CSV contains a record with missing input")

        records.append({
            "input": row["input"].strip(),
            "expected_output": (
                row.get("expected_output") or None
            ),
            "context": row.get("context") or None,
        })

    if not records:
        raise ValueError("CSV contains no dataset records")

    return records


def parse_json(content: bytes) -> list[dict]:
    """
    Parse JSON bytes into a list of dictionaries.
    """

    try:
        decoded_content = content.decode("utf-8-sig")
        data = json.loads(decoded_content)
    except UnicodeDecodeError:
        raise ValueError("JSON file must use UTF-8 encoding")
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON file")

    if not isinstance(data, list):
        raise ValueError("JSON must contain a list of records")

    if not data:
        raise ValueError("JSON contains no dataset records")

    records = []

    for item in data:
        if not isinstance(item, dict):
            raise ValueError("Each JSON record must be an object")

        records.append({
            "input": item.get("input"),
            "expected_output": item.get("expected_output"),
            "context": item.get("context"),
        })

    return records


def parse_dataset_file(
    filename: str,
    content: bytes
) -> list[dict]:
    """
    Detect file type and invoke the appropriate parser.
    """

    extension = filename.rsplit(".", 1)[-1].lower()

    if extension == "csv":
        return parse_csv(content)

    if extension == "json":
        return parse_json(content)

    raise ValueError("Only CSV and JSON files are supported")
