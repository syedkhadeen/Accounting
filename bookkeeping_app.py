"""Small Business Accounting System
Streamlit front end implementing the full accounting cycle: chart of
accounts, journal entries, general ledger, trial balance, and financial
statements (income statement & balance sheet).
"""
import pandas as pd
import streamlit as st

from app.db import init_db, is_empty
from app.accounting import (
    add_account,
    get_accounts,
    post_entry,
    get_journal,
    get_ledger,
    get_trial_balance,
    get_income_statement,
    get_balance_sheet,
    UnbalancedEntryError,
)
from app.seed import seed
from app.reports import export_all


def full_height(df):
    return 38 + 35 * len(df)


st.set_page_config(page_title="Small Business Accounting System", layout="wide")

init_db()
if is_empty():
    seed()

st.title("Small Business Accounting System")
st.caption("Fundamentals of Accounting - Project: Small Business Accounting System")

page = st.sidebar.radio(
    "Navigate",
    [
        "Chart of Accounts",
        "Record Transaction",
        "Journal",
        "General Ledger",
        "Trial Balance",
        "Income Statement",
        "Balance Sheet",
        "Export Reports",
    ],
)

# ---------------------------------------------------------------- Chart of Accounts
if page == "Chart of Accounts":
    st.header("Chart of Accounts")
    accounts = get_accounts()
    df = pd.DataFrame(
        [{"Code": a["code"], "Name": a["name"], "Type": a["type"], "Normal Balance": a["normal_balance"]} for a in accounts]
    )
    st.dataframe(df, use_container_width=True, hide_index=True, height=full_height(df))

    with st.expander("Add new account"):
        with st.form("add_account_form"):
            code = st.text_input("Account code (e.g. 1050)")
            name = st.text_input("Account name")
            acct_type = st.selectbox("Account type", ["Asset", "Liability", "Equity", "Revenue", "Expense"])
            submitted = st.form_submit_button("Add Account")
            if submitted:
                if not code or not name:
                    st.error("Code and name are required.")
                else:
                    try:
                        add_account(code, name, acct_type)
                        st.success(f"Account '{name}' added.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Could not add account: {e}")

# ---------------------------------------------------------------- Record Transaction
elif page == "Record Transaction":
    st.header("Record a Business Transaction")
    accounts = [a["name"] for a in get_accounts()]

    entry_date = st.date_input("Date")
    reference = st.text_input("Reference / Voucher No.", value="")
    description = st.text_input("Description")

    st.subheader("Journal Lines")
    n_lines = st.number_input("Number of lines", min_value=2, max_value=10, value=2, step=1)

    lines = []
    total_debit = 0.0
    total_credit = 0.0
    for i in range(int(n_lines)):
        c1, c2, c3 = st.columns([3, 1, 1])
        with c1:
            acct = st.selectbox(f"Account {i+1}", accounts, key=f"acct_{i}")
        with c2:
            debit = st.number_input(f"Debit {i+1}", min_value=0.0, step=100.0, key=f"debit_{i}")
        with c3:
            credit = st.number_input(f"Credit {i+1}", min_value=0.0, step=100.0, key=f"credit_{i}")
        lines.append({"account": acct, "debit": debit, "credit": credit})
        total_debit += debit
        total_credit += credit

    st.markdown(f"**Total Debit:** {total_debit:,.2f}  |  **Total Credit:** {total_credit:,.2f}")
    if round(total_debit, 2) == round(total_credit, 2) and total_debit > 0:
        st.success("Debits equal credits. Entry is balanced.")
    else:
        st.warning("Debits must equal credits before posting.")

    if st.button("Post Journal Entry"):
        try:
            entry_id = post_entry(str(entry_date), description or "(no description)", lines, reference)
            st.success(f"Posted journal entry #{entry_id}.")
            st.rerun()
        except UnbalancedEntryError as e:
            st.error(f"Entry rejected: {e}")
        except ValueError as e:
            st.error(f"Entry rejected: {e}")

