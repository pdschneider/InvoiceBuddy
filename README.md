# InvoiceBuddy
Invoice Buddy is a financial management app that makes data entry easier

# Welcome to Invoice Buddy!

Invoice Buddy is designed to make the invoice entry process easier. Instead of manually writing
each filename and then entering the necessary data into your spreadsheet, the application takes
care of it for you.

# How to Use

## First Glance

Upon opening the program, you will be asked to add the path to your inbox and archive folders as
well as your workbook file.

```
Workbook : This is the path to your spreadsheet file, which should be a ".xlsx" file type.
Inbox : Your inbox should be the path to whichever folder you store the files which need to be
processed.
Archive : The archive is the top-level folder you will be storing all of the files which have
already been processed.
```

## Inbox

```
After completing on-boarding, you will find yourself at the main inbox page. This is where you will
manage entering data and archiving files.
(1) Inbox Button : In the top bar, you will find the button to navigate to your inbox.
(2) Settings Button : Also in the top bar, this button will take you to the settings page.
(3) Identity Button : This button cycles through three distinct types: Invoices, Card Receipts,
and Purchase Orders. Choosing the Invoice or Card icon will determine whether the data is
entered as an invoice or a card.
```
```
(4) Filename : This is where the name of each individual file lives. Double click to edit
individual file names.
(5) Add : This button brings up a file selection window for moving files to your inbox. It will
move the chosen files meaning they will no longer exist in the previous directory.
(6) Auto-name : The auto-name button reads the contents of chosen files and, if there is a
match within the Invoice Buddy database, automatically renames each file with this format:
"Company Name, Date, Invoice Number"
(7) Enter : The enter button will add the contents of each selected file's filename to the
spreadsheet corresponding to its type indicated by the identity button's state, ignoring
Purchase Orders. Each filename is broken into parts where separated by a space where each
filename is entered into its own row and each part is entered into its own column. For
example, the current file would be entered as follows:
```
```
(8) Archive : Clicking the "Archive" button will send selected files to a sub folder within the
archive path chosen earlier. Don't worry about creating each sub folder because Invoice
Buddy will do that for you. Any companies not already in the Invoice Buddy database will
default to a "Miscellaneous" folder.
(9) Workbook : Opens the workbook file at your selected file path.
(10) Inbox : Opens the inbox folder in your default file explorer application.
(11) Delete : Sends selected files to trash (recoverable).
```

## Settings

Within settings, you have access to a variety of tools and configuration options.

**General** : In this tab, you can choose your theme.

**Paths** : The paths tab allows you to choose your workbook file, inbox path, and archive just like the
on-boarding page, as well as your history file which logs which files you have entered and archived
and must be a ".csv". This is also where you are allowed to add buddies if you collaborate with
others on the same file system.

**Spreadsheet** : The spreadsheet tab allows you to more finely tune how Invoice Buddy adds data to
your spreadsheet. Here, you can choose the sheet name and optional table name for invoices,
credit cards, and purchase orders, as well as the starting row and starting column for each sheet.

**History** : This tab lets you see which files you have previously entered or archived, which user did
the archiving and/or entering, and the ability to export or import log data.

**Advanced** : The advanced tab allows you to choose the logging level for the program. This is
separate from history logging and is designed for debugging or getting more specific information
about errors.

**About** : This tab gives you a brief explanation of what Invoice Buddy does and allows you to view
the change log.


## Adding Buddies

To add buddies, navigate to the Paths settings tab and click the "+" button underneath "Buddies".
This allows you to pick each buddy name and inbox. You can add up to three buddies and each
one will add a "Send to" button to your inbox page, allowing you to send files between members of
an organization.


