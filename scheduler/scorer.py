from dataclasses import dataclass


@dataclass(frozen=True)
class ScoreWeights:
    """
    Central location for scheduler tuning.

    Larger number = stronger penalty.
    """

    pair_history: int = 10
    individual_workload: int = 2
    same_table_pair: int = 8


def calculate_pair_score(
    pair,
    pair_counts,
    poc_counts,
    table_pair_counts,
    weights=None,
):
    """
    Calculate the cost of assigning a pair.

    Lower scores are better.
    """

    if weights is None:
        weights = ScoreWeights()

    poc1, poc2 = pair

    pair_history_count = pair_counts.get(
        pair,
        0,
    )

    poc1_count = poc_counts.get(
        poc1,
        0,
    )

    poc2_count = poc_counts.get(
        poc2,
        0,
    )

    same_table_count = table_pair_counts.get(
        pair,
        0,
    )

    pair_history_penalty = (
        pair_history_count
        * weights.pair_history
    )

    workload_penalty = (
        poc1_count + poc2_count
    ) * weights.individual_workload

    same_table_penalty = (
        same_table_count
        * weights.same_table_pair
    )

    total_score = (
        pair_history_penalty
        + workload_penalty
        + same_table_penalty
    )

    return {
        "pair": pair,
        "score": total_score,
        "pair_history_count": pair_history_count,
        "poc1_assignment_count": poc1_count,
        "poc2_assignment_count": poc2_count,
        "same_table_pair_count": same_table_count,
        "pair_history_penalty": pair_history_penalty,
        "workload_penalty": workload_penalty,
        "same_table_penalty": same_table_penalty,
    }


def rank_pairs(
    pairs,
    pair_counts,
    poc_counts,
    table_pair_counts,
    weights=None,
):
    """
    Score every valid pair and rank lowest-to-highest.

    Pair name is included in sorting to guarantee
    deterministic results when scores are tied.
    """

    rankings = []

    for pair in pairs:
        result = calculate_pair_score(
            pair=pair,
            pair_counts=pair_counts,
            poc_counts=poc_counts,
            table_pair_counts=table_pair_counts,
            weights=weights,
        )

        rankings.append(result)

    rankings.sort(
        key=lambda item: (
            item["score"],
            item["pair"][0],
            item["pair"][1],
        )
    )

    # Assign human-readable ranking.
    for index, candidate in enumerate(
        rankings,
        start=1,
    ):
        candidate["rank"] = index

    return rankings