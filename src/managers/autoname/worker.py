# src.managers.autoname.worker
from PySide6.QtCore import QThread, Signal
from src.managers.autoname.pdfsearch import pdf_button


class AutoNameWorker(QThread):
    """Runs auto-naming off the GUI thread."""
    finished_run = Signal(int)  # number of files renamed

    def __init__(self, globs, directory, file_list, force):
        super().__init__()
        self.globs = globs
        self.directory = directory
        self.file_list = file_list
        self.force = force

    def run(self):
        changes, _dates = pdf_button(
            self.globs, directory=self.directory,
            file_list=self.file_list, force=self.force,
            show_dialogs=False)
        self.finished_run.emit(changes)
