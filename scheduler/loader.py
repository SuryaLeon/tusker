import pandas as pd


def load_pocs(filepath):
    """
    Returns only available POCs
    """

    df = pd.read_excel(filepath)

    available_pocs = (
        df[df["Available"].str.upper() == "Y"]
        ["POC"]
        .tolist()
    )

    return available_pocs


def load_tasks(filepath):

    return pd.read_excel(filepath)


def load_history(filepath):

    return pd.read_excel(filepath)