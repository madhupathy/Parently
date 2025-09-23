from datetime import datetime
from nodes.extract_due_date import extract_first_due_date

def test_iso_date():
    txt = "Permission slip due 2025-09-25."
    assert extract_first_due_date(txt, now=datetime(2025,9,18)) == "2025-09-25"

def test_mmdd_week_context():
    txt = "Return by 9/25 for the field trip."
    assert extract_first_due_date(txt, now=datetime(2025,9,18)) == "2025-09-25"

def test_weekday_phrase():
    txt = "Due Friday at noon"
    # 2025-09-18 is Thursday; next Friday is 2025-09-19
    assert extract_first_due_date(txt, now=datetime(2025,9,18)) == "2025-09-19"

def test_no_date():
    txt = "General newsletter."
    assert extract_first_due_date(txt, now=datetime(2025,9,18)) is None
