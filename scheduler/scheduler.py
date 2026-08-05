# scheduler/assignment_engine.py

from scheduler.scoring import calculate_score


def get_ranked_pocs(
    task_table,
    available_pocs,
    historical_counts,
    current_counts
):
    """
    Calculate and rank POCs for a specific task table.

    Lower score = preferred.
    """

    candidate_scores = []

    for poc in available_pocs:

        score = calculate_score(
            task_table=task_table,
            poc=poc,
            historical_counts=historical_counts,
            current_counts=current_counts
        )

        candidate_scores.append({
            "POC": poc,
            "Score": score,
            "HistoricalCount": historical_counts[task_table][poc],
            "CurrentCount": current_counts[task_table][poc]
        })

    candidate_scores.sort(
        key=lambda x: (
            x["Score"],
            x["HistoricalCount"],
            x["CurrentCount"],
            x["POC"]
        )
    )

    return candidate_scores


def select_pocs(
    ranked_pocs,
    required_pocs=2
):
    """
    Select required number of unique POCs.

    Example:
        required_pocs = 2
        returns [A, B]
    """

    selected = []

    for candidate in ranked_pocs:

        if candidate["POC"] not in selected:
            selected.append(candidate["POC"])

        if len(selected) >= required_pocs:
            break

    return selected


def update_counts(
    task_table,
    assigned_pocs,
    current_counts
):
    """
    Update in-memory counters after each assignment.
    """

    for poc in assigned_pocs:
        current_counts[task_table][poc] += 1


def create_assignment_record(
    task_table,
    task_id,
    assigned_pocs,
    ranked_pocs
):
    """
    Create output row.
    """

    assignment = {
        "TaskTable": task_table,
        "TaskID": task_id,
        "POC1": assigned_pocs[0] if len(assigned_pocs) > 0 else None,
        "PO