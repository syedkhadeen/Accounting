"""Captures screenshots of every page of the running Streamlit app for
the project documentation. Requires the app to already be running on
http://localhost:8501."""
from pathlib import Path
from playwright.sync_api import sync_playwright

URL = "http://localhost:8501"
OUT = Path(__file__).resolve().parent.parent / "screenshots"
OUT.mkdir(parents=True, exist_ok=True)

PAGES = [
    "Chart of Accounts",
    "Record Transaction",
    "Journal",
    "General Ledger",
    "Trial Balance",
    "Income Statement",
    "Balance Sheet",
    "Export Reports",
]

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1440, "height": 1000})
    page.goto(URL, wait_until="networkidle")
    page.wait_for_timeout(2000)

    sidebar = page.get_by_test_id("stSidebar")
    for i, label in enumerate(PAGES, start=1):
        radio = sidebar.get_by_text(label, exact=True)
        radio.click()
        page.wait_for_timeout(1200)
        if label == "Export Reports":
            page.get_by_role("button", name="Generate All Reports").click()
            page.wait_for_timeout(1000)
        fname = OUT / f"{i:02d}_{label.lower().replace(' ', '_')}.png"
        page.screenshot(path=str(fname), full_page=True)
        print("saved", fname)

    browser.close()
