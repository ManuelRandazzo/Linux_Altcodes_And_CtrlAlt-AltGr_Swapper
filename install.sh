#!/bin/bash

set -e

SERVICE_NAME="altcodesforlinux"
SERVICE_PATH="/etc/systemd/system/${SERVICE_NAME}.service"
SCRIPT_NAME="${SERVICE_NAME}.py"
INSTALL_PATH="/usr/bin/${SCRIPT_NAME}"
AUTOSTART_PATH="/etc/xdg/autostart/${SERVICE_NAME}.desktop"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo "==================================="
echo "   AltcodesForLinux - Installer"
echo "==================================="
echo ""

# Root privileges check
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}[!] Root required: sudo bash install.sh${NC}"
    exit 1
fi

# Dependencies
echo -e "${YELLOW}[*] Checking dependencies...${NC}"
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}[!] package 'python3' not found. Install this package and run 'install.sh' again${NC}"
    exit 1
fi
if ! python3 -c "import evdev" &>/dev/null; then
    echo -e "${RED}[!] package 'python3-evdev' not found. Install this package and run 'install.sh' again${NC}"
    exit 1
fi
echo -e "${GREEN}[+] All dependencies installed${NC}"

# Copies the script in "/usr/bin/"
echo -e "${YELLOW}[*] Running installation script in $INSTALL_PATH${NC}...${NC}"
cp "$SCRIPT_NAME" "$INSTALL_PATH"
echo -e "${GREEN}[+] Done${NC}"

echo -e "${YELLOW}[*] Adding Executable flag (+x) to $SCRIPT_NAME..."
chmod +x "$INSTALL_PATH"
echo -e "${GREEN}[+] Done $INSTALL_PATH${NC}"

# uinput permissions
if ! grep -q 'uinput' /etc/modules 2>/dev/null; then
    echo -e "${YELLOW}[*] Adding 'uinput' in /etc/modules ..."
    echo 'uinput' >> /etc/modules
    echo -e "${GREEN}[+] Done $INSTALL_PATH${NC}"
fi
echo -e "${YELLOW}[*] Asking the system to load 'uinput'..."
modprobe uinput 2>/dev/null || true
echo -e "${GREEN}[+] Done $INSTALL_PATH${NC}"
if [ -e /dev/uinput ]; then
    chmod 660 /dev/uinput
    chown root:input /dev/uinput 2>/dev/null || true
fi

# Adds user to input group
echo -e "${YELLOW}[*] Adding user to input group..."
REAL_USER="${SUDO_USER:-$USER}"
if id -nG "$REAL_USER" | grep -qw input; then
    echo -e "${GREEN}[+] Done. $REAL_USER was added to input group yet${NC}"
else
    usermod -aG input "$REAL_USER"
    echo -e "${GREEN}[+] Done. $REAL_USER added to input group${NC}"
fi

# Installs systemd service
echo -e "${YELLOW}[*] Installing systemd service...${NC}"
cat > "$SERVICE_PATH" <<EOF
[Unit]
Description=AltcodesForLinux - Alt codes and swap Ctrl+Alt <-> AltGr
After=multi-user.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 $INSTALL_PATH
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF
echo -e "${GREEN}[+] Done $INSTALL_PATH${NC}"

# Daemon reload
echo -e "${YELLOW}[*] Reloading daemon...${NC}"
systemctl daemon-reload
echo -e "${GREEN}[+] Done $INSTALL_PATH${NC}"


# Ask whether to enable autostart at boot
echo ""
read -r -p "Enable automatic startup at boot? [y/N] " INSTALL_AUTOSTART

# Reload systemd configuration
echo -e "${YELLOW}[*] Reloading daemon...${NC}"
systemctl daemon-reload

if [[ "$INSTALL_AUTOSTART" =~ ^[Yy]$ ]]; then
    # Enable and start the service
    echo -e "${YELLOW}[*] Enabling service at boot...${NC}"
    systemctl enable "$SERVICE_NAME"

    echo -e "${YELLOW}[*] Starting service...${NC}"
    systemctl restart "$SERVICE_NAME"

    echo -e "${GREEN}[+] Autostart enabled${NC}"
else
    # Make sure a previous installation did not leave autostart enabled
    echo -e "${YELLOW}[*] Disabling automatic startup...${NC}"
    systemctl disable "$SERVICE_NAME" 2>/dev/null || true

    # Remove any previous desktop autostart entries
    rm -f "$AUTOSTART_PATH"

    REAL_USER="${SUDO_USER:-$USER}"
    USER_AUTOSTART="/home/$REAL_USER/.config/autostart/${SERVICE_NAME}.desktop"
    rm -f "$USER_AUTOSTART"

    # Keep the program running in the current session
    echo -e "${YELLOW}[*] Starting service for this session only...${NC}"
    systemctl restart "$SERVICE_NAME"

    echo -e "${GREEN}[+] Autostart disabled${NC}"
fi


echo ""
echo -e "${YELLOW}========================================"
echo "  check the service status with :"
echo "     sudo systemctl status $SERVICE_NAME"
echo ""
echo "  Reboot or logout/login to apply changes to the input group ."
echo -e "========================================${NC}"
echo ""
echo ""
echo -e "${GREEN}========================================"
echo "   Installation completed!"
echo -e "========================================${NC}"
echo ""
