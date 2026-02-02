# Interface/Settings/paths_settings.py
import customtkinter as ctk
import tkinter as tk
from Interface.Components.gui_actions import browse_directory, browse_file
from Utils.save_settings import save_all_settings
import Utils.fonts as fonts

def create_paths_settings_tab(globals, settings_tab):
    """
    Create the Settings tab for configuring paths and advanced settings.

    Args:
        globals (globals): The global configuration object containing UI variables and settings.
    """

    # Title Frame
    title_frame = ctk.CTkFrame(settings_tab, fg_color="transparent")
    title_frame.pack(fill="x", pady=0, padx=0)

    ctk.CTkLabel(title_frame, 
                 font=fonts.title_font,
                 text="Paths").pack(pady=20, fill="x", anchor="center", padx=10)

    # Paths Frame
    paths_section = ctk.CTkFrame(settings_tab, fg_color="transparent")
    paths_section.pack(fill="x", pady=0, padx=0)
    paths_section.grid_columnconfigure(1, weight=1)

    # Workbook
    ctk.CTkLabel(paths_section, 
                 font=fonts.heading_font,
                 text="Workbook:").grid(row=0, column=0, padx=(20, 10), sticky="w")

    ctk.CTkEntry(paths_section, 
             textvariable=globals.workbook_var).grid(row=0, column=1, padx=(0, 10), sticky="ew")

    ctk.CTkButton(paths_section, 
               text="Browse", 
               width=140,
               command=lambda: browse_file(globals.workbook_var)).grid(row=0, column=2, pady=5)
    
    # Inbox
    ctk.CTkLabel(paths_section,
                 font=fonts.heading_font, 
                 text="Inbox:").grid(row=1, column=0, padx=(20, 10), sticky="w")

    ctk.CTkEntry(paths_section, 
             textvariable=globals.inbox_dir_var).grid(row=1, column=1, padx=(0, 10), sticky="ew")

    ctk.CTkButton(paths_section, 
               text="Browse", 
               width=140,
               command=lambda: [browse_directory(globals.inbox_dir_var), globals.update_file_counts()]).grid(row=1, column=2, pady=5)

    # Archive
    ctk.CTkLabel(paths_section,
                 font=fonts.heading_font, 
                 text="Archive:").grid(row=2, column=0, padx=(20, 10), sticky="w")

    ctk.CTkEntry(paths_section, 
             textvariable=globals.archive_path_var).grid(row=2, column=1, padx=(0, 10), sticky="ew")

    ctk.CTkButton(paths_section, 
               text="Browse", 
               width=140,
               command=lambda: [browse_directory(globals.archive_path_var)]).grid(row=2, column=2, pady=5)

    def add_buddy():
        if len(globals.buddy_pairs) >= globals.max_buddies: return
        name_var = tk.StringVar(value=f"Buddy {len(globals.buddy_entries) + 1}")
        path_var = tk.StringVar()

        buddy_subframe = ctk.CTkFrame(buddies_frame)
        buddy_subframe.pack(fill="x", pady=5)
        buddy_subframe.grid_columnconfigure(1, weight=1)

        ctk.CTkEntry(buddy_subframe, textvariable=name_var, placeholder_text="Buddy", width=90).grid(row=0, column=0, padx=20)
        ctk.CTkEntry(buddy_subframe, textvariable=path_var).grid(row=0, column=1, pady=0, sticky="ew")
        ctk.CTkButton(buddy_subframe, width=105, text="Browse", command=lambda: browse_directory(path_var)).grid(row=0, column=2, pady=0, padx=5)
        ctk.CTkButton(buddy_subframe, text="-", width=30,
                    command=lambda f=buddy_subframe: remove_buddy(f)).grid(row=0, column=3, pady=0)

        globals.buddy_frames.append(buddy_subframe)
        globals.buddy_entries.append({"frame": buddy_subframe,
                                "name_var": name_var,
                                "path_var": path_var})
        
        add_button.pack_forget()
        add_button.pack(pady=0, padx=0)

        if len(globals.buddy_entries) >= globals.max_buddies:
            add_button.pack_forget()

    def remove_buddy(frame):
        # Find and remove from buddy_entries (our UI list)
        for entry in globals.buddy_entries[:]:
            if entry["frame"] == frame:
                frame.destroy()
                globals.buddy_entries.remove(entry)
                break

        # Show + button again if space
        if len(globals.buddy_entries) < globals.max_buddies:
            add_button.pack(pady=0, padx=0)

    def populate_buddies():
        """
        Add up to three buddy rows for the first non‑inbox sources.
        Must be called after `buddies_frame` exists.
        """
        # Grab the first three source entries that aren't the inbox
        candidates = [(k, v) for k, v in globals.buddies.items() if k != "inbox"][:3]

        for name, path in candidates:
            # Stop if we already hit the max allowed buddies
            if len(globals.buddy_pairs) >= globals.max_buddies:
                break
            # Create a new UI row (adds StringVars to globals.buddy_pairs)
            add_buddy()
            # The newest entry is the last in buddy_entries
            latest_entry = globals.buddy_entries[-1]
            latest_entry["name_var"].set(name)
            latest_entry["path_var"].set(path)
    
    # Buddies Title Frame
    buddies_title_frame = ctk.CTkFrame(settings_tab, fg_color="transparent")
    buddies_title_frame.pack(fill="x", pady=0, padx=0)
    buddies_title_frame.grid_columnconfigure(1, weight=1)

    add_label = ctk.CTkLabel(buddies_title_frame,
                 font=fonts.heading_font,
                 text="Buddies")
    add_label.grid(row=0, column=1, pady=5)

    # Buddies Frame
    buddies_frame = ctk.CTkFrame(settings_tab, fg_color="transparent")
    buddies_frame.pack(fill="x", pady=0, padx=0)
    buddies_frame.grid_columnconfigure(1, weight=1)
    
    add_button = ctk.CTkButton(buddies_frame,
                  text="+",
                  width=30,
                  command=add_buddy)
    add_button.pack(pady=0, padx=0)

    populate_buddies()

    # Advanced Title Frame
    advanced_title_frame = ctk.CTkFrame(settings_tab, fg_color="transparent")
    advanced_title_frame.pack(fill="x", pady=0, padx=0)
    advanced_title_frame.grid_columnconfigure(1, weight=1)

    add_label = ctk.CTkLabel(advanced_title_frame,
                 font=fonts.heading_font,
                 text="Advanced")
    add_label.pack(pady=5)

    # Advanced Paths Frame
    advanced_frame = ctk.CTkFrame(settings_tab, fg_color="transparent")
    advanced_frame.pack(fill="x", pady=0, padx=0)
    advanced_frame.grid_columnconfigure(1, weight=1)

    # History
    ctk.CTkLabel(advanced_frame, 
                 font=fonts.heading_font,
                 text="History:").grid(row=0, column=0, padx=(20, 10), sticky="w")

    ctk.CTkEntry(advanced_frame, 
             textvariable=globals.history_var).grid(row=0, column=1, padx=(0, 10), sticky="ew")

    ctk.CTkButton(advanced_frame, 
               text="Browse", 
               width=140,
               command=lambda: browse_file(globals.history_var)).grid(row=0, column=2, pady=5)

    # Save Button Frame
    save_button_frame = ctk.CTkFrame(settings_tab, fg_color="transparent")
    save_button_frame.pack(pady=10)

    ctk.CTkButton(save_button_frame, 
               text="Save Settings", 
               command=lambda: save_all_settings(globals)).pack()
