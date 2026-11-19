"""Export journal, ledger, trial balance, and financial statements to CSV
in the reports/ directory."""
import csv
from pathlib import Path

from app.accounting import (
    get_journal,
    get_ledger,
    get_trial_balance,
    get_income_statement,
    get_balance_sheet,
)

REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"


def export_journal_csv():
    rows = get_journal()
    path = REPORTS_DIR / "journal.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Entry ID", "Date", "Reference", "Description", "Account Code", "Account", "Debit", "Credit"])
        for r in rows:
            writer.writerow([r["entry_id"], r["entry_date"], r["reference"], r["description"],
                              r["account_code"], r["account_name"], r["debit"], r["credit"]])
    return path


def export_ledger_csv():
    ledger = get_ledger()
    path = REPORTS_DIR / "ledger.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Account", "Code", "Date", "Description", "Debit", "Credit", "Balance"])
        for name, data in ledger.items():
            for row in data["rows"]:
                writer.writerow([name, data["code"], row["date"], row["description"],
                                  row["debit"], row["credit"], row["balance"]])
    return path


def export_trial_balance_csv():
    tb, total_debit, total_credit = get_trial_balance()
    path = REPORTS_DIR / "trial_balance.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Code", "Account", "Debit", "Credit"])
        for row in tb:
            writer.writerow([row["code"], row["account"], row["debit"], row["credit"]])
        writer.writerow(["", "TOTAL", total_debit, total_credit])
    return path


def export_income_statement_csv():
    stmt = get_income_statement()
    path = REPORTS_DIR / "income_statement.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Revenues"])
        for name, amt in stmt["revenues"].items():
            writer.writerow(["", name, amt])
        writer.writerow(["Total Revenue", "", stmt["total_revenue"]])
        writer.writerow([])
        writer.writerow(["Expenses"])
        for name, amt in stmt["expenses"].items():
            writer.writerow(["", name, amt])
        writer.writerow(["Total Expenses", "", stmt["total_expense"]])
        writer.writerow([])
        writer.writerow(["Net Income", "", stmt["net_income"]])
    return path


def export_balance_sheet_csv():
    bs = get_balance_sheet()
    path = REPORTS_DIR / "balance_sheet.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Assets"])
        for name, amt in bs["assets"].items():
            writer.writerow(["", name, amt])
        writer.writerow(["Total Assets", "", bs["total_assets"]])
        writer.writerow([])
        writer.writerow(["Liabilities"])
        for name, amt in bs["liabilities"].items():
            writer.writerow(["", name, amt])
        writer.writerow(["Total Liabilities", "", bs["total_liabilities"]])
        writer.writerow([])
        writer.writerow(["Equity"])
        for name, amt in bs["equity"].items():
            writer.writerow(["", name, amt])
        writer.writerow(["", "Net Income", bs["net_income"]])
        writer.writerow(["Total Equity", "", bs["total_equity"]])
        writer.writerow([])
        writer.writerow(["Balanced (Assets = Liabilities + Equity)", "", bs["balances"]])
    return path


def export_all():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    return [
        export_journal_csv(),
        export_ledger_csv(),
        export_trial_balance_csv(),
        export_income_statement_csv(),
        export_balance_sheet_csv(),
    ]
