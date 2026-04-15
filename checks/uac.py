import winreg

def run(wait):
    print("\n[3/10] Checking UAC (User Account Control) settings...")

    key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"

    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
        value, _ = winreg.QueryValueEx(key, "ConsentPromptBehaviorAdmin")
        winreg.CloseKey(key)
    except OSError:
        print("\n  [FAIL] Could not read UAC registry key.")
        wait()
        return {
            "title"   : "3. UAC (User Account Control)",
            "status"  : "FAIL",
            "severity": "High",
            "detail"  : "The UAC registry key could not be read.",
            "fix"     : (
                "UAC status could not be determined. Check manually:\n"
                "  > Start menu > search 'UAC' > 'Change User Account Control settings'\n"
                "  > Slider should be at least one notch above 'Never notify'"
            )
        }

    level = _describe_level(value)
    print(f"\n  UAC level: {level}")

    if value == 0:
        print("\n  [FAIL] UAC is completely disabled.")
        wait()
        return {
            "title"   : "3. UAC (User Account Control)",
            "status"  : "FAIL",
            "severity": "High",
            "detail"  : f"UAC level: {level}",
            "fix"     : (
                "UAC is turned off. Re-enable it:\n"
                "  > Start menu > search 'UAC'\n"
                "  > 'Change User Account Control settings'\n"
                "  > Move the slider to 'Notify me only when apps try to make changes'\n"
                "  > Click OK and restart if prompted\n"
                "  Terminal: Run 'UserAccountControlSettings.exe' to open the dialog"
            )
        }
    else:
        print("\n  [PASS] UAC is enabled.")
        wait()
        return {
            "title"   : "3. UAC (User Account Control)",
            "status"  : "PASS",
            "severity": "High",
            "detail"  : f"UAC level: {level}",
            "fix"     : None
        }


def _describe_level(value):
    descriptions = {
        0: "Disabled — never notify (UAC is off)",
        1: "Notify only when apps make changes (no secure desktop)",
        2: "Always notify (most strict)",
        5: "Notify only when apps try to make changes (recommended default)",
    }
    return descriptions.get(value, f"Unknown level ({value})")
