#!/usr/bin/env python3
# type: ignore[reportGeneralTypeIssues]
"""
Pegasus v3.0 - Android Device Management & Advanced Penetration Testing Tool
Created for educational purposes only
Use this tool ONLY on devices you own or have explicit permission to test
Total Lines: 2150+ | Full Pentest Suite
"""

# ==================== IMPORTAÇÃO DE BIBLIOTECAS ====================
import subprocess
import shutil
import sys
import os
import time
import re
import datetime
import tempfile
import threading
import signal
import json
import hashlib
import base64
import random
import string
import socket
import struct
import platform
import getpass
from pathlib import Path

# ==================== CONFIGURAÇÕES DE CORES ====================
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
RED = "\033[1;31m"
CYAN = "\033[1;36m"
BLUE = "\033[1;34m"
MAGENTA = "\033[1;35m"
WHITE = "\033[1;37m"
RESET = "\033[0m"
BOLD = "\033[1m"

# ==================== BANNER DO PROGRAMA ====================
BANNER = r"""
██████╗ ███████╗ ██████╗  █████╗ ███████╗██╗   ██╗███████╗
██╔══██╗██╔════╝██╔════╝ ██╔══██╗██╔════╝██║   ██║██╔════╝
██████╔╝█████╗  ██║  ███╗███████║███████╗██║   ██║███████╗
██╔═══╝ ██╔══╝  ██║   ██║██╔══██║╚════██║██║   ██║╚════██║
██║     ███████╗╚██████╔╝██║  ██║███████║╚██████╔╝███████╗
╚═╝     ╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚══════╝                                                     
"""

HEADER_LINES = [
    " Pegasus v-3.0 | Full Pentest Edition | 2150+ lines",
    " Android Device Management & Advanced Security Tool ",
    " Use For Educational Purpose Only ",
    " Author: thakur2309 | Enhanced for Pentesting "
]

# ==================== VARIÁVEIS GLOBAIS ====================
connected_devices = {}
keylogger_active = False
keylogger_file = "keylog_capture.txt"
screenshot_count = 0
recording_count = 0
current_device = None
pentest_results = []

# ==================== FUNÇÕES AUXILIARES ====================

def check_dependency(cmd_name, apt_pkg_name=None):
    """Verifica se um comando está instalado no sistema"""
    path = shutil.which(cmd_name)
    if not path and apt_pkg_name:
        print(YELLOW + f"[!] {cmd_name} not found. Install: sudo apt install {apt_pkg_name} -y" + RESET)
    return bool(path)

def run_cmd(cmd: str, capture: bool = False, timeout: int = 30):
    """Executa comando shell com timeout"""
    try:
        if capture:
            res = subprocess.run(cmd, shell=True, check=False, 
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                text=True, timeout=timeout)
            return res.stdout.strip() if res.stdout else "", res.stderr.strip() if res.stderr else ""
        else:
            subprocess.call(cmd, shell=True, timeout=timeout)
            return "", ""
    except subprocess.TimeoutExpired:
        return "", "Command timed out after {} seconds".format(timeout)
    except Exception as e:
        return "", str(e)

def run_cmd_background(cmd: str):
    """Executa comando em background"""
    try:
        subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(RED + f"Error: {e}" + RESET)

def adb_available():
    return check_dependency("adb", "adb")

def scrcpy_available():
    return check_dependency("scrcpy", "scrcpy")

def nmap_available():
    return check_dependency("nmap", "nmap")

def metasploit_available():
    return check_dependency("msfconsole", "metasploit-framework")

def clear_screen():
    os.system("clear" if os.name == "posix" else "cls")

def print_banner():
    clear_screen()
    print(GREEN + BANNER + RESET)
    for line in HEADER_LINES:
        print(CYAN + line.center(60) + RESET)
    print(WHITE + "="*65 + RESET)
    print()

def print_status(message, status="info"):
    """Imprime mensagem com status colorido"""
    if status == "success":
        print(GREEN + "[✓] " + message + RESET)
    elif status == "error":
        print(RED + "[✗] " + message + RESET)
    elif status == "warning":
        print(YELLOW + "[!] " + message + RESET)
    elif status == "info":
        print(CYAN + "[*] " + message + RESET)
    else:
        print(message)

# ==================== FUNÇÕES DO ADB AVANÇADAS ====================

def adb_devices_list():
    """Lista todos os dispositivos conectados via ADB"""
    out, err = run_cmd("adb devices", capture=True)
    if out is None or err:
        return []
    lines = out.splitlines()
    devices = []
    for line in lines[1:]:
        line = line.strip()
        if line and "device" in line and "offline" not in line:
            parts = line.split()
            devices.append(parts[0])
    return devices

def get_selected_device():
    """Obtém dispositivo selecionado pelo usuário"""
    global current_device
    devices = adb_devices_list()
    if not devices:
        print_status("No device detected. Please connect via USB with USB Debugging enabled.", "error")
        print_status("Settings -> Developer options -> USB debugging", "warning")
        input("\nPress Enter after connecting...")
        return None
    if len(devices) == 1:
        current_device = devices[0]
        print_status(f"Device selected: {current_device}", "success")
        return current_device
    else:
        print_status("Multiple devices detected:", "info")
        for i, dev in enumerate(devices, 1):
            # Tenta obter modelo do dispositivo
            model, _ = run_cmd(f"adb -s {dev} shell getprop ro.product.model", capture=True)
            model_display = f" ({model})" if model else ""
            print(f"  {i}. {dev}{model_display}")
        while True:
            try:
                choice = int(input("Select device number: "))
                if 1 <= choice <= len(devices):
                    current_device = devices[choice - 1]
                    print_status(f"Device selected: {current_device}", "success")
                    return current_device
                else:
                    print_status("Invalid choice.", "error")
            except ValueError:
                print_status("Enter a valid number.", "error")

def adb_shell(device, command):
    """Executa comando shell no dispositivo"""
    return run_cmd(f"adb -s {device} shell {command}", capture=True)

def adb_push(device, local, remote):
    """Envia arquivo para o dispositivo"""
    return run_cmd(f"adb -s {device} push {local} {remote}", capture=True)

def adb_pull(device, remote, local):
    """Puxa arquivo do dispositivo"""
    return run_cmd(f"adb -s {device} pull {remote} {local}", capture=True)

def adb_install(device, apk_path):
    """Instala APK no dispositivo"""
    return run_cmd(f"adb -s {device} install -r {apk_path}", capture=True)

def adb_uninstall(device, package):
    """Desinstala pacote do dispositivo"""
    return run_cmd(f"adb -s {device} uninstall {package}", capture=True)

def get_device_info(device):
    """Obtém informações completas do dispositivo"""
    info = {}
    props = [
        ("brand", "ro.product.brand"),
        ("model", "ro.product.model"),
        ("device", "ro.product.device"),
        ("android_version", "ro.build.version.release"),
        ("sdk_version", "ro.build.version.sdk"),
        ("security_patch", "ro.build.version.security_patch"),
        ("build_id", "ro.build.id"),
        ("build_date", "ro.build.date"),
        ("fingerprint", "ro.build.fingerprint"),
        ("hardware", "ro.hardware"),
        ("cpu_abi", "ro.product.cpu.abi"),
        ("manufacturer", "ro.product.manufacturer"),
        ("board", "ro.product.board"),
        ("bootloader", "ro.bootloader"),
        ("radio", "ro.radio"),
        ("serial", "ro.serialno"),
    ]
    for key, prop in props:
        out, _ = adb_shell(device, f"getprop {prop}")
        info[key] = out if out else "Unknown"
    
    # Bateria
    batt_out, _ = adb_shell(device, "dumpsys battery")
    for line in (batt_out or "").splitlines():
        if "level" in line:
            info["battery_level"] = line.split(":")[1].strip()
        if "status" in line:
            info["battery_status"] = line.split(":")[1].strip()
    
    # Memória
    mem_out, _ = adb_shell(device, "cat /proc/meminfo | head -3")
    if mem_out:
        lines = mem_out.splitlines()
        info["total_ram"] = lines[0].split(":")[1].strip() if len(lines) > 0 else "Unknown"
        info["free_ram"] = lines[1].split(":")[1].strip() if len(lines) > 1 else "Unknown"
    
    # Armazenamento
    storage_out, _ = adb_shell(device, "df /data | tail -1")
    if storage_out:
        parts = storage_out.split()
        if len(parts) >= 4:
            info["total_storage"] = parts[1]
            info["used_storage"] = parts[2]
            info["free_storage"] = parts[3]
    
    return info

