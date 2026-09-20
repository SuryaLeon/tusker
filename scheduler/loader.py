from pathlib import Path

import pandas as pd


REQUIRED_POC_COLUMNS = {
    "POC",
    "Active",
}

REQUIRED_TASK_COLUMNS = {
    "Table",
    "Task",
    "Date",
}

REQUIRED_AVAILABILITY_COLUMNS = {
    "POC",
    "Date",
    "Available",
}

REQUIRED_HISTORY_COLUMNS = {
    "Table",
    "Task",
    "Date",
    "POC1",
    "POC2",
    "Status",
}


def _validate_columns(df, required_columns, filename):
    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(
            f"{filename} is missing required columns: "
            f"{sorted(missing)}"
        )


def _convert_to_bool(value):
    """
    Convert common Excel representations into Python bool values.
    """

    if isinstance(value, bool):
        return value

    if pd.isna(value):
        return False

    value = str(value).strip().lower()

    return value in {
        "true",
        "yes",
        "y",
        "1",
        "available",
        "active",
    }


def load_pocs(path):
    path = Path(path)

    df = pd.read_excel(
        path,
        sheet_name="POCs",
        engine="openpyxl",
    )

    _validate_columns(
        df,
        REQUIRED_POC_COLUMNS,
        path.name,
    )

    df["POC"] = df["POC"].astype(str).str.strip()
    df["Active"] = df["Active"].apply(_convert_to_bool)

    # Remove blank/invalid values.
    df = df[
        df["POC"].notna()
        & (df["POC"] != "")
    ].copy()

    return df


def load_tasks(path):
    path = Path(path)

    df = pd.read_excel(
        path,
        sheet_name="Tasks",
        engine="openpyxl",
    )

    _validate_columns(
        df,
        REQUIRED_TASK_COLUMNS,
        path.name,
    )

    df["Table"] = df["Table"].astype(str).str.strip()
    df["Task"] = df["Task"].astype(str).str.strip()

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="raise",
    ).dt.normalize()

    return df


def load_availability(path):
    path = Path(path)

    df = pd.read_excel(
        path,
        sheet_name="Availability",
        engine="openpyxl",
    )

    _validate_columns(
        df,
        REQUIRED_AVAILABILITY_COLUMNS,
        path.name,
    )

    df["POC"] = df["POC"].astype(str).str.strip()

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="raise",
    ).dt.normalize()

    df["Available"] = df["Available"].apply(
        _convert_to_bool
    )

    return df


def load_history(path):
    path = Path(path)

    # History is allowed to be missing during the very first run.
    if not path.exists():
        return pd.DataFrame(
            columns=sorted(REQUIRED_HISTORY_COLUMNS)
        )

    df = pd.read_excel(
        path,
        sheet_name="History",
        engine="openpyxl",
    )

    _validate_columns(
        df,
        REQUIRED_HISTORY_COLUMNS,
        path.name,
    )

    df["Table"] = df["Table"].astype(str).str.strip()
    df["Task"] = df["Task"].astype(str).str.strip()
    df["POC1"] = df["POC1"].astype(str).str.strip()
    df["POC2"] = df["POC2"].astype(str).str.strip()
    df["Status"] = df["Status"].astype(str).str.strip()

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="raise",
    ).dt.normalize()

    return df