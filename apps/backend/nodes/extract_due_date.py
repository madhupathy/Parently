import re
from datetime import datetime, timedelta
from dateutil import parser as dateparser

WEEKDAYS = "(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)"
DATE1 = r"\b\d{4}-\d{2}-\d{2}\b"
DATE2 = r"\b\d{1,2}/\d{1,2}(?:/\d{2,4})?\b"
PHRASES = rf"(?:due|by|return)\s*(?:on|by)?\s*(?:{WEEKDAYS}|\d{{1,2}}/\d{{1,2}}(?:/\d{{2,4}})?|\d{{4}}-\d{{2}}-\d{{2}})"

def extract_first_due_date(text: str, now: datetime | None = None) -> str | None:
    if not text:
        return None
    now = now or datetime.now()
    # yyyy-mm-dd explicit
    m = re.search(DATE1, text)
    if m:
        return m.group(0)
    # phrases with weekday or date token
    m = re.search(PHRASES, text, flags=re.IGNORECASE)
    if m:
        frag = m.group(0)
        m2 = re.search(DATE1 + "|" + DATE2 + "|" + WEEKDAYS, frag, re.IGNORECASE)
        if m2:
            token = m2.group(0)
            try:
                dt = None
                if re.fullmatch(WEEKDAYS, token, flags=re.IGNORECASE):
                    weekday = ["mon","tue","wed","thu","fri","sat","sun"].index(token[:3].lower())
                    delta = (weekday - now.weekday()) % 7
                    delta = 7 if delta == 0 else delta
                    dt = now + timedelta(days=delta)
                else:
                    dt = dateparser.parse(token, dayfirst=False, yearfirst=False, default=now)
                return dt.strftime("%Y-%m-%d")
            except Exception:
                pass
    # plain mm/dd
    m = re.search(DATE2, text)
    if m:
        try:
            dt = dateparser.parse(m.group(0), default=now)
            return dt.strftime("%Y-%m-%d")
        except Exception:
            return None
    return None

def extract_due_date_node(state: dict) -> dict:
    out = []
    for it in state.get("items", []):
        if not it.get("due_date"):
            dd = extract_first_due_date(it.get("text",""))
            it["due_date"] = dd
        out.append(it)
    state["items"] = out
    return state
