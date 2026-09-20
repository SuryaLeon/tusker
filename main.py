from pathlib import Path

from scheduler.exporter import export_schedule
from scheduler.loader import (
    load_availability,
    load_history,
    load_pocs,
    load_tasks,
)
from scheduler.scorer import ScoreWeights
from scheduler.scheduler import Scheduler


BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"


def main():
    print("Loading scheduling data...")

    pocs = load_pocs(
        DATA_DIR / "pocs.xlsx"
    )

    tasks = load_tasks(
        DATA_DIR / "tasks.xlsx"
    )

    availability = load_availability(
        DATA_DIR / "availability.xlsx"
    )

    history = load_history(
        DATA_DIR / "history.xlsx"
    )

    print(
        f"Loaded {len(pocs)} POCs"
    )

    print(
        f"Loaded {len(tasks)} tasks"
    )

    print(
        f"Loaded {len(availability)} "
        "availability records"
    )

    print(
        f"Loaded {len(history)} "
        "historical assignments"
    )

    weights = ScoreWeights(
        pair_history=10,
        individual_workload=2,
        same_table_pair=8,
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
        output_path=(
            OUTPUT_DIR
            / "schedule.xlsx"
        ),
    )

    print("\nGenerated schedule:")
    print(
        schedule_df.to_string(
            index=False
        )
    )

    print(
        f"\nSchedule written to:\n"
        f"{output_path}"
    )


if __name__ == "__main__":
    main()