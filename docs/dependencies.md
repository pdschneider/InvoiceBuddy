# This document lists and describes all dependencies of **Invoice Buddy**

### certifi
Mozilla CA certificate bundle
Required for: requests

### cffi
C Foreign Function Interface for Python
Depends on: pycparser
Required for: cryptography

### charset-normalizer
Character encoding detection
Required for: requests

### cryptography
Cryptographic primitives (hashing, signing, etc.)
Depends on: cffi
Required for msoffcrypto-tool

### CTkToolTip
Tooptip widget for customtkinter (old UI - deprecated)
Depends on: customtkinter

### customtkinter
Modern themed Tkinter widgets (old UI - deprecated)

### darkdetect
Detects OS dark/light mode
Dependency of: customtkinter

### et_xmlfile
Low-memory XML writer
Required for: openpyxl

### idna
International Domain Name Handling
Required for: requests, urllib3

### iniconfig
INI file parser
Required for: pytest

### msoffcrypto-tool
Decrypt encrypted MS Office files
Depends on: olefile, cryptography

### Nuitka
Python compiler turning Python into C executables

### olefile
Parses OLE compound file format (legacy Office files)
Required for: msoffcrypto-tool

### openpyxl
Read/write to .xlsx files

### ordered-set
Ordered set data structure
Required by: Nuitka

### packaging
Version parsing, packaging utilities

### pdf2image
Converts PDF pages to PIL images
Required for: pillow

### pdfminer.six
Low-level PDF text/layout extraction
Required for pdfplumber

### pdfplumber
High-level PDF table/text extraction

### pep8
PEP8 style tracker

### pillow
Image processing library (PIL fork)

### pip
Package installer

### pluggy
Plugin management system
Required for: pytest

### psutil
System process monitoring

### pycparser
C language parser for Python
Required for: cffi

### Pygments
Syntax highlighting
Required for: pytest

### pyparsing
Text parsing library
Required for: pdfminer.six

### pypdf
Reads/manipulates PDF metadata

### pypdfium2
PDF rengering engine

### PySide6
Main Qt6 Python bindings

### PySide6_Addons
Addons for Qt6 Python bindings

### PySide6_Essentials
Essentials for Qt6 Python bindings

### pytesseract
Python wrapper for Tesseract OCR engine

### pytest
Testing framework
Depends on: pluggy, iniconfig

### requests
HTTP library for making HTTP/HTTPS requests
Depends on: urllib3, idna, certifi, charset-normalizer

### Send2Trash
Cross-platform send-to-trash delete functionality

### setuptools
Package building/installation

### shiboken6
C++ to Python binding generator that powers PySide6
Required for PySide6

### urllib3
Lower level HTTP library
Required for: requests

### watchdog
Filesystem event monitoring

### zstandard
Zstandard compression library
Required by: Nuitka

*Up to date as of v0.3.0-beta*