# ==================== LOG DE CONEXÕES ====================

def update_device_logs():
    """Atualiza logs de conexão dos dispositivos"""
    current_devices = adb_devices_list()
    now = datetime.datetime.now()
    
    for dev in list(connected_devices.keys()):
        if dev not in current_devices:
            start = connected_devices.pop(dev)
            duration = now - start
            with open("connection_log.txt", "a") as f:
                f.write(f"[{now}] {dev} DISCONNECTED - Duration: {duration}\n")
    
    for dev in current_devices:
        if dev not in connected_devices:
            connected_devices[dev] = now
            with open("connection_log.txt", "a") as f:
                # Tenta obter modelo para log
                model, _ = run_cmd(f"adb -s {dev} shell getprop ro.product.model", capture=True)
                model_str = f" ({model})" if model else ""
                f.write(f"[{now}] {dev}{model_str} CONNECTED\n")

def option_view_connection_history():
    """Visualiza histórico de conexões"""
    update_device_logs()
    if not os.path.exists("connection_log.txt"):
        print_status("No connection log yet.", "warning")
        return
    
    print_status("Device Connection History:", "info")
    print(CYAN + "="*60 + RESET)
    with open("connection_log.txt", "r") as f:
        print(f.read())
    print(CYAN + "="*60 + RESET)
    
    if connected_devices:
        now = datetime.datetime.now()
        print_status("Currently Connected:", "success")
        for dev, start in connected_devices.items():
            duration = now - start
            print(f"  {dev} - connected since {start} ({duration})")

# ==================== FUNÇÕES DO MENU PRINCIPAL ====================

def option_check_device():
    """Verifica informações detalhadas do dispositivo"""
    device = get_selected_device()
    if device is None:
        return
    
    print_status("Gathering device information...", "info")
    info = get_device_info(device)
    
    print("\n" + CYAN + "═"*50 + RESET)
    print(CYAN + "           DEVICE INFORMATION" + RESET)
    print(CYAN + "═"*50 + RESET)
    
    categories = {
        "Hardware": ["manufacturer", "brand", "model", "device", "hardware", "board", "cpu_abi"],
        "System": ["android_version", "sdk_version", "build_id", "build_date", "fingerprint"],
        "Security": ["security_patch", "bootloader", "radio"],
        "Resources": ["total_ram", "free_ram", "total_storage", "used_storage", "free_storage", "battery_level", "battery_status"]
    }
    
    for category, keys in categories.items():
        print(f"\n{BOLD}{YELLOW}[ {category} ]{RESET}")
        for key in keys:
            if key in info and info[key] != "Unknown":
                label = key.replace("_", " ").title()
                print(f"  {label}: {WHITE}{info[key]}{RESET}")
    
    print(CYAN + "═"*50 + RESET)
    
    # Salva informações em arquivo
    save = input("\nSave device info to file? (y/n): ").strip().lower()
    if save == "y":
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"device_info_{timestamp}.txt"
        with open(filename, "w") as f:
            json.dump(info, f, indent=4)
        print_status(f"Saved to {filename}", "success")

def option_connect_device():
    """Conecta dispositivo via WiFi ADB"""
    print_status("WiFi ADB Connection", "info")
    
    usb_devices = [d for d in adb_devices_list() if ':' not in d]
    
    if usb_devices:
        enable_tcpip = input("Enable ADB over WiFi on USB device? (y/n): ").strip().lower()
        if enable_tcpip == 'y':
            if len(usb_devices) > 1:
                print_status("Multiple USB devices:", "info")
                for i, dev in enumerate(usb_devices, 1):
                    print(f"  {i}. {dev}")
                choice = int(input("Select device: ")) - 1
                usb_device = usb_devices[choice]
            else:
                usb_device = usb_devices[0]
            
            print_status(f"Switching {usb_device} to TCPIP mode on port 5555...", "info")
            run_cmd(f"adb -s {usb_device} tcpip 5555")
            time.sleep(2)
            
            # Obtém IP do dispositivo USB
            ip_out, _ = adb_shell(usb_device, "ip addr show wlan0 | grep 'inet ' | awk '{print $2}' | cut -d/ -f1")
            if ip_out:
                print_status(f"Device IP: {ip_out}", "success")
                default_ip = ip_out
            else:
                default_ip = "192.168.1.x"
        else:
            default_ip = "192.168.1.x"
    else:
        default_ip = "192.168.1.x"
    
    ip = input(f"Enter device IP address [{default_ip}]: ").strip()
    if not ip:
        ip = default_ip.replace("x", "100")
    
    print_status(f"Connecting to {ip}:5555...", "info")
    out, err = run_cmd(f"adb connect {ip}:5555", capture=True)
    
    if "connected" in out.lower() or "already" in out.lower():
        print_status("Connected successfully over Wi-Fi!", "success")
        run_cmd("adb devices")
    else:
        print_status(f"Connection failed: {out or err}", "error")
        print_status("Make sure device and computer are on the same network", "warning")

def option_disconnect_device():
    """Desconecta dispositivos ADB"""
    print_status("Disconnecting ADB devices...", "info")
    
    tcp_devices = [d for d in adb_devices_list() if ':' in d]
    
    if not tcp_devices:
        print_status("No wireless devices connected.", "warning")
        print("\nCurrent devices:")
        run_cmd("adb devices")
        return
    
    print_status("Wireless devices:", "info")
    for i, dev in enumerate(tcp_devices, 1):
        print(f"  {i}. {dev}")
    print("  0. All devices")
    
    try:
        choice = int(input("Select device to disconnect: "))
        if choice == 0:
            run_cmd("adb disconnect")
            print_status("All wireless devices disconnected.", "success")
        elif 1 <= choice <= len(tcp_devices):
            run_cmd(f"adb disconnect {tcp_devices[choice-1]}")
            print_status(f"Disconnected: {tcp_devices[choice-1]}", "success")
        else:
            print_status("Invalid choice.", "error")
    except ValueError:
        print_status("Enter a number.", "error")

def option_screen_recording():
    """Grava a tela do dispositivo"""
    global recording_count
    device = get_selected_device()
    if device is None:
        return
    
    recording_count += 1
    filename = f"screen_record_{recording_count}.mp4"
    
    print_status("Screen Recording", "info")
    print("Options:")
    print("  1. Fixed duration")
    print("  2. Manual stop (Ctrl+C)")
    
    choice = input("Select option (1/2): ").strip()
    
    if choice == "1":
        duration = input("Enter duration in seconds: ").strip()
        try:
            dsec = int(duration)
            print_status(f"Recording for {dsec} seconds...", "info")
            run_cmd(f"adb -s {device} shell screenrecord --time-limit {dsec} /sdcard/{filename}")
        except ValueError:
            print_status("Invalid duration.", "error")
            return
    else:
        print_status("Recording until interrupted (Ctrl+C)...", "info")
        print_status("Press Ctrl+C to stop recording", "warning")
        try:
            proc = subprocess.Popen(f"adb -s {device} shell screenrecord /sdcard/{filename}", shell=True)
            proc.wait()
        except KeyboardInterrupt:
            proc.terminate()
            print_status("\nRecording stopped.", "info")
    
    print_status("Pulling recording to computer...", "info")
    run_cmd(f"adb -s {device} pull /sdcard/{filename} ./")
    run_cmd(f"adb -s {device} shell rm /sdcard/{filename}")
    
    if os.path.exists(filename):
        print_status(f"Recording saved as {filename}", "success")
        view = input("Open recording now? (y/n): ").strip().lower()
        if view == "y":
            opener = shutil.which("xdg-open") or "open" if sys.platform == "darwin" else "start"
            run_cmd(f"{opener} {filename}")
    else:
        print_status("Failed to save recording.", "error")

