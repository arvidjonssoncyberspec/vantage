import subprocess
import json

SUSPICIOUS_PATHS = [
    "\\temp\\",
    "\\appdata\\roaming\\",
    "\\downloads\\",
]

def run(wait):
    print("\n[9/10] Checking startup programs...")

    result = subprocess.run(
        [
            "powershell", "-NoProfile", "-Command",
            "Get-CimInstance Win32_StartupCommand | Select-Object Name, Command, Location, User | ConvertTo-Json"
        ],
        capture_output=True,
        text=True
    )

    output = result.stdout.strip()

    if not output:
        print("\n  No startup entries found.")
        print("\n  [PASS] No startup programs detected.")
        wait()
        return {
            "title"   : "9. Startup Programs",
            "status"  : "PASS",
            "severity": "Medium",
            "detail"  : "No startup programs detected.",
            "fix"     : None
        }

    try:
        data = json.loads(output)
        if isinstance(data, dict):
            data = [data]
    except json.JSONDecodeError:
        print("\n  [FAIL] Could not parse startup program list.")
        wait()
        return {
            "title"   : "9. Startup Programs",
            "status"  : "FAIL",
            "severity": "Medium",
            "detail"  : "Could not parse startup program list.",
            "fix"     : (
                "Check startup programs manually:\n"
                "  > Run: Task Manager > Startup tab\n"
                "  > Disable anything you don't recognise"
            )
        }

    flagged = [entry for entry in data if _is_suspicious(entry.get("Command", ""))]
    clean   = [entry for entry in data if not _is_suspicious(entry.get("Command", ""))]

    print("\n  Startup programs found:")
    for entry in clean:
        print(f"    {entry.get('Name', 'Unknown'):<35}  {_short_location(entry.get('Location', ''))}")
    for entry in flagged:
        print(f"    {entry.get('Name', 'Unknown'):<35}  {_short_location(entry.get('Location', ''))}  [SUSPICIOUS]")

    detail_lines = ["Startup programs:"]
    for entry in clean:
        detail_lines.append(f"  {entry.get('Name', 'Unknown')} — {entry.get('Command', '')}")
    for entry in flagged:
        detail_lines.append(f"  {entry.get('Name', 'Unknown')} — {entry.get('Command', '')}  [SUSPICIOUS]")

    if flagged:
        print("\n  [FAIL] Suspicious startup entries detected.")
        print("\n  How to fix:")
        print("  > Open Task Manager > Startup tab")
        print("  > Right-click the suspicious entry > Disable")
        print("  > If you don't recognise it, research the program name before removing it")
        print("\n  Suspicious entries:")
        for entry in flagged:
            print(f"\n  {'─' * 44}")
            print(f"  Name    : {entry.get('Name', 'Unknown')}")
            print(f"  Command : {entry.get('Command', 'Unknown')}")
            print(f"  Location: {entry.get('Location', 'Unknown')}")
        wait()
        return {
            "title"   : "9. Startup Programs",
            "status"  : "FAIL",
            "severity": "Medium",
            "detail"  : "\n".join(detail_lines),
            "fix"     : (
                "Suspicious startup entries were found:\n"
                "  > Open Task Manager > Startup tab\n"
                "  > Right-click the suspicious entry > Disable\n"
                "  > Research the program name before removing if unsure"
            )
        }
    else:
        print("\n  [PASS] No suspicious startup entries found.")
        wait()
        return {
            "title"   : "9. Startup Programs",
            "status"  : "PASS",
            "severity": "Medium",
            "detail"  : "\n".join(detail_lines),
            "fix"     : None
        }


def _short_location(location):
    loc = location.upper()
    if "HKEY_LOCAL_MACHINE" in loc or loc.startswith("HKLM"):
        return "HKLM"
    if "HKEY_CURRENT_USER" in loc or loc.startswith("HKU"):
        return "HKCU"
    return location


def _is_suspicious(command):
    command_lower = command.lower()
    return any(path in command_lower for path in SUSPICIOUS_PATHS)
