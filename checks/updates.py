import subprocess

def run(wait):
    print("\n[10/10] Checking for pending Windows updates...")
    print("  (This may take a few seconds...)")

    result = subprocess.run(
        [
            "powershell", "-NoProfile", "-Command",
            "(New-Object -ComObject Microsoft.Update.Session).CreateUpdateSearcher().Search('IsInstalled=0').Updates.Count"
        ],
        capture_output=True,
        text=True,
        timeout=60
    )

    output = result.stdout.strip()

    try:
        count = int(output)
    except ValueError:
        print("\n  [FAIL] Could not check for Windows updates.")
        print("\n  How to fix:")
        print("  > Settings > Windows Update > Check for updates")
        wait()
        return {
            "title"   : "10. Pending Windows Updates",
            "status"  : "FAIL",
            "severity": "High",
            "detail"  : "Could not query Windows Update service.",
            "fix"     : (
                "Check for updates manually:\n"
                "  > Settings > Windows Update > Check for updates"
            )
        }

    if count == 0:
        print("\n  No pending updates found.")
        print("\n  [PASS] Windows is up to date.")
        wait()
        return {
            "title"   : "10. Pending Windows Updates",
            "status"  : "PASS",
            "severity": "High",
            "detail"  : "No pending updates found.",
            "fix"     : None
        }
    else:
        print(f"\n  {count} pending update(s) found.")
        print("\n  [FAIL] Windows has updates waiting to be installed.")
        print("\n  How to fix:")
        print("  > Settings > Windows Update > Check for updates > Install all")
        print("  > Or run (as admin):")
        print("    usoclient StartScan")
        print("    usoclient StartInstall")
        wait()
        return {
            "title"   : "10. Pending Windows Updates",
            "status"  : "FAIL",
            "severity": "High",
            "detail"  : f"{count} pending update(s) found.",
            "fix"     : (
                "Install pending Windows updates:\n"
                "  > Settings > Windows Update > Check for updates > Install all\n"
                "  > Or run (as admin):\n"
                "    usoclient StartScan\n"
                "    usoclient StartInstall"
            )
        }
