#!/usr/bin/env python3

import argparse
import evdev
import time
import sys
import threading
import os


hexKeyMap = {
    '0': evdev.ecodes.KEY_0,
    '1': evdev.ecodes.KEY_1,
    '2': evdev.ecodes.KEY_2,
    '3': evdev.ecodes.KEY_3,
    '4': evdev.ecodes.KEY_4,
    '5': evdev.ecodes.KEY_5,
    '6': evdev.ecodes.KEY_6,
    '7': evdev.ecodes.KEY_7,
    '8': evdev.ecodes.KEY_8,
    '9': evdev.ecodes.KEY_9,
    'A': evdev.ecodes.KEY_A,
    'B': evdev.ecodes.KEY_B,
    'C': evdev.ecodes.KEY_C,
    'D': evdev.ecodes.KEY_D,
    'E': evdev.ecodes.KEY_E,
    'F': evdev.ecodes.KEY_F,
}
numpadKeyMap = {
    evdev.ecodes.KEY_KP0: '0',
    evdev.ecodes.KEY_KP1: '1',
    evdev.ecodes.KEY_KP2: '2',
    evdev.ecodes.KEY_KP3: '3',
    evdev.ecodes.KEY_KP4: '4',
    evdev.ecodes.KEY_KP5: '5',
    evdev.ecodes.KEY_KP6: '6',
    evdev.ecodes.KEY_KP7: '7',
    evdev.ecodes.KEY_KP8: '8',
    evdev.ecodes.KEY_KP9: '9',
}


def is_keyboard(dev):
    try:
        # Excludes virtual devices created by evdev/uinput
        if 'uinput' in dev.name.lower() or 'virtual' in dev.name.lower():
            return False

        caps = dev.capabilities()
        if evdev.ecodes.EV_KEY not in caps:
            return False
        keys = set(caps[evdev.ecodes.EV_KEY])
        required = {
            evdev.ecodes.KEY_A,
            evdev.ecodes.KEY_Z,
            evdev.ecodes.KEY_0,
            evdev.ecodes.KEY_9,
            evdev.ecodes.KEY_SPACE,
            evdev.ecodes.KEY_ENTER,
            evdev.ecodes.KEY_LEFTSHIFT,
            evdev.ecodes.KEY_LEFTCTRL,
            evdev.ecodes.KEY_LEFTALT,
            evdev.ecodes.KEY_BACKSPACE,
            evdev.ecodes.KEY_TAB,
            evdev.ecodes.KEY_ESC,
            evdev.ecodes.KEY_F1,
            evdev.ecodes.KEY_F5,
        }
        if not required.issubset(keys):
            return False

        # Excludes mouses and pointing devices
        if evdev.ecodes.EV_REL in caps:
            rel_axes = set(caps[evdev.ecodes.EV_REL])
            if evdev.ecodes.REL_X in rel_axes and evdev.ecodes.REL_Y in rel_axes:
                return False

        return True
    except Exception:
        return False


def set_numlock(dev):
    try:
        caps = dev.capabilities()
        if (evdev.ecodes.EV_LED in caps and
                evdev.ecodes.LED_NUML in caps[evdev.ecodes.EV_LED]):
            dev.set_led(evdev.ecodes.LED_NUML, 1)
    except Exception:
        pass


def get_stable_id(path):
    """Returns the stable path 'by-path' corrisponding to eventX, or just path 'by-id' if it doesn't exist"""
    try:
        real = os.path.realpath(path)
        for by_dir in ['/dev/input/by-path', '/dev/input/by-id']:
            if os.path.isdir(by_dir):
                for entry in os.listdir(by_dir):
                    full = os.path.join(by_dir, entry)
                    if os.path.realpath(full) == real:
                        return full
    except Exception:
        pass
    return path