def option_screen_mirror():
    """Espelha tela com controle TOTAL via scrcpy"""
    device = get_selected_device()
    if device is None:
        return
    
    if not scrcpy_available():
        print_status("scrcpy not found!", "error")
        print_status("Install: sudo apt install scrcpy -y", "warning")
        return
    
    print_status("Starting screen mirror with FULL CONTROL...", "success")
    print_status("You can now control your Android device using mouse and keyboard!", "info")
    print_status("Keyboard shortcuts:", "info")
    print("  - Ctrl+C: Stop mirroring")
    print("  - Ctrl+Shift+F: Toggle fullscreen")
    print("  - Ctrl+Shift+Left/Right: Rotate screen")
    print("  - Ctrl+Shift+Up: Increase volume")
    print("  - Ctrl+Shift+Down: Decrease volume")
    print("  - Ctrl+Shift+P: Power button")
    print("  - Ctrl+Shift+H: Home button")
    print("  - Ctrl+Shift+B: Back button")
    print("  - Ctrl+Shift+M: Menu button")
    print("  - Ctrl+Shift+S: App switch")
    
    # Opções avançadas do scrcpy
    print("\nAdvanced options:")
    print("  1. Normal mode (default)")
    print("  2. Low resolution (faster)")
    print("  3. High bitrate (better quality)")
    print("  4. Turn screen off while mirroring")
    
    opt = input("Select option (1-4) [1]: ").strip()
    
    scrcpy_opts = f"-s {device}"
    if opt == "2":
        scrcpy_opts += " --max-size 1024"
    elif opt == "3":
        scrcpy_opts += " --bit-rate 8M"
    elif opt == "4":
        scrcpy_opts += " --turn-screen-off"
    
    print_status(f"Launching: scrcpy {scrcpy_opts}", "info")
    subprocess.Popen(f"scrcpy {scrcpy_opts}", shell=True)
    print_status("Mirror started! Close scrcpy window to return.", "success")

def option_show_apk_list():
    """Lista aplicativos instalados"""
    device = get_selected_device()
    if device is None:
        return
    
    print_status("Fetching installed packages...", "info")
    
    print("\nPackage types:")
    print("  1. User apps only")
    print("  2. System apps only")
    print("  3. All apps")
    
    choice = input("Select option (1-3): ").strip()
    
    if choice == "1":
        out, _ = adb_shell(device, "pm list packages -3")
        pkg_type = "User Apps"
    elif choice == "2":
        out, _ = adb_shell(device, "pm list packages -s")
        pkg_type = "System Apps"
    else:
        out, _ = adb_shell(device, "pm list packages")
        pkg_type = "All Apps"
    
    if not out:
        print_status("No packages found.", "warning")
        return
    
    packages = [line.replace("package:", "").strip() for line in out.splitlines() if line.strip()]
    
    print_status(f"{pkg_type}: {len(packages)} packages found", "success")
    
    # Opções de exibição
    print("\nDisplay options:")
    print("  1. Show all")
    print("  2. Search")
    print("  3. Save to file")
    
    disp = input("Select option (1-3): ").strip()
    
    if disp == "1":
        for pkg in packages:
            print(f"  {pkg}")
    elif disp == "2":
        search = input("Search term: ").strip().lower()
        matches = [p for p in packages if search in p.lower()]
        print_status(f"Found {len(matches)} matches:", "info")
        for m in matches[:50]:
            print(f"  {m}")
        if len(matches) > 50:
            print(f"  ... and {len(matches)-50} more")
    elif disp == "3":
        filename = f"apk_list_{pkg_type.replace(' ', '_').lower()}.txt"
        with open(filename, "w") as f:
            f.write(f"{pkg_type} ({len(packages)} packages)\n")
            f.write("="*50 + "\n")
            for pkg in packages:
                f.write(f"{pkg}\n")
        print_status(f"Saved to {filename}", "success")
    
    # Opção para obter informações detalhadas de um app
    detail = input("\nGet details for a package? (y/n): ").strip().lower()
    if detail == "y":
        pkg = input("Package name: ").strip()
        if pkg in packages or pkg:
            print_status(f"Getting info for {pkg}...", "info")
            dump_out, _ = adb_shell(device, f"dumpsys package {pkg} | grep -E 'versionName|versionCode|firstInstallTime|lastUpdateTime|uid|permission'")
            print(dump_out if dump_out else "No details available")

def option_take_screenshot():
    """Tira screenshot do dispositivo"""
    global screenshot_count
    device = get_selected_device()
    if device is None:
        return
    
    screenshot_count += 1
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"screenshot_{timestamp}.png"
    
    print_status("Taking screenshot...", "info")
    run_cmd(f"adb -s {device} shell screencap -p /sdcard/{filename}")
    print_status("Pulling screenshot...", "info")
    run_cmd(f"adb -s {device} pull /sdcard/{filename} ./")
    run_cmd(f"adb -s {device} shell rm /sdcard/{filename}")
    
    if os.path.exists(filename):
        print_status(f"Screenshot saved as {filename}", "success")
        view = input("Open screenshot now? (y/n): ").strip().lower()
        if view == "y":
            opener = shutil.which("xdg-open") or "open" if sys.platform == "darwin" else "start"
            run_cmd(f"{opener} {filename}")
    else:
        print_status("Failed to save screenshot.", "error")

def option_power_off():
    """Desliga o dispositivo"""
    device = get_selected_device()
    if device is None:
        return
    
    confirm = input(RED + "Are you sure you want to POWER OFF the device? (yes/no): " + RESET).strip().lower()
    if confirm == "yes":
        print_status("Sending power off command...", "warning")
        run_cmd(f"adb -s {device} shell reboot -p")
        print_status("Device is powering off.", "success")
    else:
        print_status("Cancelled.", "info")

def option_install_apk():
    """Instala APK no dispositivo"""
    device = get_selected_device()
    if device is None:
        return
    
    apk_path = input("Enter APK file path: ").strip()
    
    if not os.path.isfile(apk_path):
        print_status("File not found!", "error")
        return
    
    # Opções de instalação
    print("\nInstall options:")
    print("  1. Normal install")
    print("  2. Install for all users (-r)")
    print("  3. Install with permissions (-g)")
    print("  4. Install on SD card (-s)")
    
    opt = input("Select option (1-4): ").strip()
    
    install_opts = ""
    if opt == "2":
        install_opts = "-r"
    elif opt == "3":
        install_opts = "-g"
    elif opt == "4":
        install_opts = "-s"
    
    print_status(f"Installing {apk_path}...", "info")
    out, err = run_cmd(f"adb -s {device} install {install_opts} \"{apk_path}\"", capture=True, timeout=60)
    
    if "Success" in out:
        print_status("APK installed successfully!", "success")
    else:
        print_status(f"Installation failed: {out or err}", "error")

def option_delete_apk():
    """Desinstala aplicativo"""
    device = get_selected_device()
    if device is None:
        return
    
    package = input("Enter package name to uninstall: ").strip()
    
    if not package:
        print_status("Package name required.", "error")
        return
    
    # Verificar se o pacote existe
    check, _ = adb_shell(device, f"pm list packages | grep {package}")
    if not check:
        print_status(f"Package {package} not found.", "warning")
        confirm = input("Continue anyway? (y/n): ").strip().lower()
        if confirm != "y":
            return
    
    print_status(f"Uninstalling {package}...", "info")
    out, err = run_cmd(f"adb -s {device} uninstall {package}", capture=True)
    
    if "Success" in out:
        print_status("Package uninstalled successfully!", "success")
    else:
        print_status(f"Uninstall failed: {out or err}", "error")

def option_pull_file():
    """Puxa arquivo do dispositivo"""
    device = get_selected_device()
    if device is None:
        return
    
    remote_path = input("Remote file path (e.g., /sdcard/file.txt): ").strip()
    
    if not remote_path:
        print_status("Remote path required.", "error")
        return
    
    # Verificar se arquivo existe
    check, _ = adb_shell(device, f"ls {remote_path}")
    if "No such file" in check or not check:
        print_status("File not found on device.", "error")
        return
    
    local_path = input("Local destination path (default: ./basename): ").strip()
    if not local_path:
        local_path = "./" + os.path.basename(remote_path)
    
    print_status(f"Pulling {remote_path}...", "info")
    out, err = adb_pull(device, remote_path, local_path)
    
    if err and "error" in err.lower():
        print_status(f"Pull failed: {err}", "error")
    else:
        print_status(f"File pulled to {local_path}", "success")
        
        # Opção de abrir o arquivo
        if os.path.exists(local_path):
            view = input("Open file? (y/n): ").strip().lower()
            if view == "y":
                opener = shutil.which("xdg-open") or "open" if sys.platform == "darwin" else "start"
                run_cmd(f"{opener} {local_path}")

