# Utils/icons.py
from customtkinter import CTkImage
from PIL import Image
import logging
from src.utils.load_settings import load_data_path

def load_icons(globals):
    """Loads icons."""
    try:
        globals.add_icon = CTkImage(
            light_image=Image.open(load_data_path("config", "assets/add-2.png")),
            dark_image=Image.open(load_data_path("config", "assets/add-2.png")),
            size=(40, 40))

        globals.auto_icon = CTkImage(
            light_image=Image.open(load_data_path("config", "assets/auto.png")),
            dark_image=Image.open(load_data_path("config", "assets/auto.png")),
            size=(40, 40))

        globals.enter_icon = CTkImage(
            light_image=Image.open(load_data_path("config", "assets/pen-2.png")),
            dark_image=Image.open(load_data_path("config", "assets/pen-2.png")),
            size=(40, 40))

        globals.archive_icon = CTkImage(
            light_image=Image.open(load_data_path("config", "assets/archive.png")),
            dark_image=Image.open(load_data_path("config", "assets/archive.png")),
            size=(40, 40))

        globals.workbook_icon = CTkImage(
            light_image=Image.open(load_data_path("config", "assets/workbook-1.png")),
            dark_image=Image.open(load_data_path("config", "assets/workbook-1.png")),
            size=(40, 40))

        globals.inbox_folder_icon = CTkImage(
            light_image=Image.open(load_data_path("config", "assets/inbox-1.png")),
            dark_image=Image.open(load_data_path("config", "assets/inbox-1.png")),
            size=(40, 40))

        globals.delete_icon = CTkImage(
            light_image=Image.open(load_data_path("config", "assets/delete-4.png")),
            dark_image=Image.open(load_data_path("config", "assets/delete-4.png")),
            size=(40, 40))

        globals.send_icon = CTkImage(
            light_image=Image.open(load_data_path("config", "assets/send.png")),
            dark_image=Image.open(load_data_path("config", "assets/send.png")),
            size=(40, 40))

        globals.settings_icon = CTkImage(
            light_image=Image.open(load_data_path("config", "assets/settings.png")),
            dark_image=Image.open(load_data_path("config", "assets/settings.png")),
            size=(40, 40))

        globals.import_icon = CTkImage(
            light_image=Image.open(load_data_path("config", "assets/upload.png")),
            dark_image=Image.open(load_data_path("config", "assets/upload.png")),
            size=(40, 40))

        globals.export_icon = CTkImage(
            light_image=Image.open(load_data_path("config", "assets/download.png")),
            dark_image=Image.open(load_data_path("config", "assets/download.png")),
            size=(40, 40))

        globals.inbox_icon = CTkImage(
            light_image=Image.open(load_data_path("config", "assets/mail.png")),
            dark_image=Image.open(load_data_path("config", "assets/mail.png")),
            size=(40, 40))

        globals.invoice_icon = CTkImage(
            light_image=Image.open(load_data_path("config", globals.invoice_icon_path)),
            dark_image=Image.open(load_data_path("config", globals.invoice_icon_path)),
            size=(30, 30))

        globals.card_icon = CTkImage(
            light_image=Image.open(load_data_path("config", globals.card_icon_path)),
            dark_image=Image.open(load_data_path("config", globals.card_icon_path)),
            size=(30, 30))

        globals.po_icon = CTkImage(
            light_image=Image.open(load_data_path("config", globals.po_icon_path)),
            dark_image=Image.open(load_data_path("config", globals.po_icon_path)),
            size=(30, 30))

        globals.theme_icon = CTkImage(
            light_image=Image.open(load_data_path("config", "assets/theme.png")),
            dark_image=Image.open(load_data_path("config", "assets/theme.png")),
            size=(40, 40))

        globals.preferences_icon = CTkImage(
            light_image=Image.open(load_data_path("config", "assets/preferences.png")),
            dark_image=Image.open(load_data_path("config", "assets/preferences.png")),
            size=(40, 40))

        globals.note_icon = CTkImage(
            light_image=Image.open(load_data_path("config", "assets/note.png")),
            dark_image=Image.open(load_data_path("config", "assets/note.png")),
            size=(40, 40))

        globals.config_icon = CTkImage(
            light_image=Image.open(load_data_path("config", "assets/settings-2.png")),
            dark_image=Image.open(load_data_path("config", "assets/settings-2.png")),
            size=(40, 40))

        globals.garbage_icon = CTkImage(
            light_image=Image.open(load_data_path("config", "assets/delete-1.png")),
            dark_image=Image.open(load_data_path("config", "assets/delete-1.png")),
            size=(40, 40))

        globals.print_icon = CTkImage(
            light_image=Image.open(load_data_path("config", "assets/printer-1.png")),
            dark_image=Image.open(load_data_path("config", "assets/printer-1.png")),
            size=(40, 40))

        globals.printer_icon = CTkImage(
            light_image=Image.open(load_data_path("config", "assets/printer-2.png")),
            dark_image=Image.open(load_data_path("config", "assets/printer-2.png")),
            size=(40, 40))

    except Exception as e:
        logging.error(f"Failed to load icons due to: {e}")
