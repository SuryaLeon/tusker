import pandas as pd
def load_pocs(file_path):
    df = pd.read_excel(file_path)
    available = (
        df[df["Available"].str.upper() == "Y"]["POC"]
        .tolist()
    )
    return available

def load_tasks(file_path):
    return pd.read_excel(file_path)

def load_history(file_path):
    return pd.read_excel(file_path)
