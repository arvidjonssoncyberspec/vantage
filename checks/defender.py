import subprocess
import json

def run(wait):
    print("\n[2/10] Checking Windows Defender / Antivirus status...")

    result = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            "Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntiVirusProduct | Select-Object displayName, productState | ConvertTo-Json"
        ],
        capture_output=True,
        text=True
    )

    output = result.stdout.strip()

    if not output:
        print("\n  [FAIL] No antivirus product detected.")
        print("\n  How to fix:")
        print("  > Start menu > search 'Windows Security'")
        print("  > Virus & threat protection > Manage settings")
        print("  > Turn on Real-time protection")
        wait()
        return {
            "title"   : "2. Windows Defender / Antivirus Status",
            "status"  : "FAIL",
            "severity": "High",
            "detail"  : "No antivirus product was found registered with Windows Security Center.",
            "fix"     : (
                "No antivirus was found. Enable Windows Defender:\n"
                "  > Start menu > search 'Windows Security'\n"
                "  > Virus & threat protection > Manage settings\n"
                "  > Turn on Real-time protection"
            )
        }

    data = json.loads(output)
    if isinstance(data, dict):
        data = [data]

    detail_lines = []
    any_active = False

    for item in data:
        active = _is_active(item["productState"])
        if active:
            any_active = True
        status_str = "Active" if active else "Inactive"
        detail_lines.append(f"  {item['displayName']}: {status_str}")

    detail = "\n".join(detail_lines)
    print(f"\n{detail}")

    if any_active:
        print("\n  [PASS] An active antivirus product was found.")
        wait()
        return {
            "title"   : "2. Windows Defender / Antivirus Status",
            "status"  : "PASS",
            "severity": "High",
            "detail"  : detail,
            "fix"     : None
        }
    else:
        print("\n  [FAIL] Antivirus is installed but not active.")
        print("\n  How to fix:")
        print("  > For Windows Defender:")
        print("    Start menu > 'Windows Security' > Virus & threat protection")
        print("    > Manage settings > Turn on Real-time protection")
        print("  > For third-party AV (e.g. AVG, Avast):")
        print("    Open the program and look for 'Enable protection' or 'Turn on'")
        wait()
        return {
            "title"   : "2. Windows Defender / Antivirus Status",
            "status"  : "FAIL",
            "severity": "High",
            "detail"  : detail,
            "fix"     : (
                "Antivirus is installed but turned off. Re-enable it:\n"
                "  > For Windows Defender:\n"
                "    Start menu > 'Windows Security' > Virus & threat protection\n"
                "    > Manage settings > Turn on Real-time protection\n"
                "  > For third-party AV (e.g. AVG, Avast):\n"
                "    Open the program and look for 'Enable protection' or 'Turn on'"
            )
        }


def _is_active(state_code):
    # productState is a 6-digit hex number. Middle two digits = real-time protection:
    #   10 = enabled,  11 = enabled (definitions may be outdated),  00 = disabled
    hex_state = format(state_code, "06x")
    return hex_state[2:4] in ("10", "11")
