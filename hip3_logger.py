# HIP-3 daily logger -> Google Sheets (version GitHub Actions)
# Lee credenciales de variables de entorno; no hay nada que editar aca.
import os, json
import requests
from datetime import datetime, timezone
import gspread
from google.oauth2.service_account import Credentials

SHEET_ID  = os.environ["SHEET_ID"]
SA_JSON   = os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]
WORKSHEET = "markets"
MY_DEXES  = ["mkts", "km"]
API       = "https://api.hyperliquid.xyz/info"

HEADERS = ["date_utc", "dex", "dex_full_name", "coin", "is_markets",
           "volume_24h_usd", "open_interest_usd", "mark_px", "oracle_px",
           "funding_rate", "delisted"]

scopes = ["https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(json.loads(SA_JSON), scopes=scopes)
gc = gspread.authorize(creds)
sh = gc.open_by_key(SHEET_ID)

try:
    ws = sh.worksheet(WORKSHEET)
except gspread.WorksheetNotFound:
    ws = sh.add_worksheet(title=WORKSHEET, rows=1000, cols=len(HEADERS))
    ws.append_row(HEADERS)

today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
if today in set(ws.col_values(1)[1:]):
    print(f"Ya hay filas para {today}. Nada que hacer.")
    raise SystemExit(0)

dexes = [d for d in requests.post(API, json={"type": "perpDexs"}, timeout=30).json() if d]

rows = []
for d in dexes:
    dex = d["name"]
    try:
        meta, ctxs = requests.post(API, json={"type": "metaAndAssetCtxs", "dex": dex}, timeout=30).json()
    except Exception as e:
        print(f"[{dex}] error: {e}")
        continue
    for a, c in zip(meta["universe"], ctxs):
        vol = float(c.get("dayNtlVlm") or 0)
        oi_units = float(c.get("openInterest") or 0)
        mark = float(c.get("markPx") or 0)
        delisted = bool(a.get("isDelisted", False))
        if delisted and vol == 0 and oi_units == 0:
            continue
        rows.append([today, dex, d.get("fullName", ""), a["name"], dex in MY_DEXES,
                     round(vol, 2), round(oi_units * mark, 2), mark,
                     float(c.get("oraclePx") or 0), float(c.get("funding") or 0), delisted])

if rows:
    ws.append_rows(rows, value_input_option="RAW")

markets_vol = sum(r[5] for r in rows if r[4])
total_vol = sum(r[5] for r in rows)
share = markets_vol / total_vol * 100 if total_vol else 0
print(f"{today}: {len(rows)} filas guardadas")
print(f"Markets (deployer): ${markets_vol:,.0f} de ${total_vol:,.0f} en HIP-3 ({share:.1f}%)")