# ---------------------------------------------------------------- Journal
elif page == "Journal":
    st.header("General Journal")
    rows = get_journal()
    df = pd.DataFrame(
        [
            {
                "Entry": r["entry_id"],
                "Date": r["entry_date"],
                "Ref": r["reference"],
                "Description": r["description"],
                "Account": r["account_name"],
                "Debit": r["debit"],
                "Credit": r["credit"],
            }
            for r in rows
        ]
    )
    st.dataframe(df, use_container_width=True, hide_index=True, height=full_height(df))

# ---------------------------------------------------------------- General Ledger
elif page == "General Ledger":
    st.header("General Ledger")
    ledger = get_ledger()
    account_names = list(ledger.keys())
    choice = st.selectbox("Select account", account_names)
    data = ledger[choice]
    st.markdown(f"**Code:** {data['code']}  |  **Type:** {data['type']}  |  **Normal Balance:** {data['normal_balance']}")
    df = pd.DataFrame(data["rows"])
    st.dataframe(df, use_container_width=True, hide_index=True, height=full_height(df))
    st.markdown(f"**Ending Balance: {data['ending_balance']:,.2f}**")

# ---------------------------------------------------------------- Trial Balance
elif page == "Trial Balance":
    st.header("Unadjusted Trial Balance")
    tb, total_debit, total_credit = get_trial_balance()
    df = pd.DataFrame(tb)
    st.dataframe(df, use_container_width=True, hide_index=True, height=full_height(df))
    st.markdown(f"**Total Debit: {total_debit:,.2f}  |  Total Credit: {total_credit:,.2f}**")
    if total_debit == total_credit:
        st.success("Trial balance is balanced.")
    else:
        st.error("Trial balance is NOT balanced. Check journal entries.")

# ---------------------------------------------------------------- Income Statement
elif page == "Income Statement":
    st.header("Income Statement")
    stmt = get_income_statement()
    st.subheader("Revenues")
    st.table(pd.DataFrame(list(stmt["revenues"].items()), columns=["Account", "Amount"]))
    st.markdown(f"**Total Revenue: {stmt['total_revenue']:,.2f}**")
    st.subheader("Expenses")
    st.table(pd.DataFrame(list(stmt["expenses"].items()), columns=["Account", "Amount"]))
    st.markdown(f"**Total Expenses: {stmt['total_expense']:,.2f}**")
    st.markdown(f"## Net Income: {stmt['net_income']:,.2f}")

# ---------------------------------------------------------------- Balance Sheet
elif page == "Balance Sheet":
    st.header("Balance Sheet")
    bs = get_balance_sheet()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Assets")
        st.table(pd.DataFrame(list(bs["assets"].items()), columns=["Account", "Amount"]))
        st.markdown(f"**Total Assets: {bs['total_assets']:,.2f}**")
    with col2:
        st.subheader("Liabilities")
        st.table(pd.DataFrame(list(bs["liabilities"].items()), columns=["Account", "Amount"]))
        st.markdown(f"**Total Liabilities: {bs['total_liabilities']:,.2f}**")
        st.subheader("Equity")
        equity_rows = list(bs["equity"].items()) + [("Net Income", bs["net_income"])]
        st.table(pd.DataFrame(equity_rows, columns=["Account", "Amount"]))
        st.markdown(f"**Total Equity: {bs['total_equity']:,.2f}**")

    if bs["balances"]:
        st.success(f"Balance sheet is balanced: Assets ({bs['total_assets']:,.2f}) = Liabilities + Equity ({bs['total_liabilities'] + bs['total_equity']:,.2f})")
    else:
        st.error("Balance sheet does NOT balance. Check journal entries.")

# ---------------------------------------------------------------- Export
elif page == "Export Reports":
    st.header("Export Reports")
    st.write("Generates CSV files for journal, ledger, trial balance, and financial statements in the reports/ folder.")
    if st.button("Generate All Reports"):
        paths = export_all()
        st.success("Reports generated:")
        for p in paths:
            st.write(f"- {p}")
