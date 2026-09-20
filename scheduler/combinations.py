from itertools import combinations


def normalize_pair(poc1, poc2):
    """
    Always represent pairs in alphabetical order.

    Example:
        ("B", "A") -> ("A", "B")
    """

    return tuple(
        sorted(
            (
                str(poc1).strip(),
                str(poc2).strip(),
            )
        )
    )


def generate_pairs(pocs):
    """
    Generate every possible two-person combination.
    """

    unique_pocs = sorted(
        set(
            str(poc).strip()
            for poc in pocs
            if str(poc).strip()
        )
    )

    return list(combinations(unique_pocs, 2))


def filter_available_pairs(
    pairs,
    available_pocs,
):
    """
    Availability is a hard constraint.

    Candidate pairs are returned only when BOTH
    members are available.
    """

    available = set(available_pocs)

    return [
        pair
        for pair in pairs
        if pair[0] in available
        and pair[1] in available
    ]