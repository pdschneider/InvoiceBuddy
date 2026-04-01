# packaging/version_gen.py
# Auto-generates version.txt from version.py for PyInstaller Windows builds

import sys
from pathlib import Path


def update_version_txt():
  # Add the project root to Python path so we can import "version" reliably
  project_root = Path(__file__).parent.parent.resolve()   # Goes up from packaging/ to root
  if str(project_root) not in sys.path:
      sys.path.insert(0, str(project_root))

  from version import __version__, __author__, __title__, __description__

  # Parse version string into tuple (major, minor, patch, build)
  try:
      major, minor, patch = map(int, __version__.split('.'))
      build = 0
  except Exception:
      major, minor, patch, build = 0, 1, 0, 0

  content = f'''# UTF-8
  # Auto-generated from version.py - DO NOT EDIT MANUALLY

  VSVersionInfo(
    ffi=FixedFileInfo(
      filevers=({major}, {minor}, {patch}, {build}),
      prodvers=({major}, {minor}, {patch}, {build}),
      mask=0x3f,
      flags=0x0,
      OS=0x40004,
      fileType=0x1,
      subtype=0x0,
      date=(0, 0)
      ),
    kids=[
      StringFileInfo(
        [
        StringTable(
          '040904B0',
          [
            StringStruct('CompanyName', '{__author__}'),
            StringStruct('FileDescription', '{__description__}'),
            StringStruct('FileVersion', '{__version__}'),
            StringStruct('InternalName', 'InvoiceBuddy'),
            StringStruct('LegalCopyright', 'Copyright © 2026 {__author__}. Apache 2.0.'),
            StringStruct('OriginalFilename', 'InvoiceBuddy.exe'),
            StringStruct('ProductName', '{__title__}'),
            StringStruct('ProductVersion', '{__version__}'),
            StringStruct('Comments', 'Makes invoice and financial data entry easier.'),
          ])
        ]),
      VarFileInfo([VarStruct('Translation', [0x409, 1200])])
    ]
  )
  '''

  # Always write version.txt to the project root
  version_txt_path = project_root / 'packaging' / 'version.txt'

  with open(version_txt_path, 'w', encoding='utf-8') as f:
      f.write(content)

  print(f"✅ version.txt successfully generated with version {__version__}")
  print(f"   Location: {version_txt_path}")


def update_deb_control():
    """Update the Version field in the Debian control file using the version from version.py"""
    project_root = Path(__file__).parent.parent.resolve()
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from version import __version__

    control_path = project_root / 'packaging' / 'deb' / 'DEBIAN' / 'control'

    if not control_path.exists():
        print("⚠️  DEBIAN/control file not found. Skipping update.")
        return

    # Read the current control file
    with open(control_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Update only the Version line
    updated = False
    for i, line in enumerate(lines):
        if line.strip().startswith('Version:'):
            lines[i] = f"Version: {__version__}\n"
            updated = True
            break

    if not updated:
        print("⚠️  Could not find 'Version:' line in control file.")
        return

    # Write back the updated control file
    with open(control_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print(f"✅ DEBIAN/control updated with version {__version__}")


update_version_txt()
update_deb_control()