def handle_device(path):
    try:
        dev = evdev.InputDevice(path)

        if not is_keyboard(dev):
            dev.close()
            return

        dev.grab()
        set_numlock(dev)
        print(f'[+] Grabbed: {dev.name} ({path})')

        vinput = evdev.UInput()

        currentAltCode = None
        ctrl_held     = False
        alt_held      = False
        ctrl_alt_mode = False
        alt_pending   = False

        for event in dev.read_loop():
            if event.type != evdev.ecodes.EV_KEY:
                continue
            keyEvent = evdev.events.KeyEvent(event)
            sc = keyEvent.scancode
            ks = keyEvent.keystate

            # ── LEFT CTRL ────────────────────────────────────────────────────
            if sc == evdev.ecodes.KEY_LEFTCTRL:
                if ks == 1:
                    ctrl_held = True
                    if alt_held and not ctrl_alt_mode:
                        alt_pending    = False
                        currentAltCode = None
                        vinput.write(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_RIGHTALT, 1)
                        vinput.syn()
                        ctrl_alt_mode = True
                    elif not ctrl_alt_mode:
                        vinput.write(evdev.ecodes.EV_KEY, sc, ks)
                        vinput.syn()
                elif ks == 0:
                    ctrl_held = False
                    if ctrl_alt_mode:
                        if not alt_held:
                            vinput.write(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_RIGHTALT, 0)
                            vinput.syn()
                            ctrl_alt_mode = False
                    else:
                        vinput.write(evdev.ecodes.EV_KEY, sc, ks)
                        vinput.syn()
                else:
                    if not ctrl_alt_mode:
                        vinput.write(evdev.ecodes.EV_KEY, sc, ks)
                        vinput.syn()

            # ── LEFT ALT ─────────────────────────────────────────────────────
            elif sc == evdev.ecodes.KEY_LEFTALT:
                if ks == 1:
                    alt_held = True
                    if ctrl_held and not ctrl_alt_mode:
                        vinput.write(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_LEFTCTRL, 0)
                        vinput.syn()
                        vinput.write(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_RIGHTALT, 1)
                        vinput.syn()
                        ctrl_alt_mode = True
                    elif not ctrl_alt_mode:
                        currentAltCode = ''
                        alt_pending    = True

                elif ks == 0:
                    alt_held = False
                    if ctrl_alt_mode:
                        if not ctrl_held:
                            vinput.write(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_RIGHTALT, 0)
                            vinput.syn()
                            ctrl_alt_mode = False
                    else:
                        if alt_pending:
                            vinput.write(evdev.ecodes.EV_KEY, sc, 1)
                            vinput.syn()
                            alt_pending = False

                        if not currentAltCode:
                            vinput.write(evdev.ecodes.EV_KEY, sc, ks)
                            vinput.syn()
                            currentAltCode = None
                            continue

                        codepage    = 'cp1252' if currentAltCode[0] == '0' else 'cp850'
                        altCodeDec  = int(currentAltCode)
                        altCodeChar = ord(altCodeDec.to_bytes(1, 'big').decode(codepage))
                        altCodeHex  = ('%0.2X' % altCodeChar).upper()
                        print('ALTCODE:', currentAltCode, '('+str(altCodeDec)+')',
                              '-->', '0x'+altCodeHex, '[ '+chr(altCodeChar)+' ]')
                        currentAltCode = None

                        vinput.write(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_LEFTCTRL,  1)
                        vinput.write(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_LEFTSHIFT, 1)
                        vinput.write(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_U,         1)
                        vinput.syn()
                        vinput.write(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_LEFTCTRL,  0)
                        vinput.write(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_LEFTSHIFT, 0)
                        vinput.write(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_U,         0)
                        vinput.syn()
                        for char in altCodeHex:
                            if char in hexKeyMap:
                                vinput.write(evdev.ecodes.EV_KEY, hexKeyMap[char], 1)
                                vinput.syn()
                                vinput.write(evdev.ecodes.EV_KEY, hexKeyMap[char], 0)
                                vinput.syn()
                        vinput.write(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_ENTER, 1)
                        vinput.syn()
                        vinput.write(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_ENTER, 0)
                        vinput.syn()

                        vinput.write(evdev.ecodes.EV_KEY, sc, 1)
                        vinput.syn()
                        vinput.write(evdev.ecodes.EV_KEY, sc, 0)
                        vinput.syn()

                        set_numlock(dev)

                else:
                    if alt_pending:
                        vinput.write(evdev.ecodes.EV_KEY, sc, 1)
                        vinput.syn()
                        alt_pending = False
                    if not ctrl_alt_mode:
                        vinput.write(evdev.ecodes.EV_KEY, sc, ks)
                        vinput.syn()

            # ── RIGHT ALT (AltGr) → Ctrl+Alt ─────────────────────────────────
            elif sc == evdev.ecodes.KEY_RIGHTALT:
                if ks == 1:
                    vinput.write(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_LEFTCTRL, 1)
                    vinput.syn()
                    vinput.write(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_LEFTALT,  1)
                    vinput.syn()
                elif ks == 0:
                    vinput.write(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_LEFTALT,  0)
                    vinput.syn()
                    vinput.write(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_LEFTCTRL, 0)
                    vinput.syn()

            # ── Numpad during an alt code ───────────────────────────────────
            elif sc in numpadKeyMap and currentAltCode is not None:
                if ks == 1:
                    currentAltCode += numpadKeyMap[sc]

            # ── Anything else ──────────────────────────
            else:
                if alt_pending:
                    vinput.write(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_LEFTALT, 1)
                    vinput.syn()
                    alt_pending = False
                vinput.write(evdev.ecodes.EV_KEY, sc, ks)
                vinput.syn()

        vinput.close()

    except PermissionError as e:
        print(f'[-] Permission denied on {path}: {e}')
    except OSError as e:
        print(f'[-] Device removed: {path} ({e})')
    except Exception as e:
        print(f'[-] Error on {path}: {type(e).__name__}: {e}')
    finally:
        try:
            dev.close()
        except Exception:
            pass


