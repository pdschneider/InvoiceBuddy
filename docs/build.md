# 🚀 Build

Invoice Buddy can be built from source code via Pyinstaller on both Windows and Linux as well as Nuitka on Linux. This is for advanced users only - the simplest way to run Pearl is to download the latest release.

## 🐧 Linux

Open your IDE (VSCode recommended) and create a virtual environment using these commands:

```
python3 -m venv invoice_venv

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

**IMPORTANT: Must have patchelf installed: `sudo apt patchelf`**

Install appimagetool if not already installed:
```
wget https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage

chmod +x appimagetool-x86_64.AppImage
sudo mv appimagetool-x86_64.AppImage /usr/local/bin/appimagetool
```

Build the App:
```
pip install -r packaging/requirements.txt

nuitka \
    --standalone \
    --onefile \
    --remove-output \
    --output-dir=dist \
    --enable-plugin=pyside6 \
    --enable-plugin=tk-inter \
    --include-qt-plugins=platforms,iconengines,imageformats \
    --include-data-dir=defaults=defaults \
    --include-data-files=CHANGELOG.md=CHANGELOG.md \
    --include-data-files=README.md=README.md \
    invoicebuddy.py
```

*Note: Nuitka builds can take significantly longer than Pyinstaller. Assume 5-10 minutes to complete.*

**IMPORTANT: Set AppRun inside InvoiceBuddy.AppDir as an executable file prior to building the AppImage**

After building, copy InvoiceBuddy-Linux to packaging/InvoiceBuddy.AppDir/usr/bin

Run this command from the root directory:

```
appimagetool packaging/InvoiceBuddy.AppDir InvoiceBuddy-Linux.AppImage -v
```

## 🖥️ Windows

**IMPORTANT: Must have Visual Studio Build Tools installed with C++ / MSVC bindings**

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

That's it! If you have any questions or run into any errors, you can report them via GitHub issues
