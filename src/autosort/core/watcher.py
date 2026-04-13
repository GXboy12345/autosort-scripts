"""Real-time file watching using watchdog with FSEvents on macOS."""

from __future__ import annotations

import logging
import signal
import threading
import time
from pathlib import Path
from typing import Callable, Optional

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

logger = logging.getLogger(__name__)


class _DebouncedHandler(FileSystemEventHandler):
    """Collects file events and fires a batch callback after a debounce window."""

    def __init__(self, callback: Callable[[list[Path]], None], debounce: float = 1.0):
        super().__init__()
        self._callback = callback
        self._debounce = debounce
        self._pending: dict[str, float] = {}
        self._lock = threading.Lock()
        self._timer: Optional[threading.Timer] = None

    def on_created(self, event: FileSystemEvent):
        if event.is_directory:
            return
        self._enqueue(event.src_path)

    def on_moved(self, event: FileSystemEvent):
        if event.is_directory:
            return
        if hasattr(event, "dest_path"):
            self._enqueue(event.dest_path)

    def _enqueue(self, path: str):
        with self._lock:
            self._pending[path] = time.time()
            if self._timer is not None:
                self._timer.cancel()
            self._timer = threading.Timer(self._debounce, self._flush)
            self._timer.daemon = True
            self._timer.start()

    def _flush(self):
        with self._lock:
            paths = [Path(p) for p in self._pending if Path(p).is_file()]
            self._pending.clear()
        if paths:
            try:
                self._callback(paths)
            except Exception as e:
                logger.error(f"Watcher callback error: {e}")


class DirectoryWatcher:
    """Watches directories and triggers file organization on changes."""

    def __init__(
        self,
        paths: list[Path],
        on_files: Callable[[list[Path]], None],
        debounce: float = 1.0,
    ):
        self._paths = paths
        self._handler = _DebouncedHandler(on_files, debounce=debounce)
        self._observer = Observer()
        self._running = False

    def start(self) -> None:
        for p in self._paths:
            if p.is_dir():
                self._observer.schedule(self._handler, str(p), recursive=False)
                logger.info(f"Watching: {p}")
        self._observer.start()
        self._running = True

    def stop(self) -> None:
        if self._running:
            self._observer.stop()
            self._observer.join(timeout=5)
            self._running = False

    @property
    def is_running(self) -> bool:
        return self._running

    def run_forever(self) -> None:
        """Block until SIGINT/SIGTERM."""
        stop_event = threading.Event()

        def _handle_signal(signum, frame):
            stop_event.set()

        signal.signal(signal.SIGINT, _handle_signal)
        signal.signal(signal.SIGTERM, _handle_signal)

        self.start()
        try:
            stop_event.wait()
        finally:
            self.stop()
