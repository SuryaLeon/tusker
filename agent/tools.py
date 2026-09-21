import json

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

from scheduler.exporter import (
    export_schedule,
)

from scheduler.loader import (
    load_availability,
    load_history,
    load_pocs,
    load_tasks,
)

from scheduler.scorer import (
    ScoreWeights,
)

from scheduler.scheduler import (
    Scheduler,
)


def build_scheduler():
    """
    Build a scheduler using the latest Excel data.

    Important:
    We load Excel files every time so changes made to
    availability/tasks are picked up without restarting
    the agent.
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
        pair_history=PAIR_HISTORY_WEIGHT,
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


def generate_schedule():
    """
    Generate and export a new schedule.
    """

    scheduler = build_scheduler()

    schedule_df, rankings_df = (
        scheduler.generate()
    )

    (
        pair_statistics_df,
        poc_statistics_df,
    ) = scheduler.get_statistics()

    export_schedule(
        schedule_df=schedule_df,
        rankings_df=rankings_df,
        pair_statistics_df=(
            pair_statistics_df
        ),
        poc_statistics_df=(
            poc_statistics_df
        ),
        output_path=OUTPUT_FILE,
    )

    return {
        "success": True,
        "output_file": str(
            OUTPUT_FILE
        ),
        "assignments": (
            schedule_df
            .fillna("")
            .to_dict(
                orient="records"
            )
        ),
    }


def get_poc_statistics():
    """
    Calculate current POC workload statistics.
    """

    scheduler = build_scheduler()

    scheduler.generate()

    _, poc_statistics_df = (
        scheduler.get_statistics()
    )

    return (
        poc_statistics_df
        .fillna("")
        .to_dict(
            orient="records"
        )
    )


def get_pair_statistics():
    """
    Return historical + proposed pair counts.
    """

    scheduler = build_scheduler()

    scheduler.generate()

    pair_statistics_df, _ = (
        scheduler.get_statistics()
    )

    return (
        pair_statistics_df
        .fillna("")
        .to_dict(
            orient="records"
        )
    )


def get_schedule():
    """
    Generate the schedule in memory and return it
    without exporting.
    """

    scheduler = build_scheduler()

    schedule_df, _ = (
        scheduler.generate()
    )

    return (
        schedule_df
        .fillna("")
        .to_dict(
            orient="records"
        )
    )


def get_candidate_rankings():
    """
    Return candidate ranking information for all tasks.
    """

    scheduler = build_scheduler()

    _, rankings_df = (
        scheduler.generate()
    )

    return (
        rankings_df
        .fillna("")
        .to_dict(
            orient="records"
        )
    )