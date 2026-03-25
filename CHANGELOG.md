# Changelog

All notable changes to **Invoice Buddy** will be located in this file.

## [0.1.7] - 2026-00-00

This version 

### Added
- Added .gitignore for faster releases

### Changed
- 

### Fixed
- 

## [0.1.6] - 2026-03-24

This version of Invoice Buddy begins the transition to the much more modern and versatile GUI framework PySide6 and improves desktop integration for Linux and Windows.

### Added
- Added app icon for windows users
- Added XML file to AppImage for better Linux desktop integration
- Added factory reset button to advanced settings
- Added experimental wizard for later implementation
- Added view wizard button to about settings
- Added version file with metadata & a helper script to simplify the build process + improve Windows desktop integration

### Changed
- Improved configuration folder deletion pop-up box in case of critical GUI failure
- Switched some message boxes to toasts and others to the new PySide6 GUI framework
- Updated file and directory selection boxes
- Updated ReadMe

### Fixed
- Fixed error where a separate blank window was popping up during auto-name/data entry
- Removed deprecated security script from pre-release builds
- Removed deprecated 'revert moves/remove spreadsheet entries' functions from pre-release

## [0.1.5] - 2026-03-22

This version of Invoice Buddy focuses on documentation and bug fixes. 

### Added
- Added dedicated changelog.md file
- Python and Invoice Buddy versions now log at startup
- Added icons to settings pages
- Added config folder button to advanced settings
- Added dependency check for later GUI implementation

### Changed
- Updated loading function to work with Pyinstaller or Nuitka builds
- Updated theme check to more reliable hashing method
- Invoice Buddy now updates company map and paths automatically to reduce confusion and speed startup time
- Adding spreadsheet data now runs in a thread, making the GUI more responsive during writes
- Improved in-app changelog page
- Updated Readme
- Updated spec files
- Brought closer to PEP8 compliance
- New companies added to database
- Updated Dependencies

### Fixed
- Attempting to overwrite a file with the same name in a buddy's directory now safely returns with a warning
- Attempting to overwrite a file with the same name via the add button also safely returns with a warning
- Fixed error where Invoice Buddy was writing history file headers as individual letters on new lines
- Window now draws widgets before initial display, reducing UI errors
- Improved startup logic for more consistent and stable settings files
- Improved window redraw logic
- App now correctly shuts down logging and GUI
- General UI and stability improvements

## [0.1.4] - 2026-02-20

This update greatly improves the accuracy of auto-name feature, supports credit card numbers in auto-name, and also supports user selection for auto-naming so files are named exactly how each user wants.

### Added
- User can now choose the order autoname adds components to filenames
- Added Credit Card Number component to auto-name
- Added OCR fallback for cases when a file returns nothing
- New companies added to database

### Changed
- Greatly improved auto-name logic
- Each autoname function has been split into their own scripts
- Autoname now saves data to file metadata
- Added startup checks to fix missing or nonconforming values in spreadsheet.json
- Updated dependencies

### Fixed
- Removed folder map debug log spam on startup
- Added column keys to default spreadsheet.json file

## [0.1.3] - 2026-02-15

Invoice Buddy now allows the user to electively use the current version's folder map for archiving files, plus features updated folder and company maps.

### Added
- The app now prompts to update the folder map as well as company map

### Changed
- Spreadsheet settings are now housed in a scrollable frame
- Invoice number & date detection have been enhanced
- Internal company database updated
- Archive path automatically transfers from folder_maps.json to paths.json

### Fixed
- Removed "Program has been bundled with Pyinstaller" debug log spam

## [0.1.2] - 2026-02-04

This version supports icon selection for Invoices, Credit Cards, or Purchase Orders in the main inbox window as well as improve toast notifications.

### Added
- User can now select from a set of icons to represent sheets
- New icons added

### Changed
- Switched some warning message boxes to toasts
- Icons now visible in spreadsheet settings
- Changing the sheet name now changes its label
- Updated logging with new sheet labels

## [0.1.1] - 2026-02-03

Invoice Buddy now supports updates to the new company map on startup. The company map is a file that maps unique strings (phone numbers, addresses, emails, company names) to the company name used to rename files, as well as improved toast notifications and other general bug fixes and stability improvements.

### Added
- Added optional update for company map upon startup

### Changed
- Switched to toast notifications for some messages
- Removed unnecessary two letter word from onboarding page for English majors
- History path defaults to user-specific default path if not valid
- Changed "Moved" to "Archived" in history for clarity
- App ignores non-.pdf changes in the inbox folder, avoiding unnecessary GUI rebuilds
- Updated PSI to Summit Fire
- Updated dependencies

### Fixed
- Fixed error when deleting files on network drive
- Fixed error when buddy is named 'inbox'
- General stability improvements

## [0.1.0] - 2026-02-02

Welcome to the initial release of Invoice Buddy! This version sets the stage as a financial management app for quicker invoice entry and receipt archiving with a proper welcome document and stable features.

From Pre-release:

### Added
- Application runs through initial checks and cleans settings files if corrupted or missing values
- Draws window in the center of the screen if saved screen dimensions are missing or 0
- Added onboarding page for application start under empty or invalid path conditions
- Added welcome document

### Changed
- Normalized button icons
- Sanitized settings pages to eliminate saving nonconforming values

### Fixed
- Silenced CTkImage warnings
- Ensures all file opening or path selection can only choose working paths
- Application automatically creates new folders if one doesn't exist when archiving
- Fixed workbook and inbox not opening on Windows

### Deprecated
- Removed broken regenerate workbook buttons and revert history button
