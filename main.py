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

from scheduler.exporter import export_schedule
from scheduler.loader import (
    load_availability,
    load_history,
    load_pocs,
    load_tasks,
)
from scheduler.scorer import ScoreWeights
from scheduler.scheduler import Scheduler


def main():
    print("POC Scheduler")
    print("=" * 50)

    print("\nLoading scheduling data...")

    pocs = load_pocs(POCS_FILE)
    tasks = load_tasks(TASKS_FILE)

    availability = load_availability(
        AVAILABILITY_FILE
    )

    history = load_history(
        HISTORY_FILE
    )

    print(f"POCs             : {len(pocs)}")
    print(f"Tasks            : {len(tasks)}")
    print(
        f"Availability rows: {len(availability)}"
    )
    print(
        f"History rows     : {len(history)}"
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

    print("\nScheduler weights:")
    print(
        f"  Pair history       : "
        f"{weights.pair_history}"
    )
    print(
        f"  Individual workload: "
        f"{weights.individual_workload}"
    )
    print(
        f"  Same table pair    : "
        f"{weights.same_table_pair}"
    )

    scheduler = Scheduler(
        pocs=pocs,
        tasks=tasks,
        availability=availability,
        history=history,
        weights=weights,
    )

    print("\nGenerating schedule...")

    schedule_df, rankings_df = (
        scheduler.generate()
    )

    (
        pair_statistics_df,
        poc_statistics_df,
    ) = scheduler.get_statistics()

    output_path = export_schedule(
        schedule_df=schedule_df,
        rankings_df=rankings_df,
        pair_statistics_df=pair_statistics_df,
        poc_statistics_df=poc_statistics_df,
        output_path=OUTPUT_FILE,
    )

    print("\nGenerated schedule:")
    print(
        schedule_df.to_string(
            index=False
        )
    )

    print("\n" + "=" * 50)
    print("Scheduling completed.")
    print(f"Output: {output_path}")


if __name__ == "__main__":
    main()