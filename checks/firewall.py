import subprocess

def run(wait):
    print("\n[1/10] Checking Windows Firewall status...")

    # Run the netsh command and capture its output as text
    result = subprocess.run(
        ["netsh", "advfirewall", "show", "allprofiles"],
        capture_output=True,
        text=True
    )

    output = result.stdout

    # Check each profile by looking for "State" lines in the output
    domain_on  = "Domain Profile" in output and _profile_on(output, "Domain Profile")
    private_on = "Private Profile" in output and _profile_on(output, "Private Profile")
    public_on  = "Public Profile" in output and _profile_on(output, "Public Profile")

    # Build a readable summary of each profile's state
    detail_lines = [
        f"  Domain Profile  : {'ON' if domain_on  else 'OFF'}",
        f"  Private Profile : {'ON' if private_on else 'OFF'}",
        f"  Public Profile  : {'ON' if public_on  else 'OFF'}",
    ]
    detail = "\n".join(detail_lines)

    # Print findings to the screen
    print(detail)

    all_on = domain_on and private_on and public_on

    if all_on:
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
        wait()
        return {
            "title"   : "1. Windows Firewall Status",
            "status"  : "FAIL",
            "severity": "High",
            "detail"  : detail,
            "fix"     : (
                "Turn on all firewall profiles:\n"
                "  1. Open the Start menu and search for 'Windows Defender Firewall'\n"
                "  2. Click 'Turn Windows Defender Firewall on or off'\n"
                "  3. Enable it for all three profiles: Domain, Private, and Public\n"
                "  4. Click OK\n"
                "\n"
                "Or via command line (run as Administrator):\n"
                "  netsh advfirewall set allprofiles state on"
            )
        }


def _profile_on(output, profile_name):
    # Find the section for this profile and check if its State is ON
    start = output.find(profile_name)
    if start == -1:
        return False
    section = output[start:start + 300]  # only look within this profile's section
    for line in section.splitlines():
        if line.strip().startswith("State"):
            return "ON" in line.upper()
    return False
