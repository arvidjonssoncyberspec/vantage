import subprocess

RISKY_SERVICES = {
    "TlntSvr"       : "Telnet — unencrypted remote access",
    "RemoteRegistry": "Remote Registry — allows remote editing of your registry",
    "WinRM"         : "Windows Remote Management — common attack vector",
    "SNMP"          : "SNMP — network monitoring, often misconfigured",
    "Fax"           : "Fax — rarely needed, unnecessary attack surface",
    "XboxGipSvc"    : "Xbox GIP Service — unnecessary on non-gaming machines",
    "SharedAccess"  : "Internet Connection Sharing — exposes your connection to others",
}

def run(wait):
    print("\n[8/10] Checking running services...")

    result = subprocess.run(
        ["sc", "query", "type=", "all", "state=", "running"],
        capture_output=True,
        text=True
    )

    running = _parse_running_services(result.stdout)
    flagged = {name: desc for name, desc in RISKY_SERVICES.items() if name.lower() in running}

    if not flagged:
        print("\n  [PASS] No known risky services are running.")
        wait()
        return {
            "title"   : "8. Running Services",
            "status"  : "PASS",
            "severity": "Medium",
            "detail"  : "No known risky services detected.",
            "fix"     : None
        }

    print("\n  Risky services detected:")
    detail_lines = ["Risky services detected:"]
    for name, desc in flagged.items():
        line = f"    {name} — {desc}"
        print(line)
        detail_lines.append(line)

    print("\n  [FAIL] One or more risky services are running.")
    print("\n  How to fix:")
    for name in flagged:
        print(f"\n  {'─' * 44}")
        print(f"  {name}:")
        _print_fix(name)

    wait()
    return {
        "title"   : "8. Running Services",
        "status"  : "FAIL",
        "severity": "Medium",
        "detail"  : "\n".join(detail_lines),
        "fix"     : _build_report_fix(flagged)
    }


def _print_fix(name):
    fixes = {
        "TlntSvr": [
            "  > Run (as admin): sc stop TlntSvr && sc config TlntSvr start= disabled",
            "  > Or: Services app (services.msc) > Telnet > right-click > Stop",
            "    then Properties > Startup type > Disabled",
        ],
        "RemoteRegistry": [
            "  > Run (as admin): sc stop RemoteRegistry && sc config RemoteRegistry start= disabled",
            "  > Or: Services app (services.msc) > Remote Registry > right-click > Stop",
            "    then Properties > Startup type > Disabled",
        ],
        "WinRM": [
            "  > Run (as admin): sc stop WinRM && sc config WinRM start= disabled",
            "  > Or: Services app (services.msc) > Windows Remote Management > right-click > Stop",
            "    then Properties > Startup type > Disabled",
        ],
        "SNMP": [
            "  > Run (as admin): sc stop SNMP && sc config SNMP start= disabled",
            "  > Or: Services app (services.msc) > SNMP Service > right-click > Stop",
            "    then Properties > Startup type > Disabled",
        ],
        "Fax": [
            "  > Run (as admin): sc stop Fax && sc config Fax start= disabled",
            "  > Or: Services app (services.msc) > Fax > right-click > Stop",
            "    then Properties > Startup type > Disabled",
        ],
        "XboxGipSvc": [
            "  > Run (as admin): sc stop XboxGipSvc && sc config XboxGipSvc start= disabled",
            "  > Or: Services app (services.msc) > Xbox GIP Service > right-click > Stop",
            "    then Properties > Startup type > Disabled",
        ],
        "SharedAccess": [
            "  Note: Only disable if you are not sharing your internet connection",
            "  with other devices.",
            "  > Run (as admin): sc stop SharedAccess && sc config SharedAccess start= disabled",
            "  > Or: Services app (services.msc) > Internet Connection Sharing > right-click > Stop",
            "    then Properties > Startup type > Disabled",
        ],
    }
    for line in fixes.get(name, [f"  > Run (as admin): sc stop {name} && sc config {name} start= disabled"]):
        print(line)


def _build_report_fix(flagged):
    lines = ["Disable the following risky services:"]
    for name in flagged:
        lines.append(f"\n  {name}:")
        lines.append(f"  > Run (as admin): sc stop {name} && sc config {name} start= disabled")
        lines.append(f"  > Or: services.msc > {name} > Stop, then set Startup type to Disabled")
    return "\n".join(lines)


def _parse_running_services(output):
    services = set()
    for line in output.splitlines():
        if line.strip().startswith("SERVICE_NAME:"):
            name = line.split(":", 1)[1].strip().lower()
            services.add(name)
    return services
