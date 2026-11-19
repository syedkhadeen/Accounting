"""Captures a screenshot of the unbalanced-entry rejection, as evidence
for assignment requirement 7 (validate debits = credits per entry)."""
from pathlib import Path
from playwright.sync_api import sync_playwright

URL = "http://localhost:8501"
OUT = Path(__file__).resolve().parent.parent / "screenshots"

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1440, "height": 1000})
    page.goto(URL, wait_until="networkidle")
    page.wait_for_timeout(2000)

    sidebar = page.get_by_test_id("stSidebar")
    sidebar.get_by_text("Record Transaction", exact=True).click()
    page.wait_for_timeout(1200)

    main = page.get_by_test_id("stMainBlockContainer")
    debit_inputs = main.locator('input[aria-label^="Debit"]')
    credit_inputs = main.locator('input[aria-label^="Credit"]')
    debit_inputs.nth(0).fill("500")
    credit_inputs.nth(1).fill("300")
    page.wait_for_timeout(500)

    page.get_by_role("button", name="Post Journal Entry").click()
    page.wait_for_timeout(1000)

    page.screenshot(path=str(OUT / "09_validation_rejected.png"), full_page=True)
    print("saved 09_validation_rejected.png")

    browser.close()