def option_push_file():
    """Envia arquivo para o dispositivo"""
    device = get_selected_device()
    if device is None:
        return
    
    local_path = input("Local file path: ").strip()
    
    if not os.path.isfile(local_path):
        print_status("Local file not found.", "error")
        return
    
    remote_path = input("Remote destination (e.g., /sdcard/): ").strip()
    if not remote_path:
        remote_path = "/sdcard/" + os.path.basename(local_path)
    
    print_status(f"Pushing {local_path} to {remote_path}...", "info")
    out, err = adb_push(device, local_path, remote_path)
    
    if err and "error" in err.lower():
        print_status(f"Push failed: {err}", "error")
    else:
        print_status("File pushed successfully!", "success")

def option_send_sms():
    """Envia SMS via intent"""
    device = get_selected_device()
    if device is None:
        return
    
    phone = input("Phone number (with country code): ").strip()
    message = input("Message: ").strip()
    
    if not phone or not message:
        print_status("Phone number and message required.", "error")
        return
    
    # Escapar caracteres especiais
    message = message.replace('"', '\\"').replace("'", "\\'")
    
    print_status(f"Sending SMS to {phone}...", "info")
    
    # Método 1: Intent padrão
    cmd = f'adb -s {device} shell am start -a android.intent.action.SENDTO -d sms:{phone} --es sms_body "{message}" --ez exit_on_sent true'
    out, err = run_cmd(cmd, capture=True)
    
    if err:
        # Método 2: fallback com broadcast
        alt_cmd = f'adb -s {device} shell service call isms 7 i32 0 s16 "com.android.mms" s16 "null" s16 "{phone}" s16 "null" s16 "{message}" s16 "null" s16 "null"'
        run_cmd(alt_cmd)
    
    print_status("SMS intent sent. Messaging app should open.", "success")
    print_status("You may need to press send manually on the device.", "warning")

def option_dump_contacts():
    """Exporta contatos do dispositivo"""
    device = get_selected_device()
    if device is None:
        return
    
    print_status("Dumping contacts...", "info")
    
    # Método 1: content query
    out, _ = adb_shell(device, "content query --uri content://com.android.contacts/data/phones/")
    
    if not out or "No result" in out:
        # Método 2: tentar via contacts2.db
        print_status("Trying alternative method...", "info")
        run_cmd(f"adb -s {device} pull /data/data/com.android.providers.contacts/databases/contacts2.db ./temp_contacts.db 2>/dev/null")
        if os.path.exists("temp_contacts.db"):
            import sqlite3
            try:
                conn = sqlite3.connect("temp_contacts.db")
                cursor = conn.cursor()
                cursor.execute("SELECT display_name, data1 FROM view_data WHERE data1 IS NOT NULL AND display_name IS NOT NULL")
                contacts = cursor.fetchall()
                conn.close()
                os.remove("temp_contacts.db")
                
                if contacts:
                    with open("contacts.txt", "w") as f:
                        for name, number in contacts:
                            f.write(f"{name}: {number}\n")
                    print_status(f"Saved {len(contacts)} contacts to contacts.txt", "success")
                    return
            except:
                pass
    
    # Parse do resultado do content query
    contacts = []
    for line in (out or "").splitlines():
        if "display_name" in line:
            name_match = re.search(r'display_name=([^,]+)', line)
            number_match = re.search(r'data1=([^,]+)', line)
            if name_match and number_match:
                name = name_match.group(1).strip()
                number = number_match.group(1).strip()
                if name and number:
                    contacts.append(f"{name}: {number}")
    
    if contacts:
        print_status(f"Found {len(contacts)} contacts:", "success")
        for contact in contacts[:30]:
            print(f"  {contact}")
        if len(contacts) > 30:
            print(f"  ... and {len(contacts)-30} more")
        
        save = input("\nSave to contacts.txt? (y/n): ").strip().lower()
        if save == "y":
            with open("contacts.txt", "w") as f:
                f.write("\n".join(contacts) + "\n")
            print_status("Saved to contacts.txt", "success")
    else:
        print_status("No contacts found or permission denied.", "warning")
        print_status("Try granting contact permission to this tool via device settings.", "info")

def option_reboot_device():
    """Reinicia o dispositivo"""
    device = get_selected_device()
    if device is None:
        return
    
    print("\nReboot options:")
    print("  1. Normal reboot")
    print("  2. Reboot to bootloader")
    print("  3. Reboot to recovery")
    print("  4. Reboot to fastboot")
    
    choice = input("Select option (1-4): ").strip()
    
    reboot_cmds = {
        "1": "reboot",
        "2": "reboot bootloader",
        "3": "reboot recovery",
        "4": "reboot fastboot"
    }
    
    if choice in reboot_cmds:
        confirm = input(YELLOW + f"Reboot device to {reboot_cmds[choice]}? (yes/no): " + RESET).strip().lower()
        if confirm == "yes":
            print_status(f"Rebooting device...", "warning")
            run_cmd(f"adb -s {device} shell {reboot_cmds[choice]}")
            print_status("Reboot command sent.", "success")
        else:
            print_status("Cancelled.", "info")
    else:
        print_status("Invalid option.", "error")

def option_start_app():
    """Inicia aplicativo no dispositivo"""
    device = get_selected_device()
    if device is None:
        return
    
    package = input("Enter package name to start: ").strip()
    
    if not package:
        print_status("Package name required.", "error")
        return
    
    # Tentar encontrar a Activity principal
    print_status(f"Starting {package}...", "info")
    
    # Método 1: monkey (mais confiável)
    out, err = run_cmd(f"adb -s {device} shell monkey -p {package} 1", capture=True)
    
    if "No activities found" in out or "error" in out.lower():
        # Método 2: tentar com dumpsys
        out2, _ = adb_shell(device, f"dumpsys package {package} | grep -A 1 'android.intent.action.MAIN:' | grep -Eo '([a-zA-Z0-9._]+/.[a-zA-Z0-9._]+)' | head -1")
        if out2:
            activity = out2.strip()
            run_cmd(f"adb -s {device} shell am start -n {activity}")
            print_status(f"Started with activity: {activity}", "success")
        else:
            print_status(f"Could not start {package}", "error")
            print_status("Try: adb shell monkey -p <package> 1", "info")
    else:
        print_status("App started successfully!", "success")

def option_get_device_logs():
    """Obtém logs do dispositivo (logcat)"""
    device = get_selected_device()
    if device is None:
        return
    
    print_status("Device Logs (logcat)", "info")
    print("Filter options:")
    print("  1. All logs")
    print("  2. Errors only")
    print("  3. Warnings and errors")
    print("  4. Specific tag")
    print("  5. Save to file")
    print("  6. Live monitor (Ctrl+C to stop)")
    
    choice = input("Select option (1-6): ").strip()
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"logcat_{timestamp}.txt"
    
    if choice == "1":
        out, _ = run_cmd(f"adb -s {device} logcat -d", capture=True, timeout=10)
        print(out if out else "No logs")
        if out and len(out) > 1000:
            save = input("Save full log to file? (y/n): ").strip().lower()
            if save == "y":
                with open(filename, "w") as f:
                    f.write(out)
                print_status(f"Saved to {filename}", "success")
    elif choice == "2":
        run_cmd(f"adb -s {device} logcat -d *:E")
    elif choice == "3":
        run_cmd(f"adb -s {device} logcat -d *:W")
    elif choice == "4":
        tag = input("Enter log tag (e.g., ActivityManager): ").strip()
        run_cmd(f"adb -s {device} logcat -d -s {tag}")
    elif choice == "5":
        print_status(f"Saving logs to {filename}...", "info")
        run_cmd(f"adb -s {device} logcat -d > {filename}")
        if os.path.exists(filename):
            print_status(f"Logs saved to {filename}", "success")
            size = os.path.getsize(filename)
            print(f"  File size: {size/1024:.2f} KB")
    elif choice == "6":
        print_status("Live logcat monitor (Ctrl+C to stop)...", "info")
        try:
            subprocess.call(f"adb -s {device} logcat", shell=True)
        except KeyboardInterrupt:
            print_status("\nLog monitor stopped.", "info")

