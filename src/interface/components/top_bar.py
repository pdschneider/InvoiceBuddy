# src/nterface/Components/top_bar.py
import customtkinter as ctk
from CTkToolTip import CTkToolTip


def create_top_bar(globs):
    """
    Creates the top bar for navigation.

        Parameters:
                globs: Global variables

        Returns:
                top_bar: The top_bar frame and its child widgets
    """
    def toggle_inbox():
        pages = [globs.settings_page, globs.onboarding_page, globs.changelog]
        for page in pages:
            page.pack_forget()
        globs.main_page.pack(fill="both", expand=True, padx=10, pady=0)
        globs.title.configure(text="Inbox")

    def toggle_settings():
        """Shows and hides the settings window when the button is clicked."""
        pages = [globs.onboarding_page, globs.main_page, globs.changelog]
        for page in pages:
            page.pack_forget()
        globs.settings_page.pack(fill="both", expand=True, padx=10, pady=0)
        globs.title.configure(text="Settings")

    # Main top bar
    top_bar = ctk.CTkFrame(globs.root, height=55, corner_radius=0)
    globs.top_bar = top_bar
    top_bar.pack(side="top", fill="x")
    top_bar.pack_propagate(False)

    # Inbox button (left)
    globs.inbox_button = ctk.CTkButton(
        top_bar,
        image=globs.inbox_icon,
        text=None,
        width=45,
        height=45)
    globs.inbox_button.pack(side="left", padx=10, pady=5)
    globs.inbox_button.configure(command=toggle_inbox)
    CTkToolTip(globs.inbox_button,
               message="Inbox",
               delay=0.6,
               follow=True,
               padx=10,
               pady=5)

    # Title / App name (center)
    title = ctk.CTkLabel(
        top_bar,
        text="",
        font=ctk.CTkFont(size=20, weight="bold"))
    globs.title = title
    globs.title.pack(side="left", expand=True)

    # Settings gear (right)
    globs.settings_button = ctk.CTkButton(
        top_bar,
        image=globs.settings_icon,
        text=None,
        width=45,
        height=45)
    globs.settings_button.pack(side="right", padx=10, pady=0)
    globs.settings_button.configure(command=toggle_settings)
    CTkToolTip(
        globs.settings_button,
        message="Settings",
        delay=0.6,
        follow=True,
        padx=10,
        pady=5)

    return top_bar
