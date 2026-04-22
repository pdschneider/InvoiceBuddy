# 📖 How to Use Invoice Buddy

Invoice Buddy makes repetitive invoice processing much faster by automatically scanning files, suggesting smart filenames, helping you enter data into a spreadsheet, and archiving everything with one click.

This guide walks you through the main workflow and features.

## Getting Started

1. **Launch Invoice Buddy**  
   Run the built executable (`InvoiceBuddy.exe` on Windows or `InvoiceBuddy.AppImage` on Linux).

2. **Complete the Onboarding (first time only)**  
   The setup wizard will guide you through:
   - Selecting your main spreadsheet file
   - Configuring default archive folder
   - Initializing inbox folder

3. **Main Screen Overview**  
   - **Inbox area**: Shows the files you’ve added for processing  
   - **Bottom action bar**: Contains the main buttons (Enter to Spreadsheet, Archive, etc.)  
   - **Top menu**: Access to Settings and History

## Main Workflow

### 1. Add Files
- Click the **Add Files** button to copy files from another path to the inbox

### 2. Review Auto-Generated Information
After clicking the auto-name button, Invoice Buddy will scan each file and:
- Extract data (invoice number, date, vendor, etc.)
- Rename each file based on extracted data

**Important**: Always double-check the extracted data and filename before proceeding.

### 3. Enter Data into Spreadsheet
- Select one or multiple files
- Click **Enter to Spreadsheet** button (pen icon)
- Invoice Buddy will append the extracted data to your configured spreadsheet

### 4. Archive Files
- After entering data, click **Archive**
- Files are automatically moved to the correct folder using the generated filename

### 5. View History
- Use the History tab under settings to see previously processed files
- Export history if needed for auditing

### 6. Spreadsheet Configuration
Under the "Spreadsheet" tab in settings, users can:
- Choose sheet names
- Choose starting row and columns
- Choose icon to represent each sheet in the inbox view
- Select order to auto-name files

## Settings

Open Settings from the top menu button. Key areas include:

- **General Settings** — Select theme and other general settings
- **Paths Configuration** — Select workbook, inbox, history, and archive paths, and add buddies
- **Spreadsheet** — Add sheet names, table names, select first rows and columns, auto-naming order, and icons
- **History** — View history + import/export
- **Advanced** — Change logging level, open key folders, factory reset configuration
- **About** — View version number, changelog, and open wizard

## Tips for Best Results

- Use clear, high-quality PDFs for better data extraction accuracy
- Scanning documents works, but is less reliable requires additional dependencies on Windows
- Process files in small batches so you can review results easily
- Always verify spreadsheet entries before finalizing payments or records

## Troubleshooting

- **Files not appearing in inbox** → Make sure the file types are supported (PDF only)
- **Files only partially renamed** → Try higher-resolution scans or download documents directly
- **Spreadsheet not updating** → Check that the spreadsheet path in Settings is correct and the file is not open in another program (shared spreadsheets often have this problem)
- **Auto-naming looks wrong** → Manually edit by double clicking the filename in the inbox window
- **App feels slow** → Close large spreadsheets before processing and ensure you meet the recommended 8 GB RAM
- **Company not supported yet** → Open a GitHub issue and send your invoice in (no personal info required)!

## Keyboard Shortcuts (Coming Soon)

- Will be listed here once implemented

## Privacy & Safety

- All processing happens on your computer — nothing is sent online unless linked to Google Sheets (future)
- You are responsible for verifying all extracted data and filenames before use

---

**Maintained by**: Phillip Schneider

Questions or suggestions? Open an issue on the [GitHub repository](https://github.com/pdschneider/InvoiceBuddy).
