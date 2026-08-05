from collections import defaultdict


def build_historical_stats(history_df):

    historical_counts = defaultdict(
        lambda: defaultdict(int)
    )

    for _, row in history_df.iterrows():

        task_table = str(row["TaskTable"]).strip()
        poc = str(row["POC"]).strip()

        historical_counts[task_table][poc] += 1

    return historical_counts


def initialize_current_stats():

    return defaultdict(
        lambda: defaultdict(int)
    )


def calculate_score(
        task_table,
        poc,
        historical_counts,
        current_counts):

    historical_score = historical_counts[task_table][poc]

    current_score = current_counts[task_table][poc]

    total_score = (
        historical_score
        +
        current_score
    )

    return total_score