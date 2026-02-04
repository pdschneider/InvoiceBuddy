# Interface/Windows/changelog.py
import logging
import customtkinter as ctk
if not hasattr(ctk, "CTkScrollableFrame"):
    logging.critical(f"CTkScrollableFrame missing.")
import Utils.fonts as fonts

def create_changelog(globals, changelog_tab):
       """
       Creates the tab to display setup instructions for new users.

              Parameters:
                     globals: Global variables
                     setup_tab: The main frame of the setup window
       """
       try:
            changelog_frame = ctk.CTkScrollableFrame(changelog_tab)
            changelog_frame.pack(fill="both", expand=True, padx=10, pady=20)
       except Exception as e:
            changelog_frame = ctk.CTkFrame(changelog_tab)
            changelog_frame.pack(fill="both", expand=True, padx=10, pady=20)
            logging.critical(f"Could not create scrollable frame: {e}. Using regular CTkFrame instead.")

       # Main Changelog Sections

       # v0.1.2
       ctk.CTkLabel(changelog_frame,
                     text="v0.1.2",
                     font=fonts.heading_font,
                     anchor="center").pack(fill="x", pady=20, padx=10)

       ctk.CTkLabel(changelog_frame,
                     justify="left",
                     anchor="center",
                     wraplength=400,
                     text = "- Switched some warning messageboxes to toasts\n" \
                              "- Icons now visible in spreadsheet settings\n" \
                              "- Changing the sheet name now changes its label\n" \
                              "- User can now select from a set of icons to represent sheets\n" \
                              "- New icons added\n" \
                              "- Updated logging with new sheet labels").pack(fill="both", expand=True, padx=10, pady=10)

       # v0.1.1
       ctk.CTkLabel(changelog_frame,
                     text="v0.1.1",
                     font=fonts.heading_font,
                     anchor="center").pack(fill="x", pady=20, padx=10)

       ctk.CTkLabel(changelog_frame,
                     justify="left",
                     anchor="center",
                     wraplength=400,
                     text = "- Switched to toast notifications for some messages\n" \
                              "- Fixed error when deleting files on network drive\n" \
                              "- Removed unnecessary two letter word from onboarding page\n" \
                              "- History path defaults to user-specific default path if not valid\n" \
                              "- Changed 'Moved' to 'Archived' in history for clarity\n" \
                              "- Added optional update for company map upon startup\n" \
                              "- App ignores non-.pdf changes in the inbox folder, avoiding unnecessary GUI rebuilds\n" \
                              "- Fixed error when buddy is named 'inbox'\n" \
                              "- Updated PSI to Summit Fire\n" \
                              "- Updated dependencies\n" \
                              "- General stability improvements").pack(fill="both", expand=True, padx=10, pady=10)

       # v0.1.0
       ctk.CTkLabel(changelog_frame,
                     text="v0.1.0",
                     font=fonts.heading_font,
                     anchor="center").pack(fill="x", pady=20, padx=10)

       ctk.CTkLabel(changelog_frame,
                     justify="left",
                     anchor="center",
                     wraplength=400,
                     text = "- Initial Release\n\n" \
                              " Recently fixed from pre-release:\n\n" \
                              "- Normalized button icons\n" \
                              "- Application runs through initial checks and cleans settings files if corrupted or missing values\n" \
                              "- Draws window in the center of the screen if saved screen dimensions are missing or 0\n" \
                              "- Removed broken regenerate workbook buttons and revert history button\n" \
                              "- Sanitized settings pages to eliminate saving nonconforming values\n" \
                              "- Silenced CTkImage warnings\n" \
                              "- Ensures all file opening or path selection can only choose working paths\n" \
                              "- Application automatically creates new folders if one doesn't exist when archiving\n" \
                              "- Added onboarding page for application start under empty or invalid path conditions\n" \
                              "- Added welcome document\n" \
                              "- Fixed workbook and inbox not opening on Windows").pack(fill="both", expand=True, padx=10, pady=10)

       # Buttons Frame
       buttons_frame = ctk.CTkFrame(changelog_tab, fg_color="transparent")
       buttons_frame.pack(fill="x", padx=10, pady=10)

       ctk.CTkButton(buttons_frame, 
                     text="Back", 
                     command= lambda: back_to_main_page()).pack(padx=5, pady=0)

       def back_to_main_page():
              """Forgets setup and settings pages to return the user to a clean chat page"""
              globals.changelog.pack_forget()
              globals.settings_page.pack(fill="both", expand=True, padx=10, pady=0)
              globals.title.configure(text="Settings")
