# Changelog

All notable changes to **Invoice Buddy** will be located in this file.

## [0.2.8] - 2026-08-06

This version of Invoice Buddy adds another step of Google Sheets integration and features various UI and bug fixes, as well as several new companies added!

### Added
- Users can now choose a URL to add for later Google Sheets integration
- New companies: Whidbey Coffee, Desktronic Trading US, Pilot Travel Centers LLC, Subway, Jiffy Lube International, Washington State Department of Ecology, Under Armour, TJ Maxx
- Sha256 Checksums are now added to release notes
- Archive path is now viewable via the title bar's File Menu

### Changed
- Upgraded from Python 3.12.3 to Python 3.13.14 on Linux
- Updated dependencies
- Lowered log count to 30
- Built with cached temp files for faster re-launch
- Users upgrading from previous versions no longer have to go through as many pages of the installation wizard each upgrade
- Minor UI improvements and bug fixes

### Fixed
- During Windows installs, application now closes whether or not it responds to graceful shutdown commands - correcting a rare error during the installation process
- Browse buttons in Qt-GUI paths settings now correctly fill text boxes and save
- Toasts now correctly show up for successful spreadsheet entries

## [0.2.7] - 2026-07-07

This version of Invoice Buddy adds new functionality to the new GUI - modular sheet names, contextual buttons, bulk labeling, and more!

### Added
- Added new companies: QFC, IdentoGo by IDEMIA
- Added 'Changelog' panel accessible from the title bar under 'Help' in the new GUI
- Added 'About' panel accessible from the title bar under 'Help' in the new GUI
- Added spreadsheet data to Qt GUI settings (for later implementation)
- Added pills to the Qt GUI to indicate & cycle through sheets for each invoice (in later implementation)
- Delete button moved in new GUI to above the mailbox pane only when something is selected
- Print button moved to new contextual above mailbox pane
- New button added above mailbox pane for bulk sheet naming
- Entering data to spreadsheet now works with new Qt GUI data formats when in new GUI mode
- Auto-naming now uses Gt-GUI specific sheet names

### Changed
- Various UI improvements

### Fixed
- Stopped app from trying to apply CTK theme after switching to the Qt GUI
- Fixed glitchy toast from opening second window in Qt GUI
- Fixed legacy mode bug where sheets with non-conforming identities were not entered to spreadsheet

## [0.2.6] - 2026-07-01

This version of Invoice Buddy fixes various bugs introduced by the new GUI and adds one new company to the database.

### Added
- Added companies: Rocket Mortgage, LLC

### Changed
- Updated dependencies

### Fixed
- Fixed issue where renaming files in the new GUI would fail while pdf is up in the preview pane
- Fixed crash when preview pane is the exact size to fit the image
- Fixed broken legacy archive function
- Fixed broken OCR on Linux

### Security
- Fixed pypdf-related security vulnerability by updating to the most recent version

## [0.2.5] - 2026-06-14

This version of Invoice Buddy marks an important transition over to the new GUI framework. Users can now switch between legacy mode and Qt mode to test the new app.

### Added
- New companies added to database: Chick N Fries
- Added togglable legacy mode
- Added enter to spreadsheet functionality to new GUI
- Added auto-name functionality to new GUI
- Added print button functionality to new GUI
- Added archive functionality to new GUI
- Added more settings to new GUI
- Added functional title bar buttons to new GUI
- Added new setting for later Google Sheets implementation

### Changed
- Further separated QT-compatible code from the legacy app
- Updated dependencies

### Fixed
- Fixed logging error in archive files function
- Corrected broken auto-name feature in legacy mode
- Got rid of leading comma causing many companies to be titled "Name"

## [0.2.4] - 2026-05-26

Invoice Buddy is now pre-compiled to C on Windows! This improves speed and file size dramatically, taking Invoice Buddy from ~160GB to less than 90GB with all dependencies included!

### Added
- Invoice Buddy is now pre-compiled to C, improving speed and reducing file size
- New Companies: Chevron Corporation, Exxon Mobil Corporation, Precision Analytical Laboratories, Thai Go, Wendy's Restaurant, Great Clips, Inc.
- Greatly improved functionality of future GUI

