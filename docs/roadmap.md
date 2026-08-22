
# 💸 Invoice Buddy Roadmap

This document outlines the vision, planned features, and development priorities for **Invoice Buddy**.

It is a living document and will be updated periodically. Some features may not be included in Invoice Buddy and other features not listed may be added.

## 📅 Current Status (August 2026)

- **Version**: 0.2.x (Stable release available)
- **Core Features**: Auto-generated filenames, quick spreadsheet entry, fast file archival
- **Platforms**: Linux (x64) & Windows 10/11

## 🎯 Project Vision

Invoice Buddy is an invoice and receipt management app designed to simplify financial data entry by automating filenames, spreadsheet data entry, and archival.

My original roadmap had a series of check boxes separated by minor versions. I found this to be difficult to keep up with and a bit too specific, causing me to neglect the roadmap and treat it as a twice-a-year document to update. To modernize and simplify, I am going to turn this roadmap into a written document outlining my overall vision for **Invoice Buddy**.

I want Invoice Buddy to mature into a full-feature financial management and budgeting app. Originally, I developed it to follow a specific data entry pattern for my work, but as I build the app I have realized that I can fill a wider gap in the software market with a fully self-hosted and private financial management solution.

In my opinion, there are a handful of fantastic apps which are either Android or Desktop specific that do a great job of offering a detailed financial dashboard and keeping track of basic transactions, but no app does a sufficient job of being (a) private, (b), supports Desktop & Android sync, and (c) has a robust budgeting feature. If you want desktop-focused detailed financial tracking, then Actual Budget and FireFly III do the job. If you want local Android transaction tracking, many apps fit the bill, and if you want high quality budgeting then Every Dollar or possibly Rocket Money can be your solution.

What I want Invoice Buddy to become is the cross-platform self-hosted solution that average users will maximally benefit from. Having sync between Desktop and Mobile is important to me, as are a focus on budgeting and ease-of-use.

The app will still fully support use by small, medium, and large companies as well as everyday users, but also expand as I continue to develop the software to satisfy the needs of more types of users.

Overall, I plan to make Invoice Buddy the software I wish already existed.

## 🏆 Major Achievements

- [x] In the process of transitioning the GUI to PySide6 from Custom Tkinter
- [x] Printer support for keeping physical copies of receipts/invoices
- [x] Robust auto-naming feature supporting 160+ companies, municipalities, and government departments
- [x] OCR fallback on both Windows and Linux
- [x] Company name, date, invoice number, and card number included in auto-name

## 🗺️ Planned Milestones

The roadmap for Invoice Buddy includes several planned features prior to the official 1.0 release. Each minor release will be bumped by a feature addition and is always subject to change.

- [ ] Support for Google Sheets
- [ ] Support for .odf spreadsheets
- [ ] Image-to-pdf file conversion
- [ ] Default spreadsheet file/generation
- [ ] Progress bar for auto-name
- [ ] TUI / Web UI
- [ ] Rest API
- [ ] Change the name
- [ ] Budgeting Feature
- [ ] In-app transaction record management

### Improvements for the Auto-Name Feature
- [ ] Add description (what was purchased)
- [ ] Add Terms (Net 30, Due Upon Receipt, etc.)
- [ ] Add Total Amount
- [ ] Add Total Tax
- [ ] Add Sales Tax
- [ ] Custom Field (user determined)

## 📝 Notes

- Priorities may shift based on user feedback and bug reports.
- Feature requests are welcome — please open a GitHub issue.
- This roadmap focuses primarily on **user-facing** improvements. Technical debt and refactoring happen continuously.

**Maintained by** Phillip Schneider
*Last updated as of v0.2.9*
