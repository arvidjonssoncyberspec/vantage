import subprocess

def run(wait):
    print("\n[6/10] Checking Administrator account status...")

    result = subprocess.run(
        ["net", "user", "Administrator"],
        capture_output=True,
        text=True
    )

    output = result.stdout

    active = _parse_active(output)

    if active is None:
        print("\n  [FAIL] Could not determine Administrator account status.")
        wait()
        return {
            "title"   : "6. Administrator Account",
            "status"  : "FAIL",
            "severity": "High",
            "detail"  : "Could not read Administrator account status.",
            "fix"     : (
                "Check manually:\n"
                "  > Run (as admin): net user Administrator\n"
                "  > Look for 'Account active' — it should say No"
            )
        }

    print(f"\n  Administrator account active: {active}")

    if active.lower() == "yes":
        print("\n  [FAIL] Built-in Administrator account is enabled.")
        print("\n  How to fix:")
        print("  > Run (as admin): net user Administrator /active:no")
        print("  > Or: Computer Management > Local Users and Groups")
        print("    > Users > Administrator > right-click > Properties")
        print("    > Check 'Account is disabled'")
        wait()
        return {
            "title"   : "6. Administrator Account",
            "status"  : "FAIL",
            "severity": "High",
            "detail"  : "Built-in Administrator account is enabled.",
            "fix"     : (
                "Disable the built-in Administrator account:\n"
                "  > Run (as admin): net user Administrator /active:no\n"
                "  > Or: Computer Management > Local Users and Groups\n"
                "    > Users > Administrator > right-click > Properties\n"
                "    > Check 'Account is disabled'"
            )
        }
    else:
        print("\n  [PASS] Built-in Administrator account is disabled.")
        wait()
        return {
            "title"   : "6. Administrator Account",
            "status"  : "PASS",
            "severity": "High",
            "detail"  : "Built-in Administrator account is disabled.",
            "fix"     : None
        }


def _parse_active(output):
    for line in output.splitlines():
        if "account active" in line.lower():
            parts = line.split()
            if parts:
                return parts[-1]
    return None