### Changed
- Added debug line to troubleshoot windows silently not opening download in the browser
- Minor UI improvements
- Update dependencies

### Fixed
- Fixed issue where .deb users could not update from beta releases to the next stable release without uninstalling first
- Fixed issue where app state was considered Development even for .deb builds, breaking app restart logic
- Added missing info for Carrier Corporation's auto-name
- Fixed broken update check for Windows users
- Fixed incorrect exe description

### Security
- Patched 2 high severity vulnerabilities affecting availability and confidentiality of data in the urllib3 dependency by updating to version 2.7.0

## [0.2.3] - 2026-05-08

This update bundles OCR-related files for Windows users, making OCR cross-platform. It also fixes several Windows-specific crashes and adds an option to not remember window placement, which helps users with multiple monitor setups from having a wonky sized window.

### Added
- Tesseract and Popplar now come bundled on Windows, allowing seamless OCR
- Users can now select whether the window loads in the same spot it was left on the screen last time

### Changed
- Changed about page to include new bundled binaries

### Fixed
- Fixed crash on startup when Tesseract was not installed on Windows
- Fixed error when restarting the app via settings by removing the prompt on Windows

## [0.2.2] - 2026-05-06

This version includes 15 new companies and is build as a .deb in addition to AppImage for Linux, granting Debian users full desktop integration. Invoice Buddy also has an optional beta channel for updates, making the main channel more stable.

### Added
- Invoice Buddy is now available as a .deb on Linux
- Added beta channel to separate stable vs feature-rich branches
- Added Companies: Walgreens, ARCO, Bigfoot Music, Butter Notes Cafe, Marshalls, Old Navy, Apple Inc., Pioneer Gas, Popeyes Louisiana Kitchen, Royal Star Buffet, Sunnyside Nursery, Washington Dept of Licensing, Snohomish County Treasurer, Ulta Beauty, Wet Rabbit

### Changed
- Tesseract version now logged for debugging
- Updated dependencies

### Fixed
- Added missing metadata to Windows setup file
- Various minor UI and bug fixes

## [0.2.1] - 2026-04-22

This version adds an automatic update check on startup so you don't have to manually search for new updates to Invoice Buddy. It also supports 9 new companies and is the first version of Invoice Buddy for Windows to be correctly signed with an official certificate!

### Added
- Added Tesseract check for Windows users to prompt for download if missing
- Added optional update check on startup
- New companies supported: 7-Eleven, Everything John Deere Gator, Logical Operations, Independent Publishers Group, Fred Meyer, Haggen, Kitanda, Shell USA, Inc., SKECHERS USA, Inc.

### Changed
- Added restart prompt when saving settings which require app restart to apply
- Invoice Buddy shuts down much faster on app close
- Various UI improvements
- Updated dependencies

### Fixed
- Properly signed Windows app with official SSL.com certificate

### Security
- Patched several pypdf-related exploits by updating to v6.10.2

## [0.2.0] - 2026-04-08

This version kicks off printer support. Users can now select their default printer and print PDF documents from right inside Invoice Buddy!

### Added
- Added support for printing files from selected printer
- New companies added to database: SSL.com, Seoul Bowl
- Added github button in about settings
- The windows app is signed with a self-signed certificate - moving to official certificate next release

### Changed
- General stability & UI improvements and code refinements
- Updated dependencies

### Fixed
- Invoice Buddy now correctly supports password protected notebooks
- Archival now skips moving files that already exist in their destination folder

## [0.1.7] - 2026-04-02

This version adds greater desktop integration for Windows users and speed for Linux. The entire top-level project structure has been redesigned to fit more with convention and various bugs & vulnerabilities have been patched.

### Added
- Built via Nuitka on Linux, dramatically speeding up performance
- Full desktop integration for Windows
- Added .gitignore for faster releases
- Added new documentation: architecture, build, roadmap, companies, & usage + updated ReadMe

### Changed
- Reintroduced messageboxes to alert user when auto-name is complete
- Reorganized project structure
- Updated dependencies

### Fixed
- Fixed dependency chain issue resulting in failed builds using requirements.txt
- Fixed crash caused by PySide file browse boxes

### Security
- Updated several dependencies with low to moderate security vulnerabilities
- Removed logging with references to sheet names

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
