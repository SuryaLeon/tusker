from scheduler.loader import (
    load_pocs,
    load_tasks,
    load_history
)

from scheduler.scoring import (
    build_historical_stats,
    initialize_current_stats
)

from scheduler.assignment_engine import (
    assign_tasks
)

from scheduler.exporter import (
    export_schedule
)


def main():

    POC_FILE = "data/pocs.xlsx"
    TASK_FILE = "data/tasks.xlsx"
    HISTORY_FILE = "data/history.xlsx"

    print("Loading files...")

    available_pocs = load_pocs(POC_FILE)

    tasks_df = load_tasks(TASK_FILE)

    history_df = load_history(HISTORY_FILE)

    print(
        f"Available POCs: {len(available_pocs)}"
    )

    historical_counts = build_historical_stats(
        history_df
    )

    current_counts = initialize_current_stats()

    print("Generating schedule...")

    assignments = assign_tasks(
        tasks_df=tasks_df,
        available_pocs=available_pocs,
        historical_counts=historical_counts,
        current_counts=current_counts
    )

    result = export_schedule(
        assignments,
        "schedule.xlsx"
    )

    print("\nGenerated Schedule\n")
    print(result)

    print(
        "\nSchedule exported to schedule.xlsx"
    )


if __name__ == "__main__":
    main()