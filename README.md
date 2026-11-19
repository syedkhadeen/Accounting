# Small Business Accounting System

Streamlit + SQLite implementation of the fundamental accounting cycle:
chart of accounts, double-entry journal, general ledger, unadjusted
trial balance, income statement, and balance sheet.


## Setup

```
pip install -r requirements.txt
streamlit run bookkeeping_app.py
```

First launch auto-seeds the chart of accounts and 18 sample
transactions into `data/bookkeeper.db`.

## Project Layout

```
app/
  db.py          SQLite schema + connection
  accounting.py  double-entry posting, ledger, trial balance, statements
  seed.py        chart of accounts + 18 sample transactions
  reports.py     CSV export (journal, ledger, trial balance, statements)
bookkeeping_app.py   Streamlit UI
scripts/screenshot.py             captures UI screenshots (requires playwright)
scripts/screenshot_validation.py  captures the validation-rejected screenshot
data/            SQLite database file (generated)
reports/         generated CSV reports
screenshots/     UI screenshots for documentation
docs/Project_Report.tex   full project report (LaTeX)
docs/diagrams/            PlantUML source for the architecture, flow, and ER diagrams
```

## Core Rule

Every journal entry must satisfy `sum(debit) == sum(credit)` or it is
rejected by `app/accounting.py::post_entry` before it reaches the
database - see `UnbalancedEntryError`.
