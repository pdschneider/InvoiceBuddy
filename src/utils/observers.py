# Utils/observers.py
import time
import os
import platform
import ctypes
import logging
from watchdog.observers import Observer
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler

try:
    from PySide6.QtCore import QTimer, QObject, Signal
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False


if PYSIDE6_AVAILABLE:
    class _WatchdogSignaler(QObject):
        """Thread-safe bridge: emits signal from background thread, received in main thread."""
        file_changed = Signal()


class FolderEventHandler(FileSystemEventHandler):
    """Handles filesystem events for a single watched folder"""
    def __init__(self, globals, update_callback, debounce_delay=0.6):
        self.globals = globals
        self.update_callback = update_callback
        self.debounce_delay = debounce_delay
        self.last_event_time = 0
        self.scheduled_update = None

        # Qt mode: Set up thread-safe signaling
        if PYSIDE6_AVAILABLE and hasattr(globals, 'legacy_mode') and not globals.legacy_mode:
            self._signaler = _WatchdogSignaler()
            self._signaler.file_changed.connect(self._on_file_changed_qt)
            # Persistent timer that lives in the main thread
            self._debounce_timer = QTimer()
            self._debounce_timer.setSingleShot(True)
            self._debounce_timer.timeout.connect(self._trigger_update)

    def on_any_event(self, event):
        """Ignores directories and irrelevant event types."""
        # Only proceed upon specific events
        if event.is_directory or event.event_type not in ['created',
                                                          'deleted',
                                                          'modified',
                                                          'moved']:
            return

        # Only proceed if an event involves a pdf file
        if event.event_type == 'moved':
            if not (event.src_path.lower().endswith('.pdf') or
                    (event.dest_path and
                     event.dest_path.lower().endswith('.pdf'))):
                return
        elif not event.src_path.lower().endswith('.pdf'):
            return

        current_time = time.time()

        if PYSIDE6_AVAILABLE and hasattr(self.globals, 'legacy_mode') and not self.globals.legacy_mode:
            self._signaler.file_changed.emit()
        else:
            # Tkinter Mode: Cancel and reschedule
            if self.scheduled_update:
                self.globals.root.after_cancel(self.scheduled_update)
                self.scheduled_update = None

            delay_ms = int(self.debounce_delay * 1000)
            self.scheduled_update = self.globals.root.after(
                delay_ms, self._trigger_update)

        self.last_event_time = current_time

    def _on_file_changed_qt(self):
        """Runs in the MAIN thread when the signal is received. Handles debouncing."""
        # Calling start() on a running single-shot timer restarts it automatically
        delay_ms = int(self.debounce_delay * 1000)
        self._debounce_timer.start(delay_ms)

    def _trigger_update(self):
        self.scheduled_update = None
        self.update_callback()
        logging.debug(f"Watchdog: Folder change detected, updated counts.")


def is_network_drive(globals, path):
    """
    Check if a path is on a network drive (Windows only).
    Returns False on Linux.
    """
    if not platform.system().startswith("Windows"):
        return False
    drive, _ = os.path.splitdrive(path)
    if drive:
        drive_type = ctypes.windll.kernel32.GetDriveTypeW(drive + '\\')
        logging.debug(f"{path} is a network drive.")
        globals.network_drive = True
        return drive_type == 4  # DRIVE_REMOTE (network drive)
    return False


def setup_observer(globals, direct, key, callback=None):
    """Sets up watchdog observers."""
    directory = direct
    if not directory or not os.path.isdir(directory):
        logging.warning(
            f"Cannot setup observer for {key}: Invalid directory {directory}")
        return None
    if key in globals.observers and globals.observers[key] and globals.observers[key].is_alive():
        globals.observers[key].stop()
        globals.observers[key].join()

    if callback is None:
        if hasattr(globals, 'update_file_counts'):
            callback = globals.update_file_counts
        else:
            logging.warning("No callback provided and no globals.update_file_counts found.")
            return None

    handler = FolderEventHandler(globals, callback)
    if is_network_drive(globals, directory):
        observer = PollingObserver(timeout=1)
        logging.info(
            f"Using PollingObserver for network drive: {directory} (key: {key})")
    else:
        observer = Observer()
    observer.schedule(handler, directory, recursive=False)
    observer.start()
    return observer
