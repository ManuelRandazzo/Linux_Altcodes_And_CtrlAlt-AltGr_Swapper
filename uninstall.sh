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
echo "====================================="
echo "   AltcodesForLinux - Uninstaller"   
echo "====================================="
echo ""

# Root privileges check
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}[!] Root required: sudo bash uninstall.sh${NC}"
    exit 1
fi

# Stop service
if systemctl is-active --quiet "$SERVICE_NAME" 2>/dev/null; then
    echo -e "${YELLOW}[*] Stopping service...${NC}"
    systemctl stop "$SERVICE_NAME"
    echo -e "${GREEN}[+] Done${NC}"
fi

# Disable service
if systemctl is-enabled --quiet "$SERVICE_NAME" 2>/dev/null; then
    echo -e "${YELLOW}[*] Disabling service...${NC}"
    systemctl disable "$SERVICE_NAME"
    echo -e "${GREEN}[+] Done${NC}"
fi

# Remove service file
if [ -f "$SERVICE_PATH" ]; then
    echo -e "${YELLOW}[*] Removing service in $SERVICE_PATH...${NC}"
    rm -f "$SERVICE_PATH"
    echo -e "${GREEN}[+] Done${NC}"
    
    # daemon reload
    echo -e "${YELLOW}[*] Reloading daemon...${NC}"
    systemctl daemon-reload
    echo -e "${GREEN}[+] Done${NC}"
fi

# Remove script
if [ -f "$INSTALL_PATH" ]; then
    echo -e "${YELLOW}[*] Removing script in $INSTALL_PATH...${NC}"
    rm -f "$INSTALL_PATH"
    echo -e "${GREEN}[+] Done${NC}"
fi

# Remove autostart DE
if [ -f "$AUTOSTART_PATH" ]; then
    echo -e "${YELLOW}[+] Removing Desktop Environment autostart${NC}"
    rm -f "$AUTOSTART_PATH"
    echo -e "${GREEN}[+] Done${NC}"
fi

# Remove user autostart
REAL_USER="${SUDO_USER:-$USER}"
USER_AUTOSTART="/home/$REAL_USER/.config/autostart/${SERVICE_NAME}.desktop"
if [ -f "$USER_AUTOSTART" ]; then
    echo -e "${YELLOW}[+] Removing User's autostart${NC}"
    rm -f "$USER_AUTOSTART"
    echo -e "${GREEN}[+] Done${NC}"
fi

echo ""
echo -e "${RED}======================================================================="
echo "   ATTENTION: You need to remove dependencies (python3, python3-evdev)"
echo "              manually, be careful!"
echo -e "=======================================================================${NC}"
echo ""
echo ""
echo -e "${GREEN}========================================"
echo "   Uninstallation completed!"
echo -e "========================================${NC}"
echo ""
