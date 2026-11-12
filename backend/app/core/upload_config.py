
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5 MB
MAX_DATASET_RECORDS = 5000

ALLOWED_EXTENSIONS = {".csv", ".json"}

ALLOWED_CONTENT_TYPES = {
    ".csv": {
        "text/csv",
        "application/vnd.ms-excel",
        "application/csv",
    },
    ".json": {
        "application/json",
        "text/json",
    },
}

# inport ant
