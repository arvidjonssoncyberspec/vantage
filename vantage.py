import os
import sys
from checks import firewall, defender, uac, password_policy
from report import generate_report

def clear():
    os.system("cls")

def wait():
    input("\nPress Enter to continue...")

def main():
    clear()
    print("=" * 60)
    print("  VANTAGE — Windows Security Hardening Auditor")
    print("=" * 60)
    print("\nThis tool will scan your system for common security")
    print("weaknesses and tell you how to fix them.")
    print("\nNo changes will be made to your system.")
    wait()

    results = []

    # --- Run checks ---
    results.append(firewall.run(wait))
    results.append(defender.run(wait))
    results.append(uac.run(wait))
    results.append(password_policy.run(wait))

    # --- Generate report ---
    generate_report(results)
    print("\nAudit complete. Report saved to your Desktop.")
    print("=" * 60)

if __name__ == "__main__":
    main()