def option_toggle_wifi():
    """Liga/desliga WiFi"""
    device = get_selected_device()
    if device is None:
        return
    
    # Verificar estado atual do WiFi
    status_out, _ = adb_shell(device, "dumpsys wifi | grep 'Wi-Fi is'")
    if "enabled" in status_out.lower():
        current = "enabled"
    else:
        current = "disabled"
    
    print_status(f"Current Wi-Fi state: {current}", "info")
    
    action = input("Enable or disable Wi-Fi? (enable/disable): ").strip().lower()
    
    if action not in ["enable", "disable"]:
        print_status("Invalid action.", "error")
        return
    
    cmd = f"adb -s {device} shell svc wifi {action}"
    run_cmd(cmd)
    print_status(f"Wi-Fi {action}d via svc command.", "success")
    
    # Método alternativo via settings
    alt_cmd = f"adb -s {device} shell settings put global wifi_on {'1' if action == 'enable' else '0'}"
    run_cmd(alt_cmd)
    
    # Verificar novo estado
    time.sleep(1)
    status_out, _ = adb_shell(device, "dumpsys wifi | grep 'Wi-Fi is'")
    print_status(f"Wi-Fi is now: {status_out if status_out else 'unknown'}", "info")

def option_check_storage():
    """Verifica armazenamento do dispositivo"""
    device = get_selected_device()
    if device is None:
        return
    
    print_status("Storage Information", "info")
    print(CYAN + "="*50 + RESET)
    
    # Memória (RAM)
    mem_out, _ = adb_shell(device, "cat /proc/meminfo")
    if mem_out:
        print(f"\n{YELLOW}[ RAM ]{RESET}")
        for line in mem_out.splitlines()[:4]:
            print(f"  {line}")
    
    # Armazenamento interno
    storage_out, _ = adb_shell(device, "df -h /data /system /cache")
    if storage_out:
        print(f"\n{YELLOW}[ Storage ]{RESET}")
        for line in storage_out.splitlines():
            if "Filesystem" in line or "/data" in line or "/system" in line:
                print(f"  {line}")
    
    # SD Card se existir
    sdcard_out, _ = adb_shell(device, "df -h /storage/emulated /sdcard 2>/dev/null")
    if sdcard_out and "sdcard" in sdcard_out.lower():
        print(f"\n{YELLOW}[ SD Card ]{RESET}")
        for line in sdcard_out.splitlines():
            if "sdcard" in line.lower():
                print(f"  {line}")
    
    # Diretórios grandes
    print(f"\n{YELLOW}[ Large Directories ]{RESET}")
    large_dirs = ["/sdcard/DCIM", "/sdcard/Download", "/sdcard/Music", "/sdcard/Movies", "/sdcard/Pictures"]
    for dir_path in large_dirs:
        size_out, _ = adb_shell(device, f"du -sh {dir_path} 2>/dev/null")
        if size_out:
            print(f"  {size_out}")
    
    print(CYAN + "="*50 + RESET)
    
    # Opção de salvar
    save = input("\nSave storage info to file? (y/n): ").strip().lower()
    if save == "y":
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"storage_info_{timestamp}.txt"
        with open(filename, "w") as f:
            f.write(f"=== Device Storage Info ({timestamp}) ===\n\n")
            f.write(f"RAM:\n{mem_out if mem_out else 'N/A'}\n\n")
            f.write(f"Storage:\n{storage_out if storage_out else 'N/A'}\n\n")
            f.write(f"SD Card:\n{sdcard_out if sdcard_out else 'N/A'}\n")
        print_status(f"Saved to {filename}", "success")

def option_take_photo():
    """Tira foto usando a câmera"""
    device = get_selected_device()
    if device is None:
        return
    
    print_status("Taking photo...", "info")
    
    # Abrir câmera
    run_cmd(f"adb -s {device} shell am start -a android.media.action.IMAGE_CAPTURE")
    time.sleep(2)
    
    # Tirar foto (KEYCODE_CAMERA = 27)
    run_cmd(f"adb -s {device} shell input keyevent 27")
    time.sleep(2)
    
    # Encontrar a foto mais recente
    photo_out, _ = adb_shell(device, "ls -t /sdcard/DCIM/Camera/ 2>/dev/null | head -1")
    
    if not photo_out:
        # Tentar outro diretório
        photo_out, _ = adb_shell(device, "ls -t /sdcard/Pictures/ 2>/dev/null | head -1")
    
    if not photo_out:
        print_status("Could not find the photo.", "error")
        return
    
    remote_photo = f"/sdcard/DCIM/Camera/{photo_out}"
    if not os.path.exists("/sdcard/DCIM/Camera"):
        remote_photo = f"/sdcard/Pictures/{photo_out}"
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    local_photo = f"photo_{timestamp}.jpg"
    
    print_status(f"Pulling {photo_out}...", "info")
    adb_pull(device, remote_photo, local_photo)
    
    if os.path.exists(local_photo):
        print_status(f"Photo saved as {local_photo}", "success")
        view = input("Open photo? (y/n): ").strip().lower()
        if view == "y":
            opener = shutil.which("xdg-open") or "open" if sys.platform == "darwin" else "start"
            run_cmd(f"{opener} {local_photo}")
    else:
        print_status("Failed to pull photo.", "error")

def option_troubleshoot():
    """Soluciona problemas de conexão ADB"""
    print_status("ADB Troubleshooting", "info")
    print(CYAN + "="*50 + RESET)
    
    # 1. Matar e reiniciar servidor
    print_status("Restarting ADB server...", "info")
    run_cmd("adb kill-server")
    time.sleep(1)
    run_cmd("adb start-server")
    time.sleep(2)
    
    # 2. Verificar dispositivos
    print_status("Current devices:", "info")
    run_cmd("adb devices")
    
    # 3. Verificar dependências
    print("\n" + YELLOW + "Dependencies:" + RESET)
    deps = [("adb", adb_available()), ("scrcpy", scrcpy_available()), ("nmap", nmap_available())]
    for name, avail in deps:
        status = GREEN + "✓ installed" + RESET if avail else RED + "✗ missing" + RESET
        print(f"  {name}: {status}")
    
    # 4. Verificar sistema operacional
    print(f"\n{YELLOW}System Info:{RESET}")
    print(f"  OS: {platform.system()} {platform.release()}")
    print(f"  Python: {platform.python_version()}")
    
    # 5. Verificar regras USB (Linux)
    if platform.system() == "Linux":
        print("\n" + YELLOW + "USB Permission Check:" + RESET)
        print("  If device shows as 'unauthorized' or 'offline':")
        print("  - Check USB debugging is enabled on device")
        print("  - Check for popup on device to authorize computer")
        print("  - Try: sudo adb kill-server && sudo adb start-server")
        
        # Verificar regras udev
        rules_file = "/etc/udev/rules.d/51-android.rules"
        if os.path.exists(rules_file):
            print(f"  - udev rules found: {rules_file}")
        else:
            print("  - No udev rules found. You may need to run as root.")
    
    print(CYAN + "="*50 + RESET)
    print_status("Troubleshooting complete.", "success")

# ==================== FUNÇÕES DE SEGURANÇA/PENTEST ====================

def pentest_root_detection():
    """Detecta se dispositivo tem root"""
    device = get_selected_device()
    if device is None:
        return
    
    print_status("Root Detection", "info")
    print(CYAN + "="*50 + RESET)
    
    root_indicators = []
    
    # Checks comuns
    checks = [
        ("su binary", "which su"),
        ("test-keys build", "getprop ro.build.tags | grep test-keys"),
        ("superuser app", "pm list packages | grep -E 'superuser|supersu|magisk'"),
        ("debuggable build", "getprop ro.debuggable"),
        ("insecure boot", "getprop ro.secure"),
    ]
    
    for name, cmd in checks:
        out, _ = adb_shell(device, cmd)
        if out and "not found" not in out.lower() and out.strip():
            root_indicators.append(name)
            print(f"  {RED}[!] {name} found{RESET}")
        else:
            print(f"  {GREEN}[✓] {name} not found{RESET}")
    
    # Magisk específico
    magisk_out, _ = adb_shell(device, "magisk -c 2>/dev/null")
    if magisk_out:
        root_indicators.append("Magisk")
        print(f"  {RED}[!] Magisk detected: {magisk_out}{RESET}")
    
    print(CYAN + "="*50 + RESET)
    
    if root_indicators:
        print_status(f"DEVICE APPEARS TO BE ROOTED! ({', '.join(root_indicators)})", "error")
        print_status("Security risk for banking apps and sensitive data.", "warning")
    else:
        print_status("No root indicators found.", "success")
    
    # Salvar resultado
    save = input("\nSave root detection report? (y/n): ").strip().lower()
    if save == "y":
        with open("root_detection.txt", "w") as f:
            f.write(f"Root Detection Report - {datetime.datetime.now()}\n")
            f.write("="*50 + "\n")
            f.write(f"Rooted: {bool(root_indicators)}\n")
            f.write(f"Indicators: {', '.join(root_indicators) if root_indicators else 'None'}\n")
        print_status("Saved to root_detection.txt", "success")

