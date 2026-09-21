import threading
import time
from pathlib import Path

from watchdog.events import (
    FileSystemEventHandler,
)

from watchdog.observers import (
    Observer,
)

from config import (
    WATCH_DEBOUNCE_SECONDS,
    WATCH_DIRECTORY,
)

from scheduler.service import (
    SchedulerService,
)


WATCHED_FILES = {
    "pocs.xlsx",
    "tasks.xlsx",
    "availability.xlsx",
    "history.xlsx",
}


class ExcelChangeHandler(
    FileSystemEventHandler
):
    def __init__(
        self,
        scheduler_service,
    ):
        super().__init__()

        self.scheduler_service = (
            scheduler_service
        )

        self.timer = None
        self.lock = threading.Lock()

    def on_modified(
        self,
        event,
    ):
        self._handle_event(event)

    def on_created(
        self,
        event,
    ):
        self._handle_event(event)

    def on_moved(
        self,
        event,
    ):
        self._handle_event(event)

    def _handle_event(
        self,
        event,
    ):
        if event.is_directory:
            return

        path = Path(
            event.src_path
        )

        if path.name not in WATCHED_FILES:
            return

        print(
            f"Detected change: {path.name}"
        )

        self._debounce()

    def _debounce(self):
        with self.lock:
            if self.timer:
                self.timer.cancel()

            self.timer = threading.Timer(
                WATCH_DEBOUNCE_SECONDS,
                self._run_scheduler,
            )

            self.timer.start()

    def _run_scheduler(self):
        try:
            self.scheduler_service.run()

        except Exception as exc:
            print(
                "Scheduling run failed:"
            )

            print(exc)


def start_watcher():
    service = SchedulerService()

    handler = ExcelChangeHandler(
        service
    )

    observer = Observer()

    observer.schedule(
        handler,
        str(WATCH_DIRECTORY),
        recursive=False,
    )

    observer.start()

    print("=" * 60)

    print(
        "POC Scheduling Service"
    )

    print("=" * 60)

    print(
        f"Watching: "
        f"{WATCH_DIRECTORY}"
    )

    print(
        "Files:"
    )

    for filename in sorted(
        WATCHED_FILES
    ):
        print(
            f"  - {filename}"
        )

    print(
        "\nWaiting for Excel changes..."
    )

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print(
            "\nStopping scheduler..."
        )

        observer.stop()

    observer.join()