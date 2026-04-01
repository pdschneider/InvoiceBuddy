# Interface/Windows/changelog.py
import logging
import customtkinter as ctk
import src.utils.fonts as fonts
import pathlib
import re
if not hasattr(ctk, "CTkScrollableFrame"):
    logging.critical(f"CTkScrollableFrame missing.")

changelog_path = pathlib.Path(__file__).parent.parent.parent / "CHANGELOG.md"
current_version = re.compile(
    r"^##\s*\[(?P<ver>[^]]+)]\s*-\s*(?P<date>[\d-]*)", re.MULTILINE)


def parse_changelog() -> list[dict]:
    """
    Returns a list of dicts:
        {
            "version": "0.2.0",
            "date":    "2026-02-15",
            "body_md": "...markdown for this block..."
        }
    """
    raw = changelog_path.read_text(encoding="utf-8")
    matches = list(current_version.finditer(raw))

    entries = []
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(raw)

        body_md = raw[start:end].strip()
        entries.append(
            {
                "version": m.group("ver").strip(),
                "date": m.group("date").strip(),
                "body_md": body_md,
            }
        )
    return entries


def markdown_to_plain(md: str) -> list[tuple[str, tuple]]:
    """
    Convert a markdown block into a list of (text, font) pairs.
    * ### headings → use fonts.heading_font (already bold)
    * - list items → bullet with fonts.body_font
    * plain paragraphs → fonts.body_font
    """
    lines_out: list[tuple[str, tuple]] = []

    for raw in md.splitlines():
        line = raw.rstrip()

        # Section headings (### Added, ### Changed, …)
        if line.startswith("###"):
            heading = line.lstrip("#").strip()
            lines_out.append((heading, fonts.heading_font))
            continue

        # Unordered list items
        if line.startswith("- "):
            bullet = "• " + line[2:].strip()
            lines_out.append((bullet, fonts.body_font))
            continue

        # Blank line – keep spacing
        if line == "":
            lines_out.append(("", fonts.body_font))
            continue

        # Anything else – treat as normal paragraph
        lines_out.append((line, fonts.body_font))

    return lines_out


def create_changelog(globals, changelog_tab):
    """
    Creates the tab to display setup instructions for new users.

            Parameters:
                    globals: Global variables
                    setup_tab: The main frame of the setup window
    """

    changelog_frame = ctk.CTkScrollableFrame(changelog_tab)
    changelog_frame.pack(fill="both", expand=True, padx=10, pady=0)

    inner_width = 460
    inner_container = ctk.CTkFrame(
        changelog_frame,
        width=inner_width,
        fg_color="transparent")
    inner_container.pack(anchor="center", pady=5)

    # Main Changelog Section
    for entry in parse_changelog():
        # version + date (centered)
        header = f"{entry['version']}\u2003–\u2003{entry['date']}"
        ctk.CTkLabel(
            inner_container,
            text=header,
            font=fonts.heading_font,
            anchor="center",          # center the text inside its own label
        ).pack(fill="x", pady=8, padx=5)

        # body: each line left‑aligned
        for txt, fnt in markdown_to_plain(entry["body_md"]):
            ctk.CTkLabel(
                inner_container,
                text=txt,
                font=fnt,
                justify="left",          # text wraps left‑aligned
                wraplength=inner_width - 20,   # leave a tiny side padding
                anchor="w",              # align the label itself to the left
            ).pack(fill="x", padx=10, pady=2)

    # Buttons Frame
    buttons_frame = ctk.CTkFrame(changelog_tab, fg_color="transparent")
    buttons_frame.pack(fill="x", padx=10, pady=10)

    ctk.CTkButton(buttons_frame,
                  text="Back",
                  command=lambda: back_to_main_page()).pack(padx=5, pady=0)

    def back_to_main_page():
        """
        Forgets setup and settings pages to return
        the user to a clean main page.
        """
        globals.changelog.pack_forget()
        globals.settings_page.pack(fill="both", expand=True, padx=10, pady=0)
        globals.title.configure(text="Settings")