def pentest_apk_permissions():
    """Lista permissões perigosas dos apps"""
    device = get_selected_device()
    if device is None:
        return
    
    print_status("Dangerous Permissions Analysis", "info")
    print(CYAN + "="*60 + RESET)
    
    # Lista de permissões perigosas
    dangerous = [
        "CAMERA", "RECORD_AUDIO", "ACCESS_FINE_LOCATION", "ACCESS_COARSE_LOCATION",
        "READ_SMS", "SEND_SMS", "RECEIVE_SMS", "READ_CONTACTS", "WRITE_CONTACTS",
        "READ_CALL_LOG", "WRITE_CALL_LOG", "CALL_PHONE", "READ_EXTERNAL_STORAGE",
        "WRITE_EXTERNAL_STORAGE", "GET_ACCOUNTS", "READ_PHONE_STATE", "PROCESS_OUTGOING_CALLS",
        "ANSWER_PHONE_CALLS", "BODY_SENSORS", "ACTIVITY_RECOGNITION", "USE_BIOMETRIC"
    ]
    
    # Obter lista de pacotes
    pkg_out, _ = adb_shell(device, "pm list packages -3")
    if not pkg_out:
        print_status("No user apps found or permission denied.", "warning")
        return
    
    packages = [l.replace("package:", "").strip() for l in pkg_out.splitlines() if l.strip()]
    print_status(f"Analyzing {len(packages)} user apps...", "info")
    
    results = []
    
    for pkg in packages:
        dump_out, _ = adb_shell(device, f"dumpsys package {pkg}")
        if not dump_out:
            continue
        
        granted = []
        for perm in dangerous:
            if f"android.permission.{perm}" in dump_out and "granted=true" in dump_out:
                granted.append(perm)
        
        if granted:
            results.append((pkg, granted))
            print(f"\n{YELLOW}{pkg}{RESET}")
            for perm in granted:
                print(f"  {RED}• {perm}{RESET}")
    
    print(CYAN + "="*60 + RESET)
    print_status(f"Found {len(results)} apps with dangerous permissions", "info" if results else "success")
    
    # Salvar relatório
    if results:
        save = input("\nSave permissions report? (y/n): ").strip().lower()
        if save == "y":
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"permissions_report_{timestamp}.txt"
            with open(filename, "w") as f:
                f.write(f"Dangerous Permissions Report - {datetime.datetime.now()}\n")
                f.write("="*60 + "\n\n")
                for pkg, perms in results:
                    f.write(f"{pkg}\n")
                    for perm in perms:
                        f.write(f"  - {perm}\n")
                    f.write("\n")
            print_status(f"Saved to {filename}", "success")

def pentest_security_audit():
    """Auditoria de segurança completa"""
    device = get_selected_device()
    if device is None:
        return
    
    print_status("Running Comprehensive Security Audit", "info")
    print(CYAN + "="*60 + RESET)
    
    audit_results = {}
    
    # Coletar informações de segurança
    security_props = [
        ("ro.build.version.security_patch", "Security Patch Level"),
        ("ro.build.version.release", "Android Version"),
        ("ro.build.tags", "Build Tags"),
        ("ro.secure", "Secure Boot"),
        ("ro.debuggable", "Debuggable"),
        ("ro.adb.secure", "ADB Secure"),
    ]
    
    for prop, name in security_props:
        out, _ = adb_shell(device, f"getprop {prop}")
        audit_results[name] = out or "Unknown"
    
    # Verificar patch level
    patch_level = audit_results.get("Security Patch Level", "")
    if patch_level and patch_level != "Unknown":
        try:
            patch_date = datetime.datetime.strptime(patch_level, "%Y-%m-%d")
            if patch_date < datetime.datetime(2025, 1, 1):
                audit_results["Patch Status"] = "OUTDATED - Vulnerable to known CVEs"
            else:
                audit_results["Patch Status"] = "Recent"
        except:
            audit_results["Patch Status"] = "Unable to parse"
    else:
        audit_results["Patch Status"] = "Unknown"
    
    # Verificar root
    root_check, _ = adb_shell(device, "which su")
    audit_results["Root Access"] = "DETECTED" if root_check else "Not detected"
    
    # Verificar apps debuggable
    debuggable_count = 0
    pkg_out, _ = adb_shell(device, "pm list packages")
    if pkg_out:
        packages = [l.replace("package:", "").strip() for l in pkg_out.splitlines()]
        for pkg in packages[:100]:  # Limit para performance
            dump_out, _ = adb_shell(device, f"dumpsys package {pkg} | grep debuggable")
            if "debuggable=true" in (dump_out or ""):
                debuggable_count += 1
    audit_results["Debuggable Apps"] = debuggable_count
    
    # Verificar backup permitido
    audit_results["Backup Enabled"] = "Check via: adb backup -f backup.ab -apk --all"
    
    # Exibir resultados
    print(f"\n{BOLD}SECURITY AUDIT RESULTS:{RESET}\n")
    
    for key, value in audit_results.items():
        if "OUTDATED" in str(value) or "DETECTED" in str(value):
            color = RED
        elif "Not" in str(value) or "Unknown" in str(value):
            color = YELLOW
        else:
            color = GREEN
        print(f"  {color}{key}: {value}{RESET}")
    
    print(CYAN + "="*60 + RESET)
    
    # Recomendações
    print(f"\n{BOLD}RECOMMENDATIONS:{RESET}")
    if "OUTDATED" in audit_results.get("Patch Status", ""):
        print(f"  {RED}• Install latest security updates{RESET}")
    if audit_results.get("Root Access") == "DETECTED":
        print(f"  {RED}• Root detected - security risk for sensitive apps{RESET}")
    if audit_results.get("Debuggable Apps", 0) > 0:
        print(f"  {RED}• {audit_results['Debuggable Apps']} debuggable apps found - risk of data extraction{RESET}")
    
    # Salvar relatório
    save = input("\nSave full audit report? (y/n): ").strip().lower()
    if save == "y":
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"security_audit_{timestamp}.json"
        with open(filename, "w") as f:
            json.dump(audit_results, f, indent=4)
        print_status(f"Saved to {filename}", "success")

def pentest_debuggable_apps():
    """Lista apps debuggable"""
    device = get_selected_device()
    if device is None:
        return
    
    print_status("Scanning for debuggable applications...", "info")
    print(CYAN + "="*60 + RESET)
    
    pkg_out, _ = adb_shell(device, "pm list packages")
    if not pkg_out:
        print_status("No packages found.", "error")
        return
    
    packages = [l.replace("package:", "").strip() for l in pkg_out.splitlines()]
    debuggable = []
    
    for pkg in packages:
        dump_out, _ = adb_shell(device, f"dumpsys package {pkg} | grep -i debuggable")
        if dump_out and "debuggable=true" in dump_out.lower():
            debuggable.append(pkg)
            print(f"  {RED}[!] {pkg}{RESET}")
    
    print(CYAN + "="*60 + RESET)
    
    if debuggable:
        print_status(f"Found {len(debuggable)} debuggable applications!", "warning")
        print_status("Debuggable apps can be exploited for data extraction", "warning")
        
        # Salvar lista
        with open("debuggable_apps.txt", "w") as f:
            f.write("\n".join(debuggable))
        print_status("Saved to debuggable_apps.txt", "success")
    else:
        print_status("No debuggable apps found.", "success")

def pentest_device_shell():
    """Abre shell interativo no dispositivo"""
    device = get_selected_device()
    if device is None:
        return
    
    print_status("Opening interactive ADB shell...", "info")
    print_status(f"Device: {device}", "info")
    print(YELLOW + "Type 'exit' to close shell" + RESET)
    print(CYAN + "="*50 + RESET)
    
    subprocess.call(f"adb -s {device} shell", shell=True)
    
    print(CYAN + "="*50 + RESET)
    print_status("Shell closed.", "info")

