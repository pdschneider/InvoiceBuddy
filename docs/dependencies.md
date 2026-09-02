# All Dependencies of **Invoice Buddy**

A full list of dependencies and their current versions are available in [requirements.txt](../packaging/requirements.txt).

## certifi
Mozilla CA certificate bundle

Required for: requests

LICENSE: Mozilla Public License, v.2.0

Source: https://github.com/certifi/python-certifi

## cffi
C Foreign Function Interface for Python

Depends on: pycparser

Required for: cryptography

LICENSE: MIT No Attribution

Source: https://github.com/python-cffi/cffi

## charset-normalizer
Character encoding detection

Required for: requests

LICENSE: MIT

Source: https://github.com/jawah/charset_normalizer

## cryptography
Cryptographic primitives (hashing, signing, etc.)

Depends on: cffi

Required for msoffcrypto-tool

LICENSE: Apache 2.0 / BSD

Source: https://github.com/pyca/cryptography

## CTkToolTip
Tooptip widget for customtkinter (old UI - deprecated)

Depends on: customtkinter

LICENSE: CC0 1.0 Universal

Source: https://github.com/Akascape/CTkToolTip

## customtkinter
Modern themed Tkinter widgets (old UI - deprecated)

LICENSE: MIT

Source: https://github.com/tomschimansky/customtkinter

## darkdetect
Detects OS dark/light mode

Dependency of: customtkinter

LICENSE: All rights reserved.

Source: https://github.com/albertosottile/darkdetect

## et_xmlfile
Low-memory XML writer

Required for: openpyxl

LICENSE: MIT / PYTHON SOFTWARE FOUNDATION LICENSE VERSION 2

Source: https://github.com/biydnd/et_xmlfile

## idna
International Domain Name Handling

Required for: requests, urllib3

LICENSE: BSD 3-Clause License / All rights reserved.

Source: https://github.com/kjd/idna

## iniconfig
INI file parser

Required for: pytest

LICENSE: MIT

Source: https://github.com/dmiro/iniconfig

## msoffcrypto-tool
Decrypt encrypted MS Office files

Depends on: olefile, cryptography

LICENSE: MIT

Source: https://github.com/nolze/msoffcrypto-tool

## Nuitka
Python compiler turning Python into C executables

LICENSE: APGL-3.0

Source: https://github.com/nuitka/nuitka

## olefile
Parses OLE compound file format (legacy Office files)

Required for: msoffcrypto-tool

LICENSE: All rights reserved.

Source: https://github.com/decalage2/olefile

## openpyxl
Read/write to .xlsx files

LICENSE: MIT

Source: https://foss.heptapod.net/openpyxl/openpyxl

## ordered-set
Ordered set data structure

Required by: Nuitka

LICENSE: MIT

Source: https://github.com/rspeer/ordered-set

## packaging
Version parsing, packaging utilities

LICENSE: Apache 2.0 / BSD

Source: https://github.com/pypa/packaging

## pdf2image
Converts PDF pages to PIL images

Required for: pillow

LICNSE: MIT

Source: https://github.com/Belval/pdf2image

## pdfminer.six
Low-level PDF text/layout extraction

Required for pdfplumber

LICNSE: MIT

Source: https://github.com/pdfminer/pdfminer.six

## pdfplumber
High-level PDF table/text extraction

LICENSE: MIT

Source: https://github.com/jsvine/pdfplumber

## pep8
PEP8 style tracker

LICENSE: None

Source: https://github.com/treyhunner/pep8

## pillow
Image processing library (PIL fork)

LICENSE: MIT-CMU

Source: https://github.com/python-pillow/Pillow

## pip
Package installer

LICENSE: MIT

Source: https://github.com/pypa/pip

## pluggy
Plugin management system

Required for: pytest

LICENSE: MIT

Source: https://github.com/pytest-dev/pluggy

## poppler-windows
Necessary for OCR on Windows

LICENSE: MIT

Source: https://github.com/oschwartz10612/poppler-windows

## psutil
System process monitoring

LICENSE: BSD 3-Clause

Source: https://github.com/giampaolo/psutil

## pycparser
C language parser for Python

Required for: cffi

LICENSE: All rights reserved.

Source: https://github.com/eliben/pycparser

## Pygments
Syntax highlighting

Required for: pytest

LICENSE: BSD 2-Clause / All rights reserved.

Source: https://github.com/pygments/pygments

## pyparsing
Text parsing library

Required for: pdfminer.six

LICENSE: MIT

Source: https://github.com/pyparsing/pyparsing

## pypdf
Reads/manipulates PDF metadata

LICENSE: All rights reserved.

Source: https://github.com/py-pdf/pypdf

## pypdfium2
PDF rengering engine

LICENSE: None

Source: https://github.com/pypdfium2-team/pypdfium2

## PySide6
Main Qt6 Python bindings

## PySide6_Addons
Addons for Qt6 Python bindings

## PySide6_Essentials
Essentials for Qt6 Python bindings

## pytesseract
Python wrapper for Tesseract OCR engine

License: Apache 2.0

Source: https://github.com/tesseract-ocr/tesseract

## pytest
Testing framework

Depends on: pluggy, iniconfig

LICENSE: MIT

Source: https://github.com/pytest-dev/pytest

## requests
HTTP library for making HTTP/HTTPS requests

Depends on: urllib3, idna, certifi, charset-normalizer

LICENSE: Apache 2.0

Source: https://github.com/psf/requests

## Send2Trash
Cross-platform send-to-trash delete functionality

LICENSE: BSD 3-Clause

Source: https://github.com/arsenetar/send2trash

## setuptools
Package building/installation

LICENSE: MIT

Source: https://github.com/pypa/setuptools

## shiboken6
C++ to Python binding generator that powers PySide6

Required for PySide6

## urllib3
Lower level HTTP library

Required for: requests

LICENSE: MIT

Source: https://github.com/urllib3/urllib3

## watchdog
Filesystem event monitoring

LICENSE: Apache 2.0

Source: https://github.com/gorakhargosh/watchdog

## zstandard
Zstandard compression library

Required by: Nuitka

LICENSE: BSD 3-Clause / All rights reserved.

Source: https://github.com/indygreg/python-zstandard

---

*Up to date as of v0.3.0*
