# Linux Altcodes And Ctrl+Alt<->AltGr Swapper

## Table of Contents
- [What it does](#what-it-does)
    - [Alt codes](#alt-codes)
    - [Ctrl+Alt <-> AltGr swap](#ctrlalt---altgr-swap)
    - [Automatic keyboard detection](#automatic-keyboard-detection)
- [Dependencies to install](#dependencies-to-install)
- [Python script additional arguments](#python-script-additional-arguments)
- [Test script before installation](#test-script-before-installation)
- [Installation](#installation)
- [Autostart at boot](#autostart-at-boot)
    - [Systemd (recommended, works on all DEs)](#systemd-recommended-works-on-all-des)
    - [GNOME](#gnome)
    - [KDE Plasma](#kde-plasma)
    - [XFCE](#xfce)
    - [Cinnamon / MATE](#cinnamon--mate)
- [Uninstallation](#uninstallation)
- [Running without root](#running-without-root)
- [How to contribute to this project](#how-to-contribute-to-this-project)
- [Notes](#notes)

---

## What it does
A Python daemon that translates **Windows alt codes** into Unicode characters on Linux, and adds a **swap between Ctrl+Alt and AltGr** (and vice versa).

### Alt codes
On Windows, special characters can be inserted by holding Alt and typing a number on the numpad (e.g. `Alt+0169` → `©`).
This does not work natively on Linux. This script intercepts that combination and converts it into the `Ctrl+Shift+U → hex code → Enter` sequence, which is the standard GTK/X11/Wayland method for inserting arbitrary Unicode characters.

Both Windows codepages are supported:
- Codes starting with `0` → **CP1252** (e.g. `Alt+0169` → `©`)
- Codes without the leading `0` → **CP850** (DOS legacy, e.g. `Alt+169` → `⌐`)

### Ctrl+Alt <-> AltGr swap
- **Ctrl+Alt** or **Alt+Ctrl** → sends **AltGr**
- **Physical AltGr** → sends **Ctrl+Alt**

Useful for users accustomed to the Windows Ctrl+Alt combination.
**Note**: shortcuts will be changed. For example if you were used to open terminal with 'Ctrl+Alt+T' with this python script it will be necessary to use 'AltGr+T', thus be careful!

### Automatic keyboard detection
When launched without arguments, the script automatically detects all connected keyboards and handles them in parallel. If a keyboard is disconnected and reconnected, it is picked up again automatically without restarting the script.

---

## Dependencies to install
```bash
# Debian / Ubuntu / Mint
sudo apt install python3 python3-evdev

# Arch / EndeavourOS / Manjaro
sudo pacman -S python3 python3-evdev

# Fedora
sudo dnf install python3 python3-evdev

# Or via pip
pip3 install evdev --break-system-packages
```

---

## Python script additional arguments
    - **--list**: List all input devices and exit.
    ```bash
    # Usage example
    altcodesforlinux.py --list

    # print example
    /dev/input/event7 (/dev/input/event7) - UInput pointer
    /dev/input/event6 (/dev/input/event6) - py-evdev-uinput
    /dev/input/by-path/platform-pcspkr-event-spkr (/dev/input/event5) - py-evdev-uinput
    /dev/input/by-path/pci-xxx (/dev/input/event4) - USB Mouse
    /dev/input/by-path/platform-i8042-serio-1-event-mouse (/dev/input/event3) - mouse
    /dev/input/by-path/platform-i8042-serio-0-vent-kbd (/dev/input/event2) - AT Trans
    /dev/input/by-path/platform-event (/dev/input/event1) - keyboard
    /dev/input/by-path/platform-xxxxxx-event (/dev/input/event0) - Power Button
    ```
    **note**: the ***py-evdev-uinput*** device is the virtual keyboard created by the python script

    - **device**: Specify a device listed in /dev/input/ . If omitted, auto-detects all keyboards by-path or by id.
    ```bash
    # Usage example
    altcodesforlinux.py device /dev/input/event1
    ```
    
    - **-d** or **--daemon**: Daemon mode (only with specific device): keep retrying if device disconnects.
    ```bash
    # Usage example
    altcodesforlinux.py --daemon /dev/input/event1
    ```
---

## Test script before installation
```bash
# Auto-detect all keyboards
sudo python3 altcodesforlinux.py

# Specific device
sudo python3 altcodesforlinux.py /dev/input/event3

# Specific device with automatic reconnect
sudo python3 altcodesforlinux.py --daemon /dev/input/event3
```

---

## Installation
```bash
# switch to the directory (any in your system) where you want to clone this repo, for example
# cd ~/Downloads

# clone this repo
git clone https://github.com/ManuelRandazzo/Linux_Altcodes_And_CtrlAlt-AltGr_Swapper

# switch to repo's clone directory
cd Linux_Altcodes_And_CtrlAlt-AltGr_Swapper

# add executable permission to file "install.sh"
# ATTENTION: requires administrative (superuser) privileges with the 'sudo' command
sudo chmod +x install.sh

# run the installation script (interactive)
# ATTENTION: requires administrative (superuser) privileges with the 'sudo' command
sudo bash install.sh
```

The installer:
- Checks if it is running with 'sudo' (root privileges)
- Checks dependencies (python3 python3-evdev)
- Copies the script to the system in /usr/bin/
- Add executable flag to python script
- Adds uinput permissions in /etc/modules and loads it
- Adds the current user to the `input` group
- Installs and starts the systemd service
- Optionally installs autostart for desktop environments

---

## Autostart at boot
### Systemd (recommended, works on all DEs)
```bash
sudo systemctl enable altcodesforlinux
sudo systemctl start altcodesforlinux

# Check status
sudo systemctl status altcodesforlinux
```

### GNOME
```bash
cp altcodesforlinux.desktop ~/.config/autostart/
```
Or use **Startup Applications** from GNOME settings.

### KDE Plasma
```bash
cp altcodesforlinux.desktop ~/.config/autostart/
```
Or go to **System Settings → Startup and Shutdown → Autostart**.

### XFCE
```bash
cp altcodesforlinux.desktop ~/.config/autostart/
```
Or use **Settings → Session and Startup → Application Autostart**.

### Cinnamon / MATE
```bash
cp altcodesforlinux.desktop ~/.config/autostart/
```

> **Note:** autostart via `.desktop` requires the user to have permissions on `/dev/input` and `/dev/uinput` (member of the `input` group). The systemd service runs as root and does not have this limitation. For most use cases, the systemd service is the simplest choice.

---

## Uninstallation
```bash
# switch to the directory (any in your system) where you want to clone this repo, for example
# cd ~/Downloads

# clone this repo
git clone https://github.com/ManuelRandazzo/Linux_Altcodes_And_CtrlAlt-AltGr_Swapper

# switch to repo's clone directory (if you have deleted the repo folder just clone it again)
cd Linux_Altcodes_And_CtrlAlt-AltGr_Swapper

# add executable permission to file "uninstall.sh"
# ATTENTION: requires administrative (superuser) privileges with the 'sudo' command
chmod +x uninstall.sh

# runs the uninstallation script
# ATTENTION: requires administrative (superuser) privileges with the 'sudo' command
sudo bash uninstall.sh
```

---

## Running without root
To run the script without sudo, the user must be in the `input` group and have access to `/dev/uinput`:
**ATTENTION** : This is automatically handled in the 'install.sh' script

```bash
sudo usermod -aG input $USER
sudo bash -c 'echo "KERNEL==\"uinput\", GROUP=\"input\", MODE=\"0660\"" > /etc/udev/rules.d/99-uinput.rules'
sudo udevadm control --reload-rules
# Log out and back in to apply
```

---

## How to contribute to this project
To help me improve this script feel free to **report bugs** or ask to **add features** following the proposed templates.

If you have already fixed something feel free to make a **pull request** following the proposed templates for features and bugs that I will personally review and eventually merge.

---

## Notes
- The script uses `dev.grab()` to exclusively capture physical keyboard events. This is required to remap modifiers (Ctrl, Alt and AltGr) without the system seeing both the physical keys and the virtual ones emitted by the script.
- While the script is running, no other process can open the same device. Stop the service before testing manually.
- If you use **keyd** or other remapping tools, point the script to the virtual device created by keyd instead of the physical keyboard.