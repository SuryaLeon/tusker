from config import (
    AVAILABILITY_FILE,
    HISTORY_FILE,
    INDIVIDUAL_WORKLOAD_WEIGHT,
    OUTPUT_FILE,
    PAIR_HISTORY_WEIGHT,
    POCS_FILE,
    SAME_TABLE_PAIR_WEIGHT,
    TASKS_FILE,
)

from reasoner import OllamaReasoner

from scheduler.exporter import export_schedule

from scheduler.loader import (
    load_availability,
    load_history,
    load_pocs,
    load_tasks,
)

from scheduler.scorer import ScoreWeights

from scheduler.scheduler import Scheduler


class SchedulerService:
    def __init__(self):
        self.reasoner = OllamaReasoner()

    def _build_scheduler(self):
        """
        Reload Excel files on every run.

        This ensures filesystem changes are reflected
        immediately.
        """

        pocs = load_pocs(
            POCS_FILE
        )

        tasks = load_tasks(
            TASKS_FILE
        )

        availability = load_availability(
            AVAILABILITY_FILE
        )

        history = load_history(
            HISTORY_FILE
        )

        weights = ScoreWeights(
            pair_history=(
                PAIR_HISTORY_WEIGHT
            ),
            individual_workload=(
                INDIVIDUAL_WORKLOAD_WEIGHT
            ),
            same_table_pair=(
                SAME_TABLE_PAIR_WEIGHT
            ),
        )

        return Scheduler(
            pocs=pocs,
            tasks=tasks,
            availability=availability,
            history=history,
            weights=weights,
        )

    def run(self):
        print(
            "\nScheduling triggered..."
        )

        scheduler = (
            self._build_scheduler()
        )

        (
            schedule_df,
            rankings_df,
        ) = scheduler.generate()

        (
            pair_statistics_df,
            poc_statistics_df,
        ) = scheduler.get_statistics()

        print(
            "Generating assignment explanations..."
        )

        reasons = []

        for _, row in (
            schedule_df.iterrows()
        ):
            assignment = row.to_dict()

            if (
                assignment["Status"]
                != "SCHEDULED"
            ):
                reasons.append(
                    "Assignment could not "
                    "be generated."
                )

                continue

            reason = (
                self.reasoner
                .explain_assignment(
                    assignment
                )
            )

            reasons.append(reason)

        schedule_df["Reason"] = reasons

        output = export_schedule(
            schedule_df=(
                schedule_df
            ),
            rankings_df=(
                rankings_df
            ),
            pair_statistics_df=(
                pair_statistics_df
            ),
            poc_statistics_df=(
                poc_statistics_df
            ),
            output_path=(
                OUTPUT_FILE
            ),
        )

        print(
            f"Schedule updated: {output}"
        )

        return schedule_df