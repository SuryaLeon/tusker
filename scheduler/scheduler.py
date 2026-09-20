from collections import Counter, defaultdict

import pandas as pd

from .combinations import (
    filter_available_pairs,
    generate_pairs,
    normalize_pair,
)
from .scorer import (
    ScoreWeights,
    rank_pairs,
)


class Scheduler:
    def __init__(
        self,
        pocs,
        tasks,
        availability,
        history,
        weights=None,
    ):
        self.pocs = pocs.copy()
        self.tasks = tasks.copy()
        self.availability = availability.copy()
        self.history = history.copy()

        self.weights = weights or ScoreWeights()

        self.pair_counts = Counter()
        self.poc_counts = Counter()

        # Keeps track of assignments made during
        # the current scheduling run.
        self.table_pair_counts = defaultdict(Counter)

        self.schedule = []
        self.candidate_rankings = []

        self._initialize_history_counts()

    def _initialize_history_counts(self):
        """
        Build historical pair and individual POC counts.
        """

        if self.history.empty:
            return

        for _, row in self.history.iterrows():
            poc1 = str(row["POC1"]).strip()
            poc2 = str(row["POC2"]).strip()

            if not poc1 or not poc2:
                continue

            pair = normalize_pair(
                poc1,
                poc2,
            )

            self.pair_counts[pair] += 1

            self.poc_counts[poc1] += 1
            self.poc_counts[poc2] += 1

    def _get_active_pocs(self):
        """
        Return the active POCs configured in pocs.xlsx.
        """

        active = self.pocs[
            self.pocs["Active"] == True
        ]

        return sorted(
            active["POC"]
            .astype(str)
            .str.strip()
            .tolist()
        )

    def _get_available_pocs(
        self,
        task_date,
        active_pocs,
    ):
        """
        Return POCs available for a specific date.

        Conservative behavior:
        if no availability record exists for a POC/date,
        that person is treated as unavailable.

        This avoids silently scheduling somebody whose
        availability is unknown.
        """

        task_date = pd.Timestamp(
            task_date
        ).normalize()

        records = self.availability[
            self.availability["Date"]
            == task_date
        ]

        available_on_date = set(
            records[
                records["Available"] == True
            ]["POC"]
            .astype(str)
            .str.strip()
        )

        return sorted(
            set(active_pocs)
            & available_on_date
        )

    def _make_reason(
        self,
        selected,
        candidate_count,
    ):
        pair = selected["pair"]

        return (
            f"Selected {pair[0]}+{pair[1]} "
            f"from {candidate_count} valid pairs; "
            f"score={selected['score']}; "
            f"historical pair count="
            f"{selected['pair_history_count']}; "
            f"individual counts="
            f"{selected['poc1_assignment_count']}/"
            f"{selected['poc2_assignment_count']}; "
            f"same-table count="
            f"{selected['same_table_pair_count']}."
        )

    def _record_rankings(
        self,
        table_name,
        task_name,
        task_date,
        rankings,
    ):
        """
        Store all candidates, not only the winner.

        This is useful later for:
        - auditing
        - troubleshooting
        - AI explanations
        """

        for candidate in rankings:
            poc1, poc2 = candidate["pair"]

            self.candidate_rankings.append(
                {
                    "Table": table_name,
                    "Task": task_name,
                    "Date": task_date,
                    "Rank": candidate["rank"],
                    "POC1": poc1,
                    "POC2": poc2,
                    "Score": candidate["score"],
                    "HistoricalPairCount":
                        candidate[
                            "pair_history_count"
                        ],
                    "POC1AssignmentCount":
                        candidate[
                            "poc1_assignment_count"
                        ],
                    "POC2AssignmentCount":
                        candidate[
                            "poc2_assignment_count"
                        ],
                    "SameTablePairCount":
                        candidate[
                            "same_table_pair_count"
                        ],
                    "PairHistoryPenalty":
                        candidate[
                            "pair_history_penalty"
                        ],
                    "WorkloadPenalty":
                        candidate[
                            "workload_penalty"
                        ],
                    "SameTablePenalty":
                        candidate[
                            "same_table_penalty"
                        ],
                    "Selected":
                        candidate["rank"] == 1,
                }
            )

    def _update_counts(
        self,
        table_name,
        selected_pair,
    ):
        """
        Update statistics immediately.

        This means the current assignment influences
        the scoring of the next task.
        """

        poc1, poc2 = selected_pair

        self.pair_counts[selected_pair] += 1

        self.poc_counts[poc1] += 1
        self.poc_counts[poc2] += 1

        self.table_pair_counts[
            table_name
        ][selected_pair] += 1

    def generate(self):
        """
        Generate the full schedule.

        Returns:
            schedule_df
            rankings_df
        """

        active_pocs = self._get_active_pocs()

        if len(active_pocs) < 2:
            raise ValueError(
                "At least two active POCs are required."
            )

        all_pairs = generate_pairs(
            active_pocs
        )

        # Keep Excel row order when dates are equal.
        tasks = self.tasks.sort_values(
            by=["Date", "Table", "Task"],
            kind="stable",
        )

        for _, task in tasks.iterrows():
            table_name = str(
                task["Table"]
            ).strip()

            task_name = str(
                task["Task"]
            ).strip()

            task_date = pd.Timestamp(
                task["Date"]
            ).normalize()

            available_pocs = (
                self._get_available_pocs(
                    task_date,
                    active_pocs,
                )
            )

            available_pairs = (
                filter_available_pairs(
                    all_pairs,
                    available_pocs,
                )
            )

            if not available_pairs:
                self.schedule.append(
                    {
                        "Table": table_name,
                        "Task": task_name,
                        "Date": task_date,
                        "POC1": None,
                        "POC2": None,
                        "Score": None,
                        "Status": "UNASSIGNED",
                        "Reason":
                            "Fewer than two eligible "
                            "POCs are available.",
                    }
                )

                continue

            table_counts = (
                self.table_pair_counts[
                    table_name
                ]
            )

            rankings = rank_pairs(
                pairs=available_pairs,
                pair_counts=self.pair_counts,
                poc_counts=self.poc_counts,
                table_pair_counts=table_counts,
                weights=self.weights,
            )

            selected = rankings[0]

            self._record_rankings(
                table_name=table_name,
                task_name=task_name,
                task_date=task_date,
                rankings=rankings,
            )

            selected_pair = selected["pair"]

            reason = self._make_reason(
                selected,
                len(rankings),
            )

            self.schedule.append(
                {
                    "Table": table_name,
                    "Task": task_name,
                    "Date": task_date,
                    "POC1":
                        selected_pair[0],
                    "POC2":
                        selected_pair[1],
                    "Score":
                        selected["score"],
                    "Status":
                        "SCHEDULED",
                    "Reason":
                        reason,
                }
            )

            self._update_counts(
                table_name,
                selected_pair,
            )

        schedule_df = pd.DataFrame(
            self.schedule
        )

        rankings_df = pd.DataFrame(
            self.candidate_rankings
        )

        return (
            schedule_df,
            rankings_df,
        )

    def get_statistics(self):
        """
        Return final statistics after scheduling.

        Useful for fairness analysis.
        """

        pair_rows = []

        for pair, count in sorted(
            self.pair_counts.items()
        ):
            pair_rows.append(
                {
                    "POC1": pair[0],
                    "POC2": pair[1],
                    "AssignmentCount": count,
                }
            )

        poc_rows = []

        for poc, count in sorted(
            self.poc_counts.items()
        ):
            poc_rows.append(
                {
                    "POC": poc,
                    "AssignmentCount": count,
                }
            )

        return (
            pd.DataFrame(pair_rows),
            pd.DataFrame(poc_rows),
        )