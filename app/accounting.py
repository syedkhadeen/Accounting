"""Core accounting logic: chart of accounts, journal posting, ledger,
trial balance, and financial statements. Implements double-entry
bookkeeping on top of the SQLite schema in db.py.
"""
from app.db import get_connection

DEBIT_NORMAL_TYPES = {"Asset", "Expense"}
CREDIT_NORMAL_TYPES = {"Liability", "Equity", "Revenue"}


class UnbalancedEntryError(Exception):
    pass


def normal_balance_for(account_type: str) -> str:
    return "Debit" if account_type in DEBIT_NORMAL_TYPES else "Credit"


# ---------------------------------------------------------------- Chart of Accounts
def add_account(code: str, name: str, account_type: str):
    conn = get_connection()
    conn.execute(
        "INSERT INTO accounts (code, name, type, normal_balance) VALUES (?, ?, ?, ?)",
        (code, name, account_type, normal_balance_for(account_type)),
    )
    conn.commit()
    conn.close()


def get_accounts():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM accounts ORDER BY code").fetchall()
    conn.close()
    return rows


def get_account_by_name(name: str):
    conn = get_connection()
    row = conn.execute("SELECT * FROM accounts WHERE name = ?", (name,)).fetchone()
    conn.close()
    return row


# ---------------------------------------------------------------- Journal
def post_entry(entry_date: str, description: str, lines: list[dict], reference: str = ""):
    """lines: [{"account": name, "debit": 0, "credit": 0}, ...]
    Raises UnbalancedEntryError if total debits != total credits.
    """
    total_debit = round(sum(l.get("debit", 0) for l in lines), 2)
    total_credit = round(sum(l.get("credit", 0) for l in lines), 2)
    if total_debit != total_credit:
        raise UnbalancedEntryError(
            f"Debits ({total_debit}) do not equal credits ({total_credit})"
        )
    if total_debit == 0:
        raise UnbalancedEntryError("Entry has zero amount")

    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO journal_entries (entry_date, reference, description) VALUES (?, ?, ?)",
        (entry_date, reference, description),
    )
    entry_id = cur.lastrowid
    for line in lines:
        account = conn.execute(
            "SELECT id FROM accounts WHERE name = ?", (line["account"],)
        ).fetchone()
        if account is None:
            conn.rollback()
            conn.close()
            raise ValueError(f"Unknown account: {line['account']}")
        conn.execute(
            "INSERT INTO journal_lines (entry_id, account_id, debit, credit) VALUES (?, ?, ?, ?)",
            (entry_id, account["id"], line.get("debit", 0), line.get("credit", 0)),
        )
    conn.commit()
    conn.close()
    return entry_id


def get_journal():
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT je.id AS entry_id, je.entry_date, je.reference, je.description,
               a.code AS account_code, a.name AS account_name,
               jl.debit, jl.credit
        FROM journal_entries je
        JOIN journal_lines jl ON jl.entry_id = je.id
        JOIN accounts a ON a.id = jl.account_id
        ORDER BY je.entry_date, je.id, jl.id
        """
    ).fetchall()
    conn.close()
    return rows


# ---------------------------------------------------------------- Ledger
def get_ledger(account_name: str = None):
    """Returns per-account list of postings with running balance.
    If account_name given, returns only that account's ledger."""
    conn = get_connection()
    accounts = conn.execute(
        "SELECT * FROM accounts" + (" WHERE name = ?" if account_name else "") + " ORDER BY code",
        (account_name,) if account_name else (),
    ).fetchall()

    ledger = {}
    for acct in accounts:
        lines = conn.execute(
            """
            SELECT je.entry_date, je.description, jl.debit, jl.credit
            FROM journal_lines jl
            JOIN journal_entries je ON je.id = jl.entry_id
            WHERE jl.account_id = ?
            ORDER BY je.entry_date, je.id, jl.id
            """,
            (acct["id"],),
        ).fetchall()

        balance = 0.0
        rows = []
        for line in lines:
            if acct["normal_balance"] == "Debit":
                balance += line["debit"] - line["credit"]
            else:
                balance += line["credit"] - line["debit"]
            rows.append(
                {
                    "date": line["entry_date"],
                    "description": line["description"],
                    "debit": line["debit"],
                    "credit": line["credit"],
                    "balance": round(balance, 2),
                }
            )
        ledger[acct["name"]] = {
            "code": acct["code"],
            "type": acct["type"],
            "normal_balance": acct["normal_balance"],
            "rows": rows,
            "ending_balance": round(balance, 2),
        }
    conn.close()
    return ledger


# ---------------------------------------------------------------- Trial Balance
def get_trial_balance():
    ledger = get_ledger()
    tb = []
    total_debit = 0.0
    total_credit = 0.0
    for name, data in ledger.items():
        balance = data["ending_balance"]
        debit_col = balance if data["normal_balance"] == "Debit" and balance >= 0 else 0
        credit_col = balance if data["normal_balance"] == "Credit" and balance >= 0 else 0
        # handle accounts that went negative (abnormal balance) by flipping column
        if balance < 0:
            if data["normal_balance"] == "Debit":
                credit_col = -balance
                debit_col = 0
            else:
                debit_col = -balance
                credit_col = 0
        tb.append(
            {
                "code": data["code"],
                "account": name,
                "debit": round(debit_col, 2),
                "credit": round(credit_col, 2),
            }
        )
        total_debit += debit_col
        total_credit += credit_col
    return tb, round(total_debit, 2), round(total_credit, 2)


# ---------------------------------------------------------------- Financial Statements
def get_income_statement():
    ledger = get_ledger()
    revenues = {n: d["ending_balance"] for n, d in ledger.items() if d["type"] == "Revenue"}
    expenses = {n: d["ending_balance"] for n, d in ledger.items() if d["type"] == "Expense"}
    total_revenue = round(sum(revenues.values()), 2)
    total_expense = round(sum(expenses.values()), 2)
    net_income = round(total_revenue - total_expense, 2)
    return {
        "revenues": revenues,
        "expenses": expenses,
        "total_revenue": total_revenue,
        "total_expense": total_expense,
        "net_income": net_income,
    }


def get_balance_sheet():
    ledger = get_ledger()
    income = get_income_statement()
    assets = {n: d["ending_balance"] for n, d in ledger.items() if d["type"] == "Asset"}
    liabilities = {n: d["ending_balance"] for n, d in ledger.items() if d["type"] == "Liability"}
    equity = {n: d["ending_balance"] for n, d in ledger.items() if d["type"] == "Equity"}

    total_assets = round(sum(assets.values()), 2)
    total_liabilities = round(sum(liabilities.values()), 2)
    total_equity_before_income = round(sum(equity.values()), 2)
    total_equity = round(total_equity_before_income + income["net_income"], 2)

    return {
        "assets": assets,
        "liabilities": liabilities,
        "equity": equity,
        "net_income": income["net_income"],
        "total_assets": total_assets,
        "total_liabilities": total_liabilities,
        "total_equity": total_equity,
        "balances": total_assets == round(total_liabilities + total_equity, 2),
    }
