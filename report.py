import os
from datetime import datetime

def generate_report(results):
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"Vantage_Report_{timestamp}.txt"
    filepath = os.path.join(desktop, filename)

    with open(filepath, "w") as f:
        f.write("=" * 60 + "\n")
        f.write("  VANTAGE — Windows Security Hardening Auditor\n")
        f.write(f"  Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")

        for result in results:
            f.write(result["title"] + "\n")
            f.write("-" * 60 + "\n")
            f.write(f"Status : {result['status']}\n")
            f.write(f"Severity: {result['severity']}\n\n")
            f.write(result["detail"] + "\n")
            if result["fix"]:
                f.write("\nHow to fix:\n")
                f.write(result["fix"] + "\n")
            f.write("\n" + "=" * 60 + "\n\n")
