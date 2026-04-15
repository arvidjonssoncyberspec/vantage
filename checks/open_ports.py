import subprocess
import json

HIGH_RISK = {
    21:   "FTP — unencrypted file transfer",
    23:   "Telnet — unencrypted remote access",
    69:   "TFTP — trivial file transfer, no authentication",
    512:  "rexec — remote execution (legacy Unix service)",
    513:  "rlogin — remote login (legacy Unix service)",
    514:  "rsh — remote shell (legacy Unix service)",
    5900: "VNC — remote desktop, often unsecured",
}

MEDIUM_RISK = {
    135:  "RPC — remote procedure call, common malware target",
    139:  "NetBIOS — legacy Windows file sharing",
    445:  "SMB — Windows file sharing (exploited by WannaCry)",
    3389: "RDP — Remote Desktop Protocol, common attack target",
}

def run(wait):
    print("\n[7/10] Checking open ports and listening services...")

    result = subprocess.run(
        ["netstat", "-ano"],
        capture_output=True,
        text=True
    )

    listening_ports  = _parse_listening_ports(result.stdout)
    fw_blocked_ports = _get_firewall_blocked_ports()

    high_found   = {p: HIGH_RISK[p]   for p in listening_ports if p in HIGH_RISK}
    medium_found = {p: MEDIUM_RISK[p] for p in listening_ports if p in MEDIUM_RISK}

    if not high_found and not medium_found:
        print("\n  [PASS] No known risky ports are open.")
        wait()
        return {
            "title"   : "7. Open Ports & Listening Services",
            "status"  : "PASS",
            "severity": "High",
            "detail"  : "No known risky ports detected.",
            "fix"     : None
        }

    detail_lines = []

    if high_found:
        print("\n  High risk ports detected:")
        detail_lines.append("High risk ports detected:")
        for port, desc in high_found.items():
            line = f"    Port {port} — {desc}"
            print(line)
            detail_lines.append(line)

    if medium_found:
        print("\n  Notable ports detected:")
        detail_lines.append("\nNotable ports detected:")
        for port, desc in medium_found.items():
            blocked = port in fw_blocked_ports
            status  = "[firewall block active]" if blocked else "[not blocked]"
            line    = f"    Port {port} — {desc.split(' — ')[0]:<10}  {status}"
            print(line)
            detail_lines.append(line)

    unblocked_medium = {p: d for p, d in medium_found.items() if p not in fw_blocked_ports}

    if high_found:
        print("\n  [FAIL] High risk ports are listening.")
        print("\n  How to fix:")
        print("  > Identify which program is using the port:")
        print("    Run (as admin): netstat -ano | findstr :<port>")
        print("    Then: tasklist | findstr <PID>")
        print("  > Disable or uninstall the associated service if not needed")
        print("  > Or block the port in Windows Firewall:")
        print("    Windows Defender Firewall > Advanced Settings")
        print("    > Inbound Rules > New Rule > Port > Block the connection")
        wait()
        return {
            "title"   : "7. Open Ports & Listening Services",
            "status"  : "FAIL",
            "severity": "High",
            "detail"  : "\n".join(detail_lines),
            "fix"     : (
                "Identify what is using the flagged port:\n"
                "  > Run (as admin): netstat -ano | findstr :<port>\n"
                "  > Then: tasklist | findstr <PID>\n"
                "  > Disable or uninstall the service if not needed\n"
                "  > Or block it in Windows Firewall:\n"
                "    Windows Defender Firewall > Advanced Settings\n"
                "    > Inbound Rules > New Rule > Port > Block the connection"
            )
        }
    else:
        print("\n  [PASS] No high risk ports found.")
        if unblocked_medium:
            print("\n  How to block each unprotected port:")
            for port, desc in unblocked_medium.items():
                print(f"\n  {'─' * 44}")
                print(f"  Port {port} — {desc.split(' — ')[0]}")
                _print_medium_fix(port)
        wait()
        return {
            "title"   : "7. Open Ports & Listening Services",
            "status"  : "PASS",
            "severity": "High",
            "detail"  : "\n".join(detail_lines),
            "fix"     : None
        }


def _get_firewall_blocked_ports():
    result = subprocess.run(
        [
            "powershell", "-NoProfile", "-Command",
            "Get-NetFirewallRule -Direction Inbound -Action Block -Enabled True "
            "| Get-NetFirewallPortFilter "
            "| Where-Object {$_.LocalPort -ne 'Any'} "
            "| Select-Object LocalPort "
            "| ConvertTo-Json"
        ],
        capture_output=True,
        text=True
    )

    output = result.stdout.strip()
    if not output:
        return set()

    try:
        data = json.loads(output)
        if isinstance(data, dict):
            data = [data]
        ports = set()
        for item in data:
            try:
                ports.add(int(item["LocalPort"]))
            except (ValueError, KeyError):
                continue
        return ports
    except json.JSONDecodeError:
        return set()


def _print_medium_fix(port):
    fixes = {
        135: [
            "  Note: Port 135 is used internally by Windows. Blocking it",
            "  can cause unexpected issues. Only block if you are on an",
            "  isolated or test machine.",
            "  > Run (as admin):",
            "    netsh advfirewall firewall add rule name=\"Block RPC 135\" protocol=TCP dir=in localport=135 action=block",
            "  > Or: Windows Defender Firewall > Advanced Settings",
            "    > Inbound Rules > New Rule > Port > TCP > 135 > Block",
        ],
        139: [
            "  Note: Port 139 is used for file and printer sharing on your",
            "  local network. Safe to block if you don't share files or",
            "  printers with other devices on your home network.",
            "  > Run (as admin):",
            "    netsh advfirewall firewall add rule name=\"Block NetBIOS 139\" protocol=TCP dir=in localport=139 action=block",
            "  > Or: Control Panel > Network and Sharing Center",
            "    > Change adapter settings > right-click adapter > Properties",
            "    > Uncheck 'File and Printer Sharing for Microsoft Networks'",
        ],
        445: [
            "  Note: Port 445 is used for Windows file sharing. Blocking it",
            "  means you won't be able to access shared folders or network",
            "  drives. Safe to block if this is a standalone personal PC.",
            "  > Run (as admin):",
            "    netsh advfirewall firewall add rule name=\"Block SMB 445\" protocol=TCP dir=in localport=445 action=block",
            "  > Or: Windows Defender Firewall > Advanced Settings",
            "    > Inbound Rules > New Rule > Port > TCP > 445 > Block",
        ],
        3389: [
            "  Note: Port 3389 is Remote Desktop. Safe to disable if you",
            "  never connect to this PC remotely. Has no effect on normal",
            "  day-to-day use.",
            "  > Settings > System > Remote Desktop > toggle Off",
            "  > Or run (as admin):",
            '    reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server" /v fDenyTSConnections /t REG_DWORD /d 1 /f',
        ],
    }
    for line in fixes.get(port, ["  > Block it in Windows Defender Firewall > Advanced Settings > Inbound Rules"]):
        print(line)


def _parse_listening_ports(output):
    ports = set()
    for line in output.splitlines():
        if "LISTENING" not in line.upper():
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        try:
            port = int(parts[1].rsplit(":", 1)[-1])
            ports.add(port)
        except ValueError:
            continue
    return ports
