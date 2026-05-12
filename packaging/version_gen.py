# packaging/version_gen.py
# Auto-generates version.txt from version.py for PyInstaller Windows builds
# Also updates Inno Script

import re
import sys
from pathlib import Path

# Add the project root to Python path so we can import "version" reliably
project_root = Path(__file__).parent.parent.resolve()   # Goes up from packaging/ to root
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from version import __version__, __author__, __title__, __description__

# Parse version string into tuple (major, minor, patch, build)
try:
    clean_version = __version__.replace('-beta', '').replace('-rc', '')
    major, minor, patch = map(int, clean_version.split('.'))
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
          StringStruct('InternalName', 'Invoice Buddy'),
          StringStruct('LegalCopyright', 'Copyright © 2026 {__author__}. Apache 2.0.'),
          StringStruct('OriginalFilename', 'InvoiceBuddy.exe'),
          StringStruct('ProductName', '{__title__}'),
          StringStruct('ProductVersion', '{__version__}'),
          StringStruct('Comments', 'Personal Everything Assistant Running Locally'),
        ])
      ]),
    VarFileInfo([VarStruct('Translation', [0x409, 1200])])
  ]
)
'''

# Also update the Inno Script file with correct information
inno_script_path = project_root / 'packaging' / 'InnoSetup.iss'

if inno_script_path.exists():
    with open(inno_script_path, 'r', encoding='utf-8') as f:
        inno_content = f.read()

    # Update the three defines using the values from version.py
    inno_content = re.sub(
        r'^#define MyAppName ".*"',
        f'#define MyAppName "{__title__}"',
        inno_content,
        flags=re.MULTILINE
    )
    inno_content = re.sub(
        r'^#define MyAppVersion ".*"',
        f'#define MyAppVersion "{__version__}"',
        inno_content,
        flags=re.MULTILINE
    )
    inno_content = re.sub(
        r'^#define MyAppPublisher ".*"',
        f'#define MyAppPublisher "{__author__}"',
        inno_content,
        flags=re.MULTILINE
    )

    with open(inno_script_path, 'w', encoding='utf-8') as f:
        f.write(inno_content)
    
    print(f"✅ Inno Setup script successfully updated")
    print(f"   Location: {inno_script_path}")
else:
    print(f"⚠️  Inno script not found at {inno_script_path}")

# Update the Debian control file
control_file_path = project_root / 'packaging' / 'deb' / 'DEBIAN' / 'control'

if control_file_path.exists():
    with open(control_file_path, 'r', encoding='utf-8') as f:
        control_content = f.read()

    # Replace the Version line specifically
    # This regex matches "Version: " followed by anything until the end of the line
    deb_version = __version__.replace('-beta', '~beta').replace('-rc', '~rc')

    control_content = re.sub(
        r'^Version: .*$',
        f'Version: {deb_version}',
        control_content,
        flags=re.MULTILINE)

    with open(control_file_path, 'w', encoding='utf-8') as f:
        f.write(control_content)
    
    print(f"✅ Debian control file successfully updated")
    print(f"   Location: {control_file_path}")
else:
    print(f"⚠️  Control file not found at {control_file_path}")

# Always write version.txt to the corect location
version_txt_path = project_root / 'packaging' / 'version.txt'

with open(version_txt_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✅ version.txt successfully generated with version {__version__}")
print(f"   Location: {version_txt_path}")
