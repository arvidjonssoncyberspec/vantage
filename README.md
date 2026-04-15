# Vantage — Windows Security Hardening Auditor

Vantage is a Python-based CLI tool that audits your Windows system for common
security weaknesses and tells you exactly how to fix them. It is designed to be
simple, transparent, and safe — it never modifies your system.

---

## What it does

Vantage runs 10 security checks against your local machine and produces a
written report saved to your Desktop. Each failed check includes plain-English
fix instructions shown directly in the terminal.

---

## Checks

| # | Check | What it looks for |
|---|---|---|
| 1 | Windows Firewall | All three profiles (Domain, Private, Public) are enabled |
| 2 | Antivirus | A registered and active antivirus product is present |
| 3 | UAC | User Account Control is enabled |
| 4 | Password Policy | Minimum length of 8+, passwords are set to expire |
| 5 | Guest Account | Built-in Guest account is disabled |
| 6 | Administrator Account | Built-in Administrator account is disabled |
| 7 | Open Ports | Flags known risky listening ports, checks firewall block status |
| 8 | Running Services | Flags known risky or unnecessary running services |
| 9 | Startup Programs | Flags entries running from suspicious paths |
| 10 | Windows Updates | Checks for pending updates via the Windows Update service |

---

## Requirements

- Windows 10 or Windows 11
- Python 3.8 or higher
- No third-party packages — standard library only

---

## Installation

**1. Clone the repository**

```
git clone https://github.com/arvidjonssoncyberspec/vantage.git
cd vantage
```

**2. Run Vantage**

```
python vantage.py
```

> Vantage does not require administrator privileges to run.
> All checks work as a standard user.
>
> Note: the fix commands shown in the terminal (e.g. disabling accounts
> or blocking ports) do require an administrator terminal to execute.

---

## How it works

Vantage steps through each check one at a time. After each check you will see:

- The result — `[PASS]` or `[FAIL]`
- A short summary of what was found
- Fix instructions printed directly in the terminal if the check failed

Press **Enter** to move to the next check. Once all checks are complete, a
full report is saved as a `.txt` file on your Desktop.

---

## Report

At the end of the audit, Vantage saves a timestamped report to your Desktop:

```
Vantage_Report_2026-04-15_14-30-00.txt
```

The report includes the result, severity, and fix instructions for every check.

---

## Important notes

- Vantage is **read-only**. It will never make changes to your system.
- Vantage does not require administrator privileges to run.
- Fix instructions are suggestions. Research before applying changes,
  especially when disabling services or blocking ports.
- Fix commands shown in the terminal require an administrator terminal to execute.
- Some checks (e.g. Windows Updates) may take a few seconds to complete.

---

## Project structure

```
vantage/
├── vantage.py          # Entry point
├── report.py           # Report generation
└── checks/
    ├── firewall.py
    ├── defender.py
    ├── uac.py
    ├── password_policy.py
    ├── guest_account.py
    ├── admin_account.py
    ├── open_ports.py
    ├── services.py
    ├── startup.py
    └── updates.py
```

---

## Author

Arvid Jonsson — IT and Information Security student
GitHub: [arvidjonssoncyberspec](https://github.com/arvidjonssoncyberspec)
