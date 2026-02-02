# Utils/observers.py
import time, os, platform, ctypes, logging
from watchdog.observers import Observer
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler

logging.getLogger('watchdog').setLevel(logging.WARNING)

class FolderEventHandler(FileSystemEventHandler):
    """Handles filesystem events for a single watched folder"""
    def __init__(self, globals, update_callback, debounce_delay=0.6):
        self.globals = globals
        self.update_callback = update_callback
        self.debounce_delay = debounce_delay
        self.last_event_time = 0
        self.scheduled_update = None

    def on_any_event(self, event):
        """Ignores directories and irrelevant event types."""
        if event.is_directory or event.event_type not in ['created', 'deleted', 'modified', 'moved']:
            return

        current_time = time.time()

        # Cancel any pending updates
        if self.scheduled_update:
            self.globals.root.after_cancel(self.scheduled_update)
            self.scheduled_update = None

        # Schedule new update (UI refresh + metadata save)
        self.scheduled_update = self.globals.root.after(
            int(self.debounce_delay * 1000),
            self._trigger_update)

        self.last_event_time = current_time

    def _trigger_update(self):
        self.scheduled_update = None
        self.update_callback()
        logging.debug(f"Watchdog: Folder change detected, updated counts.")

def is_network_drive(path):
    """Check if a path is on a network drive (Windows only). Returns False on Linux."""
    if platform.system() != 'Windows':
        return False
    drive, _ = os.path.splitdrive(path)
    if drive:
        drive_type = ctypes.windll.kernel32.GetDriveTypeW(drive + '\\')
        logging.debug(f"{path} is a network drive.")
        return drive_type == 4  # DRIVE_REMOTE (network drive)
    return False

def setup_observer(globals, direct, key):
    directory = direct
    if not directory or not os.path.isdir(directory):
        logging.warning(f"Cannot setup observer for {key}: Invalid directory {directory}")
        return None
    if key in globals.observers and globals.observers[key] and globals.observers[key].is_alive():
        globals.observers[key].stop()
        globals.observers[key].join()
    handler = FolderEventHandler(globals, globals.update_file_counts)
    if is_network_drive(directory):
        observer = PollingObserver(timeout=1)
        logging.info(f"Using PollingObserver for network drive: {directory} (key: {key})")
    else:
        observer = Observer()
    observer.schedule(handler, directory, recursive=False)
    observer.start()
    return observer
