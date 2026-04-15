import subprocess

def run(wait):
    print("\n[5/10] Checking Guest account status...")

    result = subprocess.run(
        ["net", "user", "Guest"],
        capture_output=True,
        text=True
    )

    output = result.stdout

    active = _parse_active(output)

    if active is None:
        print("\n  [FAIL] Could not determine Guest account status.")
        wait()
        return {
            "title"   : "5. Guest Account",
            "status"  : "FAIL",
            "severity": "Medium",
            "detail"  : "Could not read Guest account status.",
            "fix"     : (
                "Check manually:\n"
                "  > Run (as admin): net user Guest\n"
                "  > Look for 'Account active' — it should say No"
            )
        }

    print(f"\n  Guest account active: {active}")

    if active.lower() == "yes":
        print("\n  [FAIL] Guest account is enabled.")
        print("\n  How to fix:")
        print("  > Run (as admin): net user Guest /active:no")
        print("  > Or: Computer Management > Local Users and Groups")
        print("    > Users > Guest > right-click > Properties")
        print("    > Check 'Account is disabled'")
        wait()
        return {
            "title"   : "5. Guest Account",
            "status"  : "FAIL",
            "severity": "Medium",
            "detail"  : "Guest account is enabled.",
            "fix"     : (
                "Disable the Guest account:\n"
                "  > Run (as admin): net user Guest /active:no\n"
                "  > Or: Computer Management > Local Users and Groups\n"
                "    > Users > Guest > right-click > Properties\n"
                "    > Check 'Account is disabled'"
            )
        }
    else:
        print("\n  [PASS] Guest account is disabled.")
        wait()
        return {
            "title"   : "5. Guest Account",
            "status"  : "PASS",
            "severity": "Medium",
            "detail"  : "Guest account is disabled.",
            "fix"     : None
        }


def _parse_active(output):
    for line in output.splitlines():
        if "account active" in line.lower():
            parts = line.split()
            if parts:
                return parts[-1]
    return None
