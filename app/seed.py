"""Seeds the chart of accounts and a sample dataset of 18 business
transactions for a small business (demo: "Khadeen Trading Co.")."""
from app.db import init_db, is_empty
from app.accounting import add_account, post_entry

CHART_OF_ACCOUNTS = [
    ("1010", "Cash", "Asset"),
    ("1020", "Accounts Receivable", "Asset"),
    ("1030", "Supplies", "Asset"),
    ("1040", "Equipment", "Asset"),
    ("2010", "Accounts Payable", "Liability"),
    ("2020", "Notes Payable", "Liability"),
    ("3010", "Owner's Capital", "Equity"),
    ("3020", "Owner's Drawings", "Equity"),
    ("4010", "Service Revenue", "Revenue"),
    ("5010", "Rent Expense", "Expense"),
    ("5020", "Salaries Expense", "Expense"),
    ("5030", "Utilities Expense", "Expense"),
    ("5040", "Advertising Expense", "Expense"),
]

TRANSACTIONS = [
    ("2026-11-01", "Owner invested cash to start the business", "JE-01",
     [{"account": "Cash", "debit": 50000}, {"account": "Owner's Capital", "credit": 50000}]),
    ("2026-11-01", "Purchased equipment for cash", "JE-02",
     [{"account": "Equipment", "debit": 12000}, {"account": "Cash", "credit": 12000}]),
    ("2026-11-02", "Purchased supplies on account", "JE-03",
     [{"account": "Supplies", "debit": 3000}, {"account": "Accounts Payable", "credit": 3000}]),
    ("2026-11-03", "Borrowed cash from bank (note payable)", "JE-04",
     [{"account": "Cash", "debit": 15000}, {"account": "Notes Payable", "credit": 15000}]),
    ("2026-11-04", "Billed client for services rendered on account", "JE-05",
     [{"account": "Accounts Receivable", "debit": 8000}, {"account": "Service Revenue", "credit": 8000}]),
    ("2026-11-05", "Received cash for services rendered", "JE-06",
     [{"account": "Cash", "debit": 6000}, {"account": "Service Revenue", "credit": 6000}]),
    ("2026-11-06", "Paid rent for the month", "JE-07",
     [{"account": "Rent Expense", "debit": 2500}, {"account": "Cash", "credit": 2500}]),
    ("2026-11-07", "Paid partial amount owed to supplier", "JE-08",
     [{"account": "Accounts Payable", "debit": 1000}, {"account": "Cash", "credit": 1000}]),
    ("2026-11-08", "Received partial payment from client", "JE-09",
     [{"account": "Cash", "debit": 4000}, {"account": "Accounts Receivable", "credit": 4000}]),
    ("2026-11-09", "Paid salaries to staff", "JE-10",
     [{"account": "Salaries Expense", "debit": 3500}, {"account": "Cash", "credit": 3500}]),
    ("2026-11-10", "Paid electricity and water bill", "JE-11",
     [{"account": "Utilities Expense", "debit": 600}, {"account": "Cash", "credit": 600}]),
    ("2026-11-11", "Owner withdrew cash for personal use", "JE-12",
     [{"account": "Owner's Drawings", "debit": 2000}, {"account": "Cash", "credit": 2000}]),
    ("2026-11-12", "Paid for newspaper advertisement", "JE-13",
     [{"account": "Advertising Expense", "debit": 800}, {"account": "Cash", "credit": 800}]),
    ("2026-11-13", "Billed another client for services on account", "JE-14",
     [{"account": "Accounts Receivable", "debit": 5000}, {"account": "Service Revenue", "credit": 5000}]),
    ("2026-11-14", "Purchased additional supplies for cash", "JE-15",
     [{"account": "Supplies", "debit": 700}, {"account": "Cash", "credit": 700}]),
    ("2026-11-15", "Made partial repayment of bank note", "JE-16",
     [{"account": "Notes Payable", "debit": 2500}, {"account": "Cash", "credit": 2500}]),
    ("2026-11-16", "Received cash for services rendered", "JE-17",
     [{"account": "Cash", "debit": 3200}, {"account": "Service Revenue", "credit": 3200}]),
    ("2026-11-17", "Paid remaining balance to supplier", "JE-18",
     [{"account": "Accounts Payable", "debit": 2000}, {"account": "Cash", "credit": 2000}]),
]


def seed():
    init_db()
    if not is_empty():
        return False
    for code, name, acct_type in CHART_OF_ACCOUNTS:
        add_account(code, name, acct_type)
    for entry_date, description, reference, lines in TRANSACTIONS:
        post_entry(entry_date, description, lines, reference)
    return True


if __name__ == "__main__":
    seeded = seed()
    print("Seeded demo dataset." if seeded else "Database already has data; skipped seeding.")