def auto_detect():
    active     = {}   # eventX path -> thread
    grabbed_ids = set()  # stable by-id path grabbed
    print('[*] Auto-detect active, listening for keyboards...')

    while True:
        try:
            current_paths = set(evdev.list_devices())
        except Exception as e:
            print(f'[-] Error listing devices: {e}')
            time.sleep(1)
            continue

        for path in current_paths:
            stable_id = get_stable_id(path)

            # Skips if this device has been already grabbed
            if stable_id in grabbed_ids:
                continue

            # Skips if thread is still alive
            if path in active and active[path].is_alive():
                continue

            try:
                dev = evdev.InputDevice(path)
                if is_keyboard(dev):
                    dev.close()
                    grabbed_ids.add(stable_id)
                    t = threading.Thread(
                        target=handle_device,
                        args=(path,),
                        daemon=True
                    )
                    t.start()
                    active[path] = t
                    print(f'[*] Keyboard detected: {dev.name} ({stable_id})')
                else:
                    dev.close()
            except OSError:
                pass
            except Exception as e:
                print(f'[-] Could not open {path}: {e}')

        # Clean up: removes unactive device id
        active      = {p: t for p, t in active.items() if t.is_alive()}
        grabbed_ids = {get_stable_id(p) for p in active}

        time.sleep(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Translate alt codes into Unicode keystrokes and swap Ctrl+Alt with AltGr'
    )
    parser.add_argument(
        'device', nargs='?', default=None,
        help='Specific device (e.g. /dev/input/event1). If omitted, auto-detects all keyboards.'
    )
    parser.add_argument(
        '-d', '--daemon', action='store_true',
        help='Daemon mode (only with specific device): keep retrying if device disconnects.'
    )
    parser.add_argument(
        '--list', action='store_true',
        help='List all input devices and exit.'
    )
    args = parser.parse_args()

    if args.list:
        for path in evdev.list_devices():
            try:
                dev = evdev.InputDevice(path)
                kb = is_keyboard(dev)
                stable = get_stable_id(path)
                print(f'{"[KB]" if kb else "    "} {stable} ({path}) - {dev.name}')
                dev.close()
            except Exception:
                pass
        sys.exit(0)

    if args.device:
        while True:
            try:
                time.sleep(0.2)
                handle_device(args.device)
            except (FileNotFoundError, OSError) as e:
                print(type(e), e)
                if args.daemon:
                    time.sleep(1)
                else:
                    sys.exit(1)
    else:
        try:
            auto_detect()
        except KeyboardInterrupt:
            print('\n[*] Exit.')
            sys.exit(0)
