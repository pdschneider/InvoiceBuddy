# 🚀 Build Invoice Buddy

Invoice Buddy can be built from source code via Pyinstaller or Nuitka on both Windows and Linux. This is for advanced users only - the simplest way to run Invoice Buddy is to download the latest release.

## 🐧 Linux

Open your IDE (VSCode recommended) and create a virtual environment using Python 3.13.15 from deadsnakes:

Download Python 3.13.15 from [Deadsnakes](https://launchpad.net/~deadsnakes/+archive/ubuntu/ppa).

```
python3.13 -m venv invoice_venv

source invoice_venv/bin/activate
```

### Pyinstaller

Run these commands to install dependencies and generate the file:

```
pip install -r packaging/requirements.txt

pyinstaller packaging/InvoiceBuddy-Linux.spec --clean
```

### Nuitka

Alternatively, run these commands to build with Nuitka:

Build the App:
````
pip install -r packaging/requirements.txt

nuitka \
    --standalone \
    --onefile \
    --onefile-cache-mode=cached \
    --quiet \
    --product-version=0.2.9 \
    --file-version=0.2.9 \
    --company-name=InvoiceBuddy \
    --product-name=Invoice Buddy \
    --output-filename=invoice-buddy \
    --remove-output \
    --output-dir=dist \
    --enable-plugin=pyside6 \
    --enable-plugin=tk-inter \
    --include-qt-plugins=platforms,iconengines,imageformats \
    --include-data-dir=defaults=defaults \
    --include-data-files=CHANGELOG.md=CHANGELOG.md \
    --include-data-files=README.md=README.md \
    --include-data-files=LICENSE.txt=LICENSE.txt \
    main.py
````

Make sure to update the product version and file version with the correct version number.

*Note: Nuitka builds can take significantly longer than Pyinstaller. Assume 5-10 minutes to complete.*

## AppImage

To build an AppImage file, follow these steps after building the file with the previous commands.

**IMPORTANT: Must have patchelf installed: `sudo apt patchelf`**

Install appimagetool if not already installed:
```
wget https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage

chmod +x appimagetool-x86_64.AppImage
sudo mv appimagetool-x86_64.AppImage /usr/local/bin/appimagetool
```

**IMPORTANT: Set AppRun inside InvoiceBuddy.AppDir as an executable file prior to building the AppImage**

After building, copy invoice-buddy to packaging/InvoiceBuddy.AppDir/usr/bin

Run this command from the root directory:
```
appimagetool packaging/InvoiceBuddy.AppDir InvoiceBuddy-Linux.AppImage -v
```

## DEBIAN

For a Debian (.deb) file, follow these steps after building the file with the command listed earlier.

Copy built file to deb directory:
```
mkdir -p packaging/deb/usr/bin
cp dist/invoice-buddy packaging/deb/usr/bin/invoice-buddy
```

Set permissions:
```
find packaging/deb -type d -exec chmod 755 {} +
find packaging/deb/usr/bin -type f -exec chmod 755 {} +
find packaging/deb/DEBIAN -type f -exec chmod 755 {} +
find packaging/deb -type f ! -path "*/DEBIAN/*" -exec chmod 644 {} +
chmod 755 packaging/deb/usr/bin/invoice-buddy
find packaging/deb -type f ! -path "*/DEBIAN/*" -exec chmod 644 {} +
```

Build DEB:
```
fakeroot dpkg-deb --build packaging/deb "InvoiceBuddy-Linux-${VERSION}.deb"
```

Set permissions for .deb file:
```
chmod 644 "InvoiceBuddy-Linux-<version-number>.deb"
```

**Important: Make sure that you replace the version number properly to match the filename.**

## 🖥️ Windows

**IMPORTANT: Must have Visual Studio Build Tools installed with C++ / MSVC bindings**

### Pyinstaller

**Python 3.10+ recommended**

Open your IDE (VSCode recommended) and create a virtual environment using these commands:

```
python -m venv invoice_venv

invoice_venv\Scripts\Activate.ps1
```

Next, run these commands to install dependencies and build the file:

```
pip install -r packaging/requirements.txt
pip install pywin32

pyinstaller packaging/InvoiceBuddy-Linux.spec --clean
```

Invoice Buddy will be found in the dist/ folder.

### Nuitka

To build an executable with Nuitka, follow these instructions:

Build the app:
```
pip install -r packaging/requirements.txt

nuitka `
    --msvc=latest `
    --standalone `
    --remove-output `
    --enable-plugin=pyside6 `
    --include-qt-plugins=platforms `
    --enable-plugin=tk-inter `
    --windows-console-mode=disable `
    --output-dir=dist `
    --windows-icon-from-ico=defaults/assets/icon.ico `
    --include-package-data=pdf2image `
    --include-package-data=pytesseract `
    --include-data-dir=defaults=defaults `
    --include-raw-dir=bin=bin `
    --include-data-files=CHANGELOG.md=CHANGELOG.md `
    --include-data-files=README.md=README.md `
    --include-data-files=LICENSE.txt=LICENSE.txt `
    --file-version=0.2.9.0 `
    --product-version=0.2.9.0 `
    --company-name="Phillip Schneider" `
    --product-name="Invoice Buddy" `
    --file-description="Simplified invoice and receipt management" `
    --copyright="Copyright © 2026 Phillip Schneider. Apache 2.0." `
    --output-filename=InvoiceBuddy.exe `
    main.py
```

Make sure to update the product version and file version with the correct version number.

*Note: Nuitka builds can take significantly longer than Pyinstaller. Assume 5-10 minutes to complete.*

That's it! If you have any questions or run into any errors, you can report them via GitHub issues

*Up to date as of v0.2.9*