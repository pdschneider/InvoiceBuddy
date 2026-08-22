# src/utils/icons.py
from customtkinter import CTkImage
from PIL import Image
import logging
from src.utils.load_settings import load_data_path

def load_icons(globs):
    """Loads icons."""
    try:
        globs.add_icon = CTkImage(
            light_image=Image.open(load_data_path("config", "assets/add-2.png")),
            dark_image=Image.open(load_data_path("config", "assets/add-2.png")),
            size=(40, 40))

        globs.auto_icon = CTkImage(
            light_image=Image.open(load_data_path("config", "assets/auto.png")),
            dark_image=Image.open(load_data_path("config", "assets/auto.png")),
            size=(40, 40))

        globs.enter_icon = CTkImage(
            light_image=Image.open(load_data_path("config", "assets/pen-2.png")),
            dark_image=Image.open(load_data_path("config", "assets/pen-2.png")),
            size=(40, 40))

        globs.archive_icon = CTkImage(
            light_image=Image.open(load_data_path("config", "assets/archive.png")),
            dark_image=Image.open(load_data_path("config", "assets/archive.png")),
            size=(40, 40))

        globs.workbook_icon = CTkImage(
            light_image=Image.open(load_data_path("config", "assets/workbook-1.png")),
            dark_image=Image.open(load_data_path("config", "assets/workbook-1.png")),
            size=(40, 40))

        globs.inbox_folder_icon = CTkImage(
            light_image=Image.open(load_data_path("config", "assets/inbox-1.png")),
            dark_image=Image.open(load_data_path("config", "assets/inbox-1.png")),
            size=(40, 40))

        globs.delete_icon = CTkImage(
            light_image=Image.open(load_data_path("config", "assets/delete-4.png")),
            dark_image=Image.open(load_data_path("config", "assets/delete-4.png")),
            size=(40, 40))

        globs.send_icon = CTkImage(
            light_image=Image.open(load_data_path("config", "assets/send.png")),
            dark_image=Image.open(load_data_path("config", "assets/send.png")),
            size=(40, 40))

        globs.settings_icon = CTkImage(
            light_image=Image.open(load_data_path("config", "assets/settings.png")),
            dark_image=Image.open(load_data_path("config", "assets/settings.png")),
            size=(40, 40))

        globs.import_icon = CTkImage(
            light_image=Image.open(load_data_path("config", "assets/upload.png")),
            dark_image=Image.open(load_data_path("config", "assets/upload.png")),
            size=(40, 40))

        globs.export_icon = CTkImage(
            light_image=Image.open(load_data_path("config", "assets/download.png")),
            dark_image=Image.open(load_data_path("config", "assets/download.png")),
            size=(40, 40))

        globs.inbox_icon = CTkImage(
            light_image=Image.open(load_data_path("config", "assets/mail.png")),
            dark_image=Image.open(load_data_path("config", "assets/mail.png")),
            size=(40, 40))

        globs.invoice_icon = CTkImage(
            light_image=Image.open(load_data_path("config", globs.invoice_icon_path)),
            dark_image=Image.open(load_data_path("config", globs.invoice_icon_path)),
            size=(30, 30))

        globs.card_icon = CTkImage(
            light_image=Image.open(load_data_path("config", globs.card_icon_path)),
            dark_image=Image.open(load_data_path("config", globs.card_icon_path)),
            size=(30, 30))

        globs.po_icon = CTkImage(
            light_image=Image.open(load_data_path("config", globs.po_icon_path)),
            dark_image=Image.open(load_data_path("config", globs.po_icon_path)),
            size=(30, 30))

        globs.theme_icon = CTkImage(
            light_image=Image.open(load_data_path("config", "assets/theme.png")),
            dark_image=Image.open(load_data_path("config", "assets/theme.png")),
            size=(40, 40))

        globs.preferences_icon = CTkImage(
            light_image=Image.open(load_data_path("config", "assets/preferences.png")),
            dark_image=Image.open(load_data_path("config", "assets/preferences.png")),
            size=(40, 40))

        globs.note_icon = CTkImage(
            light_image=Image.open(load_data_path("config", "assets/note.png")),
            dark_image=Image.open(load_data_path("config", "assets/note.png")),
            size=(40, 40))

        globs.config_icon = CTkImage(
            light_image=Image.open(load_data_path("config", "assets/settings-2.png")),
            dark_image=Image.open(load_data_path("config", "assets/settings-2.png")),
            size=(40, 40))

        globs.garbage_icon = CTkImage(
            light_image=Image.open(load_data_path("config", "assets/delete-1.png")),
            dark_image=Image.open(load_data_path("config", "assets/delete-1.png")),
            size=(40, 40))

        globs.print_icon = CTkImage(
            light_image=Image.open(load_data_path("config", "assets/printer-1.png")),
            dark_image=Image.open(load_data_path("config", "assets/printer-1.png")),
            size=(40, 40))

        globs.printer_icon = CTkImage(
            light_image=Image.open(load_data_path("config", "assets/printer-2.png")),
            dark_image=Image.open(load_data_path("config", "assets/printer-2.png")),
            size=(40, 40))
        
        globs.notification_icon = CTkImage(
            light_image=Image.open(load_data_path("config", "assets/notification-1.png")),
            dark_image=Image.open(load_data_path("config", "assets/notification-1.png")),
            size=(40, 40))

        globs.windows_icon = CTkImage(
            light_image=Image.open(load_data_path("config", "assets/window-size.png")),
            dark_image=Image.open(load_data_path("config", "assets/window-size.png")),
            size=(40, 40))

    except Exception as e:
        logging.error(f"Failed to load icons due to: {e}")