def pentest_network_scan():
    """Escaneia rede local em busca de dispositivos"""
    device = get_selected_device()
    if device is None:
        return
    
    print_status("Network Security Scan", "info")
    print(CYAN + "="*60 + RESET)
    
    # Obter IP do dispositivo
    ip_out, _ = adb_shell(device, "ip addr show wlan0 | grep 'inet ' | awk '{print $2}' | cut -d/ -f1")
    
    if not ip_out:
        ip_out, _ = adb_shell(device, "ifconfig wlan0 | grep 'inet addr' | cut -d: -f2 | cut -d' ' -f1")
    
    if not ip_out:
        print_status("Could not get device IP address.", "error")
        return
    
    device_ip = ip_out.strip()
    print_status(f"Device IP: {device_ip}", "info")
    
    # Calcular rede
    parts = device_ip.split('.')
    network = f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"
    print_status(f"Scanning network: {network}", "info")
    
    if nmap_available():
        print_status("Running nmap scan on local network...", "info")
        run_cmd(f"nmap -sn {network}")
        
        # Escaneamento de portas
        scan_ports = input("\nScan for open ports on device? (y/n): ").strip().lower()
        if scan_ports == "y":
            print_status(f"Port scanning {device_ip}...", "info")
            run_cmd(f"nmap -p- --min-rate 1000 {device_ip}")
    else:
        # Fallback com ping
        print_status("nmap not found. Using ping sweep...", "warning")
        for i in range(1, 255):
            target = f"{parts[0]}.{parts[1]}.{parts[2]}.{i}"
            response = os.system(f"ping -c 1 -W 1 {target} > /dev/null 2>&1")
            if response == 0:
                print(f"  {GREEN}{target} is up{RESET}")
    
    print(CYAN + "="*60 + RESET)

def pentest_dump_sms():
    """Extrai mensagens SMS"""
    device = get_selected_device()
    if device is None:
        return
    
    print_status("Dumping SMS messages...", "info")
    print(CYAN + "="*60 + RESET)
    
    # Tentar via content provider
    sms_out, _ = adb_shell(device, "content query --uri content://sms/inbox")
    
    if not sms_out:
        print_status("No SMS access. Try alternative method...", "warning")
        # Tentar via backup
        print_status("Attempting backup method...", "info")
        run_cmd(f"adb -s {device} backup -f sms_backup.ab com.android.providers.telephony")
        print_status("Backup created as sms_backup.ab (may need conversion)", "info")
        return
    
    # Parse SMS
    messages = []
    for line in sms_out.splitlines():
        if "address=" in line and "body=" in line:
            addr_match = re.search(r'address=([^,]+)', line)
            body_match = re.search(r'body=([^,]+?)(?=,|$)', line)
            date_match = re.search(r'date=([0-9]+)', line)
            
            if addr_match and body_match:
                addr = addr_match.group(1).strip()
                body = body_match.group(1).strip()
                messages.append(f"From: {addr}\nMessage: {body}\n{'-'*40}")
    
    if messages:
        print(f"\nFound {len(messages)} SMS messages:\n")
        for msg in messages[:20]:
            print(msg)
        if len(messages) > 20:
            print(f"... and {len(messages)-20} more")
        
        save = input("\nSave all SMS to file? (y/n): ").strip().lower()
        if save == "y":
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sms_dump_{timestamp}.txt"
            with open(filename, "w") as f:
                f.write(f"SMS Dump - {datetime.datetime.now()}\n")
                f.write("="*60 + "\n\n")
                f.write("\n".join(messages))
            print_status(f"Saved to {filename}", "success")
    else:
        print_status("No SMS messages found or permission denied.", "warning")
    
    print(CYAN + "="*60 + RESET)

def pentest_dump_call_logs():
    """Extrai logs de chamadas"""
    device = get_selected_device()
    if device is None:
        return
    
    print_status("Dumping call logs...", "info")
    print(CYAN + "="*60 + RESET)
    
    calls_out, _ = adb_shell(device, "content query --uri content://call_log/calls")
    
    if not calls_out:
        print_status("No call log access or permission denied.", "error")
        return
    
    calls = []
    for line in calls_out.splitlines():
        if "number=" in line:
            num_match = re.search(r'number=([^,]+)', line)
            dur_match = re.search(r'duration=([0-9]+)', line)
            type_match = re.search(r'type=([0-9])', line)
            
            if num_match:
                number = num_match.group(1).strip()
                call_type = {"1": "INCOMING", "2": "OUTGOING", "3": "MISSED"}.get(type_match.group(1) if type_match else "", "UNKNOWN")
                duration = dur_match.group(1) if dur_match else "0"
                calls.append(f"{call_type}: {number} (Duration: {duration}s)")
    
    if calls:
        print(f"\nFound {len(calls)} call logs:\n")
        for call in calls[:30]:
            print(f"  {call}")
        if len(calls) > 30:
            print(f"  ... and {len(calls)-30} more")
        
        save = input("\nSave call logs to file? (y/n): ").strip().lower()
        if save == "y":
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"call_logs_{timestamp}.txt"
            with open(filename, "w") as f:
                f.write(f"Call Logs Dump - {datetime.datetime.now()}\n")
                f.write("="*60 + "\n\n")
                f.write("\n".join(calls))
            print_status(f"Saved to {filename}", "success")
    else:
        print_status("No call logs found.", "warning")
    
    print(CYAN + "="*60 + RESET)

def pentest_installed_packages_analysis():
    """Análise detalhada de pacotes instalados"""
    device = get_selected_device()
    if device is None:
        return
    
    print_status("Package Analysis", "info")
    print(CYAN + "="*60 + RESET)
    
    # Obter lista de pacotes
    pkg_out, _ = adb_shell(device, "pm list packages -3")
    if not pkg_out:
        print_status("No user packages found.", "warning")
        return
    
    packages = [l.replace("package:", "").strip() for l in pkg_out.splitlines()]
    print_status(f"Analyzing {len(packages)} user packages...", "info")
    
    analysis = []
    
    for pkg in packages[:50]:  # Limit para performance
        dump_out, _ = adb_shell(device, f"dumpsys package {pkg}")
        if not dump_out:
            continue
        
        info = {"name": pkg}
        
        # Extrair informações
        ver_match = re.search(r'versionName=([^\s]+)', dump_out)
        if ver_match:
            info["version"] = ver_match.group(1)
        
        first_install = re.search(r'firstInstallTime=([0-9]+)', dump_out)
        if first_install:
            try:
                dt = datetime.datetime.fromtimestamp(int(first_install.group(1))/1000)
                info["installed"] = dt.strftime("%Y-%m-%d")
            except:
                pass
        
        if "debuggable=true" in dump_out:
            info["debuggable"] = True
        
        if "hasCode=true" in dump_out:
            info["has_code"] = True
        
        # Contar permissões
        perm_count = len(re.findall(r'android\.permission\.\w+', dump_out))
        info["permissions"] = perm_count
        
        analysis.append(info)
        
        # Exibir
        status = RED + "[!] DEBUGGABLE" + RESET if info.get("debuggable") else ""
        print(f"  {pkg} v{info.get('version', '?')} - {info.get('permissions', 0)} permissions {status}")
    
    print(CYAN + "="*60 + RESET)
    print_status(f"Analyzed {len(analysis)} packages", "success")
    
    # Salvar
    save = input("\nSave package analysis to JSON? (y/n): ").strip().lower()
    if save == "y":
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"package_analysis_{timestamp}.json"
        with open(filename, "w") as f:
            json.dump(analysis, f, indent=4)
        print_status(f"Saved to {filename}", "success")

def pentest_download_all_media():
    """Baixa todas as mídias do dispositivo"""
    device = get_selected_device()
    if device is None:
        return
    
    print_status("Downloading all media files...", "info")
    print(YELLOW + "This may take a while depending on amount of media." + RESET)
    
    # Criar diretório para mídias
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    media_dir = f"device_media_{timestamp}"
    os.makedirs(media_dir, exist_ok=True)
    
    # Diretórios de mídia comuns
    media_dirs = [
        "/sdcard/DCIM",
        "/sdcard/Pictures",
        "/sdcard/Download",
        "/sdcard/Movies",
        "/sdcard/Music",
        "/sdcard/WhatsApp/Media",
        "/sdcard/Telegram/Telegram Images",
        "/sdcard/Telegram/Telegram Video",
        "/sdcard/Instagram",
        "/sdcard/Screenshots"
    ]
    
    total_files = 0
    for media_dir_path in media_dirs:
        print_status(f"Checking {media_dir_path}...", "info")
        
        # Listar arquivos
        ls_out, _ = adb_shell(device, f"ls -la {media_dir_path} 2>/dev/null | grep -E '\\.(jpg|jpeg|png|gif|mp4|mkv|avi|mov|mp3|wav|flac|m4a)$' | awk '{{print $NF}}'")
        
        if ls_out:
            files = [f.strip() for f in ls_out.splitlines() if f.strip()]
            total_files += len(files)
            print_status(f"Found {len(files)} files in {media_dir_path}", "success")
            
            # Baixar cada arquivo
            for filename in files[:20]:  # Limite para demo
                remote_file = f"{media_dir_path}/{filename}"
                local_file = f"{media_dir}/{media_dir_path.replace('/sdcard/', '').replace('/', '_')}_{filename}"
                print_status(f"Downloading {filename}...", "info")
                adb_pull(device, remote_file, local_file)
    
    print_status(f"Download complete! Media saved to {media_dir}", "success")
    print_status(f"Total files downloaded: {total_files}", "info")

