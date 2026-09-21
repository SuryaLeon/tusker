import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")


def get_path(name: str, default: str) -> Path:
    value = os.getenv(name, default)

    path = Path(value)

    if not path.is_absolute():
        path = BASE_DIR / path

    return path


def get_bool(
    name: str,
    default: bool = False,
) -> bool:
    value = os.getenv(
        name,
        str(default),
    )

    return value.strip().lower() in {
        "true",
        "1",
        "yes",
        "y",
    }


# ----------------------------------------------------------
# Data
# ----------------------------------------------------------

POCS_FILE = get_path(
    "POCS_FILE",
    "data/pocs.xlsx",
)

TASKS_FILE = get_path(
    "TASKS_FILE",
    "data/tasks.xlsx",
)

AVAILABILITY_FILE = get_path(
    "AVAILABILITY_FILE",
    "data/availability.xlsx",
)

HISTORY_FILE = get_path(
    "HISTORY_FILE",
    "data/history.xlsx",
)

OUTPUT_FILE = get_path(
    "OUTPUT_FILE",
    "output/schedule.xlsx",
)


# ----------------------------------------------------------
# Scheduler
# ----------------------------------------------------------

PAIR_HISTORY_WEIGHT = int(
    os.getenv(
        "PAIR_HISTORY_WEIGHT",
        "10",
    )
)

INDIVIDUAL_WORKLOAD_WEIGHT = int(
    os.getenv(
        "INDIVIDUAL_WORKLOAD_WEIGHT",
        "2",
    )
)

SAME_TABLE_PAIR_WEIGHT = int(
    os.getenv(
        "SAME_TABLE_PAIR_WEIGHT",
        "8",
    )
)


# ----------------------------------------------------------
# Ollama
# ----------------------------------------------------------

OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434",
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "phi3:latest",
)

ENABLE_AI_REASONING = get_bool(
    "ENABLE_AI_REASONING",
    True,
)


# ----------------------------------------------------------
# File watcher
# ----------------------------------------------------------

WATCH_DIRECTORY = get_path(
    "WATCH_DIRECTORY",
    "data",
)

WATCH_DEBOUNCE_SECONDS = float(
    os.getenv(
        "WATCH_DEBOUNCE_SECONDS",
        "2",
    )
)