import subprocess

def run(wait):
    print("\n[4/10] Checking password policy...")

    result = subprocess.run(
        ["net", "accounts"],
        capture_output=True,
        text=True
    )

    output = result.stdout

    min_length = _parse_value(output, "Minimum password length")
    max_age    = _parse_value(output, "Maximum password age (days)")

    print(f"\n  Minimum password length : {min_length}")
    print(f"  Maximum password age    : {max_age}")

    failures = []

    # Check 1: password length
    try:
        if int(min_length) < 8:
            failures.append("Minimum password length is below 8 characters.")
    except ValueError:
        failures.append(f"Could not read minimum password length (got: {min_length}).")

    # Check 2: password expiry
    if max_age.lower() == "unlimited":
        failures.append("Passwords are set to never expire.")

    detail = (
        f"Minimum password length : {min_length}\n"
        f"Maximum password age    : {max_age}"
    )

    if failures:
        for msg in failures:
            print(f"\n  [!] {msg}")
        print("\n  [FAIL] Password policy has weak settings.")
        print("\n  How to fix:")
        print(_build_fix(failures))
        wait()
        return {
            "title"   : "4. Password Policy",
            "status"  : "FAIL",
            "severity": "Medium",
            "detail"  : detail,
            "fix"     : _build_fix(failures)
        }
    else:
        print("\n  [PASS] Password policy meets basic requirements.")
        wait()
        return {
            "title"   : "4. Password Policy",
            "status"  : "PASS",
            "severity": "Medium",
            "detail"  : detail,
            "fix"     : None
        }


def _parse_value(output, label):
    # Each line looks like:  "Minimum password length:          0"
    # We find the line containing the label, split on ":", and take the right side
    for line in output.splitlines():
        if label.lower() in line.lower():
            parts = line.split(":")
            if len(parts) >= 2:
                return parts[1].strip()
    return "Unknown"


def _build_fix(failures):
    lines = ["Strengthen your local password policy:"]
    for msg in failures:
        if "length" in msg:
            lines.append(
                "\n  Password length is too short:\n"
                "  > Run (as admin): net accounts /minpwlen:8\n"
                "  > Or: Local Security Policy > Account Policies\n"
                "    > Password Policy > Minimum password length > set to 8"
            )
        if "never expire" in msg:
            lines.append(
                "\n  Passwords never expire:\n"
                "  > Run (as admin): net accounts /maxpwage:90\n"
                "  > Or: Local Security Policy > Account Policies\n"
                "    > Password Policy > Maximum password age > set to 90"
            )
    return "\n".join(lines)