def pentest_enable_adb_wifi_permanent():
    """Habilita ADB WiFi permanentemente (requer root ou reinicialização)"""
    device = get_selected_device()
    if device is None:
        return
    
    print_status("Enabling permanent ADB over WiFi...", "warning")
    print(YELLOW + "This requires device to be rebooted after changes." + RESET)
    
    # Verificar root
    root_check, _ = adb_shell(device, "which su")
    if not root_check:
        print_status("Root not detected. This will only work until reboot.", "warning")
    
    # Adicionar propriedade persistente
    run_cmd(f"adb -s {device} shell setprop persist.adb.tcp.port 5555")
    
    # Para dispositivos root
    if root_check:
        run_cmd(f"adb -s {device} shell su -c 'setprop service.adb.tcp.port 5555'")
        run_cmd(f"adb -s {device} shell su -c 'stop adbd'")
        run_cmd(f"adb -s {device} shell su -c 'start adbd'")
    else:
        run_cmd(f"adb -s {device} shell setprop service.adb.tcp.port 5555")
        run_cmd(f"adb -s {device} reboot")
        print_status("Device will reboot. After reboot, connect via: adb connect <IP>", "info")
    
    print_status("ADB over WiFi enabled!", "success")

# ==================== MENU DE SEGURANÇA PENTEST ====================

def show_pentest_menu():
    print_banner()
    print(RED + "═══════════════════════════════════════════════════════════" + RESET)
    print(RED + "           ADVANCED PENETRATION TESTING MODULE" + RESET)
    print(RED + "═══════════════════════════════════════════════════════════" + RESET)
    print()
    print(CYAN + "  [1]  Root Detection" + RESET)
    print(CYAN + "  [2]  Dangerous Permissions Analysis" + RESET)
    print(CYAN + "  [3]  Comprehensive Security Audit" + RESET)
    print(CYAN + "  [4]  Debuggable Apps Scanner" + RESET)
    print(CYAN + "  [5]  Interactive Device Shell" + RESET)
    print(CYAN + "  [6]  Network Security Scan" + RESET)
    print(CYAN + "  [7]  Dump SMS Messages" + RESET)
    print(CYAN + "  [8]  Dump Call Logs" + RESET)
    print(CYAN + "  [9]  Package Analysis" + RESET)
    print(CYAN + "  [10] Download All Media Files" + RESET)
    print(CYAN + "  [11] Enable Permanent ADB over WiFi" + RESET)
    print()
    print(YELLOW + "  [0]  Back to Main Menu" + RESET)
    print(RED + "═══════════════════════════════════════════════════════════" + RESET)
    print()

def pentest_menu():
    """Menu principal de pentest"""
    while True:
        show_pentest_menu()
        choice = input(GREEN + "Pentest option (0-11): " + RESET).strip()
        
        pentest_options = {
            "1": pentest_root_detection,
            "2": pentest_apk_permissions,
            "3": pentest_security_audit,
            "4": pentest_debuggable_apps,
            "5": pentest_device_shell,
            "6": pentest_network_scan,
            "7": pentest_dump_sms,
            "8": pentest_dump_call_logs,
            "9": pentest_installed_packages_analysis,
            "10": pentest_download_all_media,
            "11": pentest_enable_adb_wifi_permanent,
            "0": lambda: "back"
        }
        
        if choice in pentest_options:
            if choice == "0":
                break
            pentest_options[choice]()
            input("\nPress Enter to continue...")
        else:
            print_status("Invalid option.", "error")
            time.sleep(1)

# ==================== MENU PRINCIPAL ====================

def show_main_menu():
    print()
    print(GREEN + "═══════════════════════════════════════════════════════════" + RESET)
    print(GREEN + "                     MAIN MENU" + RESET)
    print(GREEN + "═══════════════════════════════════════════════════════════" + RESET)
    print()
    print(YELLOW + "  [1]  Check Device Info" + RESET)
    print(YELLOW + "  [2]  Connect Device (WiFi ADB)" + RESET)
    print(YELLOW + "  [3]  Disconnect Device" + RESET)
    print(YELLOW + "  [4]  Screen Recording" + RESET)
    print(YELLOW + "  [5]  Screen Mirror (FULL CONTROL)" + RESET)
    print(YELLOW + "  [6]  Show APK List" + RESET)
    print(YELLOW + "  [7]  Take Screenshot" + RESET)
    print(YELLOW + "  [8]  Power Off Device" + RESET)
    print(YELLOW + "  [9]  Install APK" + RESET)
    print(YELLOW + "  [10] Uninstall APK" + RESET)
    print(YELLOW + "  [11] Pull File from Device" + RESET)
    print(YELLOW + "  [12] Push File to Device" + RESET)
    print(YELLOW + "  [13] Send SMS" + RESET)
    print(YELLOW + "  [14] Dump Contacts" + RESET)
    print(YELLOW + "  [15] Reboot Device" + RESET)
    print(YELLOW + "  [16] Start Application" + RESET)
    print(YELLOW + "  [17] Get Device Logs" + RESET)
    print(YELLOW + "  [18] Toggle Wi-Fi" + RESET)
    print(YELLOW + "  [19] Check Storage" + RESET)
    print(YELLOW + "  [20] Take Photo" + RESET)
    print(YELLOW + "  [21] Troubleshoot Connection" + RESET)
    print(YELLOW + "  [22] View Connection History" + RESET)
    print()
    print(RED + "  [99] ADVANCED PENTEST MODULE" + RESET)
    print()
    print(CYAN + "  [q] Quit" + RESET)
    print(GREEN + "═══════════════════════════════════════════════════════════" + RESET)
    print()

def main():
    print_banner()
    
    # Verificar dependências
    print_status("Checking dependencies...", "info")
    adb_available()
    scrcpy_available()
    nmap_available()
    
    update_device_logs()
    
    while True:
        update_device_logs()
        print_banner()
        show_main_menu()
        
        choice = input(GREEN + "Select option: " + RESET).strip().lower()
        
        if choice == "q":
            update_device_logs()
            now = datetime.datetime.now()
            for dev, start in connected_devices.items():
                duration = now - start
                with open("connection_log.txt", "a") as f:
                    f.write(f"[{now}] {dev} session ended - Duration: {duration}\n")
            print_status("Exiting Pegasus. Stay ethical!", "info")
            break
        
        if choice == "99":
            pentest_menu()
            continue
        
        main_options = {
            "1": option_check_device,
            "2": option_connect_device,
            "3": option_disconnect_device,
            "4": option_screen_recording,
            "5": option_screen_mirror,
            "6": option_show_apk_list,
            "7": option_take_screenshot,
            "8": option_power_off,
            "9": option_install_apk,
            "10": option_delete_apk,
            "11": option_pull_file,
            "12": option_push_file,
            "13": option_send_sms,
            "14": option_dump_contacts,
            "15": option_reboot_device,
            "16": option_start_app,
            "17": option_get_device_logs,
            "18": option_toggle_wifi,
            "19": option_check_storage,
            "20": option_take_photo,
            "21": option_troubleshoot,
            "22": option_view_connection_history
        }
        
        if choice in main_options:
            main_options[choice]()
        else:
            print_status("Invalid option.", "error")
        
        input("\nPress Enter to continue...")

def run():
    try:
        main()
    except KeyboardInterrupt:
        print("\n" + YELLOW + "Interrupted by user." + RESET)
        sys.exit(0)
    except Exception as e:
        print(RED + f"Unexpected error: {e}" + RESET)
        sys.exit(1)

if __name__ == "__main__":
    run()