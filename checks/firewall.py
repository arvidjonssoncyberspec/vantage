import subprocess

def run(wait):
    print("\n[1/10] Checking Windows Firewall status...")

    result = subprocess.run(
        ["netsh", "advfirewall", "show", "allprofiles"],
        capture_output=True,
        text=True
    )

    output = result.stdout

    domain_on  = "Domain Profile"  in output and _profile_on(output, "Domain Profile")
    private_on = "Private Profile" in output and _profile_on(output, "Private Profile")
    public_on  = "Public Profile"  in output and _profile_on(output, "Public Profile")

    detail_lines = [
        f"  Domain Profile  : {'ON' if domain_on  else 'OFF'}",
        f"  Private Profile : {'ON' if private_on else 'OFF'}",
        f"  Public Profile  : {'ON' if public_on  else 'OFF'}",
    ]
    detail = "\n".join(detail_lines)

    print(detail)

    if domain_on and private_on and public_on:
        print("\n  [PASS] All firewall profiles are enabled.")
        wait()
        return {
            "title"   : "1. Windows Firewall Status",
            "status"  : "PASS",
            "severity": "High",
            "detail"  : detail,
            "fix"     : None
        }
    else:
        print("\n  [FAIL] One or more firewall profiles are turned off.")
        print("\n  How to fix:")
        print("  > Start menu > 'Windows Defender Firewall'")
        print("  > Turn Windows Defender Firewall on or off")
        print("  > Enable for Domain, Private, and Public > OK")
        print("  > Or run (as admin): netsh advfirewall set allprofiles state on")
        wait()
        return {
            "title"   : "1. Windows Firewall Status",
            "status"  : "FAIL",
            "severity": "High",
            "detail"  : detail,
            "fix"     : (
                "One or more firewall profiles are off. To fix:\n"
                "  > Start menu > 'Windows Defender Firewall'\n"
                "  > Turn Windows Defender Firewall on or off\n"
                "  > Enable for Domain, Private, and Public > OK\n"
                "  > Or run (as admin): netsh advfirewall set allprofiles state on"
            )
        }


def _profile_on(output, profile_name):
    start = output.find(profile_name)
    if start == -1:
        return False
    section = output[start:start + 300]
    for line in section.splitlines():
        if line.strip().startswith("State"):
            return "ON" in line.upper()
    return False
