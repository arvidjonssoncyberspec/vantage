import subprocess
import json

def run(wait):
    print("\n[2/10] Checking Windows Defender / Antivirus status...")

    # Query the Security Center for any registered antivirus products
    # ConvertTo-Json gives us clean output that Python can parse reliably
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
        # No antivirus product found at all
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
                "  1. Start menu > search 'Windows Security'\n"
                "  2. Virus & threat protection > Manage settings\n"
                "  3. Turn on Real-time protection"
            )
        }

    # Parse the JSON output into a list of products
    # If only one product is installed, PowerShell returns an object, not an array
    data = json.loads(output)
    if isinstance(data, dict):
        data = [data]

    products = [(item["displayName"], item["productState"]) for item in data]

    detail_lines = []
    any_active = False

    for name, state_code in products:
        active = _is_active(state_code)
        if active:
            any_active = True
        status_str = "Active" if active else "Inactive"
        detail_lines.append(f"  {name}: {status_str}")

    detail = "\n".join(detail_lines)
    print(detail)

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
                "  - For Windows Defender:\n"
                "      Start menu > 'Windows Security' > Virus & threat protection\n"
                "      > Manage settings > Turn on Real-time protection\n"
                "  - For third-party AV (e.g. AVG, Avast):\n"
                "      Open the program and look for a 'Enable protection' or 'Turn on' button"
            )
        }


def _is_active(state_code):
    # productState is a 6-digit hex number. The middle two digits represent
    # the real-time protection state:
    #   10 = enabled, definitions up to date
    #   11 = enabled, definitions may be outdated
    #   00 = disabled
    hex_state = format(state_code, "06x")
    rt_state = hex_state[2:4]  # middle two hex digits
    return rt_state in ("10", "11")
