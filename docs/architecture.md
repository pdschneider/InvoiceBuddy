
# 🏗️ Invoice Buddy Architecture

This document provides a high-level overview of Invoice Buddy's codebase and design decisions. It is intended for developers who want to understand how the application is structured.

## Overview

Invoice Buddy is a financial management desktop application built with Python. It features a graphical user interface using **Custom Tkinter** with certain elements built with **PySide6**, automating repetitive invoice processing tasks by auto-generating filenames, entering data to a local spreadsheet, and quickly archiving files.

The application is designed to be:
- **Fully offline-first** — no user data leaves the local machine by default
- **Cross-platform** — Windows 10/11 and Linux (Ubuntu 18.04+ recommended)
- **Easy to build and distribute** — using PyInstaller (recommended on Windows) and Nuitka (Linux)
- **Simple and focused** — minimal dependencies with a clean, actionable interface

## Core Components

### 1. GUI Layer (Custom Tkinter + PySide6)
- Main window with inbox-style file view and bottom action buttons
- Settings page with multiple sub-pages
- Onboarding page / wizard
- Message boxes and file selection boxes built with PySide6

### 2. Backend / Core Logic (Managers)
- File scanning and content analysis
- Data extraction (invoice number, date, company, etc.)
- Auto-naming logic (`Managers/Autoname`)
- Customizable spreadsheet entry
- History retention
- Import + export for history

### 3. Utilities & Helpers
- Shared functions for loading, saving, and toasts
- Configuration loading and defaults management

### 4. Data & Persistence
- `defaults/` directory for configuration and assets
- Welcome document
- Company and folder maps for auto-naming and archival

## Folder Structure

```Bash
InvoiceBuddy/
├── InvoiceBuddy.py           # Main entry point - launches the GUI
├── config.py                 # Configuration and settings handling
├── version.py                # Version information
├── defaults/                 # Default themes, assets, icons, and configuration files
├── src/                      # Primary source code
│   ├── interface/            # All GUI-related code
│   │   ├── components/       # Reusable  UI components
│   │   ├── settings/         # Settings pages
│   │   └── setup/            # Initial setup wizard and onboarding screen
│   ├── connections/          # Connections to external API's or domains (ex: GitHub)
│   ├── managers/             # Core business logic managers
│   │   └── autoname/         # Logic for auto-generating filenames
│   └── utils/                # Utility functions, helpers, and shared tools
├── data/                     # Development mode data storage
├── packaging/                # Build configurations, spec files, AppImage resources, Inno Setup scripts
├── docs/                     # Documentation files (ARCHITECTURE.md, USAGE.md, etc.)
├── CHANGELOG.md
├── LICENSE.txt
└── README.md
```

## Key Design Decisions

- **Separation of Concerns**: GUI code is kept separate from core logic where possible.
- **Privacy First**: All processing happens locally. No telemetry or cloud services are used by default.
- **Modularity**: Multiple filetypes are supported for spreadsheets and cloud integration is planned.
- **Why PySide6**: Chosen for better styling, performance, and modern Qt features compared to the current Tkinter implementation.
- **Build Strategy**: One-file executables for easy distribution while maintaining reasonable binary size.

## Data Flow (Simplified)

1. User adds files to the inbox view
2. Invoice Buddy scans and analyzes files for keywords
3. Extraction engine pulls key data
4. Auto-naming feature generates a new filename based on file contents in a user-selected order
5. Data is entered to a spreadsheet via the filenames via the spreadsheet entry button
6. Files are moved to appropriate auto-generated folders when user clicks archive button
7. All actions are logged to history for auditing

## Extensibility Points

- Adding support for more filetypes for both spreadsheets and invoices
- Extending auto-naming to meet more criteria
- Adding spreadsheet generation logic
- Incorporating printer support for making physical copies of invoices/receipts
- Supporting cloud-based spreadsheets like Google Sheets

## Future Considerations

- Full migration to PySide6 for a more modern and versatile GUI
- Enhanced data validation and error handling
- Expanded company list
- Performance optimizations for large context windows

---

## Folder Structure (deb - inside packaging/)

``` bash
deb/
├── DEBIAN
├── etc
│   └── invoice-buddy
└── usr
    ├── bin
    ├── lib
    │   └── invoice-buddy
    └── share
        ├── applications
        ├── doc
        │   └── invoice-buddy
        ├── icons
        │   └── hicolor
        │       ├── 128x128
        │       │   └── apps
        │       ├── 256x256
        │       │   └── apps
        │       └── scalable
        ├── invoice-buddy
        ├── man
        │   └── man1
        ├── metainfo
        └── pixmaps

```

---

## Important Variables

### Paths
- globals.inbox: The path to the user's chosen inbox directory
- globals.workbook: The path to the user's chosen workbook file
- globals.archive: The path to the user's chosen top-level archive directory

### UI
- globals.history_tree: The tkinter treeview for viewing past actions
- globals.inbox_tree: Custom treeview used for the inbox

### Configuration
- globals.os_name: The name of the user's operating system
- globals.user: The name of the currently logged in user

---

**Maintained by**: Phillip Schneider
