#!/usr/bin/env python3
"""Days on Hand / Sales Velocity Analysis for 10 demo products.

Queries VIP DAILYT for 2+ years of sales history, calculates velocity metrics
(day-of-week patterns, monthly seasonality, current rates), and writes results
to the Google Sheets workbook.

Output tabs:
  - Velocity_Analysis: summary, DOW patterns, seasonality, DOH calculator
"""

import os
import time
from datetime import date, timedelta
from pathlib import Path

import gspread
import pandas as pd
import psycopg2
import psycopg2.extras
from google.oauth2.service_account import Credentials

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DB_CONFIG = {
    "host": os.getenv("PGHOST", "gulfstream-db2-data.postgres.database.azure.com"),
    "port": int(os.getenv("PGPORT", "5432")),
    "dbname": os.getenv("PGDATABASE", "gulfstream"),
    "user": os.getenv("PGUSER", "ohanafy"),
    "password": os.getenv("PGPASSWORD", "Xq7!mR#2vK$9pLw@nZ"),
    "sslmode": "require",
}

SERVICE_ACCOUNT_PATH = Path("/Users/danielzeder/Desktop/VIP to Ohanafy/service-account.json")
SHEET_ID = "108Eyx2n16FzOilD7Kaze1YTKF_NQBDYoHsb3svlDeWE"
SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
]

DEMO_ITEMS = [
    "05716",
    "10216",
    "22133",
    "22813",
    "77527",
    "77577",
    "28065",
    "28069",
    "49513",
    "50113",
]

WAREHOUSE_NAMES = {
    "1": "Mobile",
    "2": "Milton",
    "5": "Jackson",
    "6": "Gulfport",
    "7": "Montgomery",
    "9": "Birmingham",
    "10": "Huntsville",
}

DOW_NAMES = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"}
MONTH_NAMES = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec",
}

# Inventory levels for DOH calculator
DOH_LEVELS = [500, 1000, 2500, 5000, 10000]

# History start date
HISTORY_START = 20240101


# ---------------------------------------------------------------------------
# Step 1: Query DAILYT
# ---------------------------------------------------------------------------
def query_dailyt():
    """Pull daily sales totals per item x warehouse from DAILYT."""
    print("Step 1: Querying DAILYT for 10 demo items (2024-01-01 to present)...")
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    sql = """
    SELECT TRIM("DAITEM") AS item_code,
           TRIM("DAWHSE") AS warehouse,
           "DAIDAT" AS invoice_date,
           SUM("DAQTY") AS total_cases,
           SUM("DAUNIT") AS total_units
    FROM staging."DAILYT"
    WHERE "DATYPE" = '1'
      AND "DAIDAT" >= %s
      AND TRIM("DAITEM") = ANY(%s)
    GROUP BY TRIM("DAITEM"), TRIM("DAWHSE"), "DAIDAT"
    ORDER BY 1, 2, 3
    """

    cur.execute(sql, (HISTORY_START, DEMO_ITEMS))
    rows = cur.fetchall()
    print(f"  Retrieved {len(rows):,} daily sales records")

    conn.close()

    df = pd.DataFrame(rows, columns=["item_code", "warehouse", "invoice_date", "cases", "units"])
    # Convert Decimal to native Python types
    df["cases"] = df["cases"].astype(float)
    df["units"] = df["units"].astype(float)
    df["invoice_date"] = df["invoice_date"].astype(int)
    # Parse YYYYMMDD integer to date
    df["date"] = pd.to_datetime(df["invoice_date"].astype(str), format="%Y%m%d")
    df["dow"] = df["date"].dt.dayofweek  # 0=Mon, 6=Sun
    df["month"] = df["date"].dt.month
    df["year"] = df["date"].dt.year
    df["is_weekday"] = df["dow"] < 5

    return df


# ---------------------------------------------------------------------------
# Step 2: Query item descriptions
# ---------------------------------------------------------------------------
def query_item_descriptions():
    """Get package descriptions for the 10 demo items."""
    print("Step 2: Fetching item descriptions...")
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT TRIM("ITEM_CODE"), TRIM("PACKAGE_DESCRIPTION")
        FROM staging."ITEMT"
        WHERE TRIM("ITEM_CODE") = ANY(%s)
    """,
        (DEMO_ITEMS,),
    )
    rows = cur.fetchall()
    conn.close()
    return dict(rows)


# ---------------------------------------------------------------------------
# Step 3: Calculate velocity metrics
# ---------------------------------------------------------------------------
def calc_velocity_summary(df, item_descs):
    """Section A: Per item x warehouse velocity summary."""
    print("Step 3a: Calculating velocity summary...")

    # Filter to active warehouses only
    df_active = df[df["warehouse"].isin(WAREHOUSE_NAMES.keys())].copy()

    # Current month
    today = date.today()
    current_month = today.month
    current_year = today.year

    results = []
    for (item, wh), grp in df_active.groupby(["item_code", "warehouse"]):
        weekday_data = grp[grp["is_weekday"]]
        if weekday_data.empty:
            continue

        # Count unique weekdays in the data range
        unique_weekdays = weekday_data["date"].dt.date.nunique()
        total_cases = weekday_data["cases"].sum()

        avg_daily = total_cases / unique_weekdays if unique_weekdays > 0 else 0

        # Current month rate
        cur_month_data = weekday_data[(weekday_data["year"] == current_year) & (weekday_data["month"] == current_month)]
        cur_month_days = cur_month_data["date"].dt.date.nunique()
        cur_month_cases = cur_month_data["cases"].sum()
        cur_month_rate = cur_month_cases / cur_month_days if cur_month_days > 0 else 0

        # Seasonal index for current month (avg across years for this month / overall avg)
        month_data = weekday_data[weekday_data["month"] == current_month]
        month_days = month_data["date"].dt.date.nunique()
        month_avg = month_data["cases"].sum() / month_days if month_days > 0 else 0
        seasonal_idx = month_avg / avg_daily if avg_daily > 0 else 1.0

        # Cases needed for N-day supply (using current month rate)
        supply_3d = round(cur_month_rate * 3)
        supply_5d = round(cur_month_rate * 5)
        supply_7d = round(cur_month_rate * 7)

        results.append(
            {
                "item": item,
                "description": item_descs.get(item, ""),
                "warehouse": wh,
                "warehouse_name": WAREHOUSE_NAMES.get(wh, wh),
                "avg_daily_weekday": round(avg_daily, 1),
                "current_month_rate": round(cur_month_rate, 1),
                "seasonal_index": round(seasonal_idx, 2),
                "cases_3day": supply_3d,
                "cases_5day": supply_5d,
                "cases_7day": supply_7d,
            }
        )

    return sorted(results, key=lambda r: (r["item"], -r["avg_daily_weekday"]))


def calc_dow_pattern(df):
    """Section B: Day-of-week pattern per item x warehouse."""
    print("Step 3b: Calculating day-of-week patterns...")

    df_active = df[df["warehouse"].isin(WAREHOUSE_NAMES.keys())].copy()

    results = []
    for (item, wh), grp in df_active.groupby(["item_code", "warehouse"]):
        # Average cases per DOW
        dow_avg = {}
        for dow in range(7):
            dow_data = grp[grp["dow"] == dow]
            unique_days = dow_data["date"].dt.date.nunique()
            total = dow_data["cases"].sum()
            dow_avg[dow] = round(total / unique_days, 1) if unique_days > 0 else 0

        # Weekday average for factor calculation
        weekday_total = sum(dow_avg[d] for d in range(5))
        weekday_avg = weekday_total / 5 if weekday_total > 0 else 1

        results.append(
            {
                "item": item,
                "warehouse": wh,
                "warehouse_name": WAREHOUSE_NAMES.get(wh, wh),
                "mon_cases": dow_avg[0],
                "tue_cases": dow_avg[1],
                "wed_cases": dow_avg[2],
                "thu_cases": dow_avg[3],
                "fri_cases": dow_avg[4],
                "sat_cases": dow_avg[5],
                "sun_cases": dow_avg[6],
                "mon_factor": round(dow_avg[0] / weekday_avg, 2),
                "tue_factor": round(dow_avg[1] / weekday_avg, 2),
                "wed_factor": round(dow_avg[2] / weekday_avg, 2),
                "thu_factor": round(dow_avg[3] / weekday_avg, 2),
                "fri_factor": round(dow_avg[4] / weekday_avg, 2),
            }
        )

    return sorted(results, key=lambda r: (r["item"], r["warehouse"]))


def calc_seasonality(df):
    """Section C: Monthly seasonality index per item x warehouse."""
    print("Step 3c: Calculating monthly seasonality...")

    df_active = df[df["warehouse"].isin(WAREHOUSE_NAMES.keys()) & df["is_weekday"]].copy()

    results = []
    for (item, wh), grp in df_active.groupby(["item_code", "warehouse"]):
        # Overall avg daily rate
        total_days = grp["date"].dt.date.nunique()
        total_cases = grp["cases"].sum()
        overall_avg = total_cases / total_days if total_days > 0 else 1

        month_indices = {}
        for mo in range(1, 13):
            mo_data = grp[grp["month"] == mo]
            mo_days = mo_data["date"].dt.date.nunique()
            mo_total = mo_data["cases"].sum()
            mo_avg = mo_total / mo_days if mo_days > 0 else 0
            month_indices[mo] = round(mo_avg / overall_avg, 2) if overall_avg > 0 else 0

        results.append(
            {
                "item": item,
                "warehouse": wh,
                "warehouse_name": WAREHOUSE_NAMES.get(wh, wh),
                **{MONTH_NAMES[m]: month_indices[m] for m in range(1, 13)},
            }
        )

    return sorted(results, key=lambda r: (r["item"], r["warehouse"]))


def calc_doh_table(df):
    """Section D: Days on hand at different inventory levels.

    Uses forward-looking simulation: for each day starting from today,
    subtract the expected demand (base_rate * dow_factor * seasonal_factor)
    until inventory is depleted.
    """
    print("Step 3d: Calculating DOH at various inventory levels...")

    df_active = df[df["warehouse"].isin(WAREHOUSE_NAMES.keys()) & df["is_weekday"]].copy()
    today = date.today()

    results = []
    for (item, wh), grp in df_active.groupby(["item_code", "warehouse"]):
        total_days = grp["date"].dt.date.nunique()
        total_cases = grp["cases"].sum()
        base_rate = total_cases / total_days if total_days > 0 else 0

        if base_rate == 0:
            results.append(
                {
                    "item": item,
                    "warehouse": wh,
                    "warehouse_name": WAREHOUSE_NAMES.get(wh, wh),
                    **{f"{lvl}_cases": "N/A" for lvl in DOH_LEVELS},
                }
            )
            continue

        # Build DOW factors
        dow_factors = {}
        for dow in range(7):
            dow_data = (
                grp[grp["date"].dt.dayofweek == dow]
                if dow < 5
                else df[(df["item_code"] == item) & (df["warehouse"] == wh) & (df["dow"] == dow)]
            )
            dow_days = dow_data["date"].dt.date.nunique() if not dow_data.empty else 0
            dow_total = dow_data["cases"].sum() if not dow_data.empty else 0
            dow_avg = dow_total / dow_days if dow_days > 0 else 0
            weekday_avg = base_rate
            dow_factors[dow] = dow_avg / weekday_avg if weekday_avg > 0 else 0

        # Weekends: use actual weekend fraction (typically near 0)
        for dow in [5, 6]:
            all_dow = df[(df["item_code"] == item) & (df["warehouse"] == wh) & (df["dow"] == dow)]
            dow_days = all_dow["date"].dt.date.nunique()
            dow_total = all_dow["cases"].sum()
            dow_avg = dow_total / dow_days if dow_days > 0 else 0
            dow_factors[dow] = dow_avg / base_rate if base_rate > 0 else 0

        # Monthly seasonal factors
        seasonal_factors = {}
        for mo in range(1, 13):
            mo_data = grp[grp["date"].dt.month == mo]
            mo_days = mo_data["date"].dt.date.nunique()
            mo_total = mo_data["cases"].sum()
            mo_avg = mo_total / mo_days if mo_days > 0 else 0
            seasonal_factors[mo] = mo_avg / base_rate if base_rate > 0 else 1.0

        # Simulate forward depletion for each inventory level
        doh_values = {}
        for level in DOH_LEVELS:
            inventory = level
            day = today
            day_count = 0
            max_days = 365  # safety cap

            while inventory > 0 and day_count < max_days:
                dow = day.weekday()  # 0=Mon
                mo = day.month
                demand = base_rate * dow_factors.get(dow, 0) * seasonal_factors.get(mo, 1.0)
                inventory -= demand
                day_count += 1
                day += timedelta(days=1)

            doh_values[f"{level}_cases"] = round(day_count, 1)

        results.append(
            {
                "item": item,
                "warehouse": wh,
                "warehouse_name": WAREHOUSE_NAMES.get(wh, wh),
                **doh_values,
            }
        )

    return sorted(results, key=lambda r: (r["item"], r["warehouse"]))


# ---------------------------------------------------------------------------
# Step 4: Write to Google Sheets
# ---------------------------------------------------------------------------
def get_sheets_client():
    """Authenticate and return gspread client."""
    sa_paths = [SERVICE_ACCOUNT_PATH, Path(__file__).parent / "service-account.json"]
    sa_path = None
    for p in sa_paths:
        if p.exists():
            sa_path = p
            break
    if not sa_path:
        raise FileNotFoundError(f"Service account not found: {[str(p) for p in sa_paths]}")

    print(f"  Using service account: {sa_path}")
    creds = Credentials.from_service_account_file(str(sa_path), scopes=SCOPES)
    return gspread.authorize(creds)


def write_section(ws, start_row, title, headers, data_rows, retries=3):
    """Write a titled section (title row + headers + data) to a worksheet.

    Returns the next available row after this section.
    """
    # Title row
    ws.update(range_name=f"A{start_row}", values=[[title]])
    # Bold title would need formatting API — skip for now

    # Headers
    header_row = start_row + 1
    ws.update(range_name=f"A{header_row}", values=[headers])

    # Data in batches
    batch_size = 500
    for i in range(0, len(data_rows), batch_size):
        batch = data_rows[i : i + batch_size]
        data_start = header_row + 1 + i
        for attempt in range(retries):
            try:
                ws.update(range_name=f"A{data_start}", values=batch)
                break
            except gspread.exceptions.APIError as e:
                if "RATE_LIMIT" in str(e) or "429" in str(e):
                    wait = (attempt + 1) * 30
                    print(f"    Rate limited, waiting {wait}s...")
                    time.sleep(wait)
                else:
                    raise
        if i + batch_size < len(data_rows):
            time.sleep(1)

    # Return next row (with a blank line gap)
    return header_row + 1 + len(data_rows) + 2


def write_to_sheets(velocity_summary, dow_pattern, seasonality, doh_table, item_descs):
    """Write all sections to a Velocity_Analysis tab."""
    print("\nStep 4: Writing to Google Sheets...")

    gc = get_sheets_client()
    spreadsheet = gc.open_by_key(SHEET_ID)

    tab_name = "Velocity_Analysis"
    try:
        ws = spreadsheet.worksheet(tab_name)
        ws.clear()
    except gspread.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(title=tab_name, rows=1000, cols=20)

    # Resize generously
    total_data_rows = len(velocity_summary) + len(dow_pattern) + len(seasonality) + len(doh_table)
    ws.resize(rows=max(total_data_rows + 50, 500), cols=20)

    row = 1

    # --- Section A: Velocity Summary ---
    headers_a = [
        "Item",
        "Description",
        "Warehouse",
        "WH Name",
        "Avg Cases/Day (Weekday)",
        "Current Month Rate",
        "Seasonal Index",
        "Cases for 3-Day",
        "Cases for 5-Day",
        "Cases for 7-Day",
    ]
    data_a = [
        [
            r["item"],
            r["description"],
            r["warehouse"],
            r["warehouse_name"],
            r["avg_daily_weekday"],
            r["current_month_rate"],
            r["seasonal_index"],
            r["cases_3day"],
            r["cases_5day"],
            r["cases_7day"],
        ]
        for r in velocity_summary
    ]
    print(f"  Section A: Velocity Summary ({len(data_a)} rows)")
    row = write_section(ws, row, "VELOCITY SUMMARY (Weekday Avg, All History)", headers_a, data_a)
    time.sleep(2)

    # --- Section B: Day-of-Week Pattern ---
    headers_b = [
        "Item",
        "Warehouse",
        "WH Name",
        "Mon Cases",
        "Tue Cases",
        "Wed Cases",
        "Thu Cases",
        "Fri Cases",
        "Sat Cases",
        "Sun Cases",
        "Mon Factor",
        "Tue Factor",
        "Wed Factor",
        "Thu Factor",
        "Fri Factor",
    ]
    data_b = [
        [
            r["item"],
            r["warehouse"],
            r["warehouse_name"],
            r["mon_cases"],
            r["tue_cases"],
            r["wed_cases"],
            r["thu_cases"],
            r["fri_cases"],
            r["sat_cases"],
            r["sun_cases"],
            r["mon_factor"],
            r["tue_factor"],
            r["wed_factor"],
            r["thu_factor"],
            r["fri_factor"],
        ]
        for r in dow_pattern
    ]
    print(f"  Section B: Day-of-Week Pattern ({len(data_b)} rows)")
    row = write_section(ws, row, "DAY-OF-WEEK PATTERN (Avg Cases per Day & Factor vs Weekday Avg)", headers_b, data_b)
    time.sleep(2)

    # --- Section C: Monthly Seasonality ---
    headers_c = [
        "Item",
        "Warehouse",
        "WH Name",
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]
    data_c = [
        [
            r["item"],
            r["warehouse"],
            r["warehouse_name"],
            r["Jan"],
            r["Feb"],
            r["Mar"],
            r["Apr"],
            r["May"],
            r["Jun"],
            r["Jul"],
            r["Aug"],
            r["Sep"],
            r["Oct"],
            r["Nov"],
            r["Dec"],
        ]
        for r in seasonality
    ]
    print(f"  Section C: Monthly Seasonality ({len(data_c)} rows)")
    row = write_section(ws, row, "MONTHLY SEASONALITY INDEX (1.0 = Average, >1 = Above Avg)", headers_c, data_c)
    time.sleep(2)

    # --- Section D: DOH Calculator ---
    headers_d = [
        "Item",
        "Warehouse",
        "WH Name",
    ] + [f"{lvl} Cases (Days)" for lvl in DOH_LEVELS]
    data_d = [
        [r["item"], r["warehouse"], r["warehouse_name"]] + [r[f"{lvl}_cases"] for lvl in DOH_LEVELS] for r in doh_table
    ]
    print(f"  Section D: DOH Calculator ({len(data_d)} rows)")
    row = write_section(
        ws, row, "DAYS ON HAND AT INVENTORY LEVELS (Forward Simulation, DOW + Seasonal Adjusted)", headers_d, data_d
    )

    sheet_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}"
    print(f"\n  Done! Sheet URL: {sheet_url}")
    print(f"  Tab: {tab_name}")
    return sheet_url


# ---------------------------------------------------------------------------
# Step 5: 3-Day Movement Forecast tab
# ---------------------------------------------------------------------------
def calc_3day_forecast(df, item_descs):
    """Calculate expected movement for the next 3 days per item x warehouse.

    Uses today's date to determine the actual upcoming days, applies DOW
    and seasonal factors for an accurate forecast.
    """
    print("Step 5: Calculating 3-day movement forecast...")

    df_active = df[df["warehouse"].isin(WAREHOUSE_NAMES.keys()) & df["is_weekday"]].copy()
    today = date.today()

    results = []
    for (item, wh), grp in df_active.groupby(["item_code", "warehouse"]):
        total_days = grp["date"].dt.date.nunique()
        total_cases = grp["cases"].sum()
        base_rate = total_cases / total_days if total_days > 0 else 0

        if base_rate == 0:
            continue

        # DOW factors (0=Mon..6=Sun)
        dow_factors = {}
        for dow in range(5):
            dow_data = grp[grp["date"].dt.dayofweek == dow]
            dow_days = dow_data["date"].dt.date.nunique()
            dow_total = dow_data["cases"].sum()
            dow_avg = dow_total / dow_days if dow_days > 0 else 0
            dow_factors[dow] = dow_avg / base_rate if base_rate > 0 else 0

        # Weekend factors from full dataset
        for dow in [5, 6]:
            all_dow = df[(df["item_code"] == item) & (df["warehouse"] == wh) & (df["dow"] == dow)]
            dow_days = all_dow["date"].dt.date.nunique()
            dow_total = all_dow["cases"].sum()
            dow_avg = dow_total / dow_days if dow_days > 0 else 0
            dow_factors[dow] = dow_avg / base_rate if base_rate > 0 else 0

        # Monthly seasonal factors
        seasonal_factors = {}
        for mo in range(1, 13):
            mo_data = grp[grp["date"].dt.month == mo]
            mo_days = mo_data["date"].dt.date.nunique()
            mo_total = mo_data["cases"].sum()
            mo_avg = mo_total / mo_days if mo_days > 0 else 0
            seasonal_factors[mo] = mo_avg / base_rate if base_rate > 0 else 1.0

        # Forecast next 3 days
        day_forecasts = []
        for offset in range(3):
            d = today + timedelta(days=offset)
            dow = d.weekday()
            mo = d.month
            demand = base_rate * dow_factors.get(dow, 0) * seasonal_factors.get(mo, 1.0)
            day_forecasts.append(
                {
                    "date": d,
                    "day_name": d.strftime("%a"),
                    "demand": round(demand),
                }
            )

        total_3day = sum(f["demand"] for f in day_forecasts)

        # Also compute what 3 days looks like starting from each DOW (for comparison)
        dow_scenarios = {}
        for start_dow_name, start_dow in [("Mon", 0), ("Wed", 2), ("Fri", 4)]:
            scenario_total = 0
            for offset in range(3):
                d_dow = (start_dow + offset) % 7
                # Use current month's seasonal factor
                demand = base_rate * dow_factors.get(d_dow, 0) * seasonal_factors.get(today.month, 1.0)
                scenario_total += demand
            dow_scenarios[start_dow_name] = round(scenario_total)

        results.append(
            {
                "item": item,
                "description": item_descs.get(item, ""),
                "warehouse": wh,
                "warehouse_name": WAREHOUSE_NAMES.get(wh, wh),
                "day1_label": f"{day_forecasts[0]['day_name']} {day_forecasts[0]['date'].strftime('%m/%d')}",
                "day1_cases": day_forecasts[0]["demand"],
                "day2_label": f"{day_forecasts[1]['day_name']} {day_forecasts[1]['date'].strftime('%m/%d')}",
                "day2_cases": day_forecasts[1]["demand"],
                "day3_label": f"{day_forecasts[2]['day_name']} {day_forecasts[2]['date'].strftime('%m/%d')}",
                "day3_cases": day_forecasts[2]["demand"],
                "total_3day": total_3day,
                "if_mon_start": dow_scenarios["Mon"],
                "if_wed_start": dow_scenarios["Wed"],
                "if_fri_start": dow_scenarios["Fri"],
            }
        )

    return sorted(results, key=lambda r: (r["item"], -r["total_3day"]))


def write_forecast_tab(forecast, item_descs):
    """Write the 3-Day Forecast to its own tab."""
    print("\nStep 6: Writing 3-Day Forecast to Google Sheets...")

    gc = get_sheets_client()
    spreadsheet = gc.open_by_key(SHEET_ID)

    tab_name = "3_Day_Forecast"
    try:
        ws = spreadsheet.worksheet(tab_name)
        ws.clear()
    except gspread.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(title=tab_name, rows=200, cols=20)

    ws.resize(rows=max(len(forecast) + 30, 100), cols=16)

    today = date.today()
    day_labels = [(today + timedelta(days=i)).strftime("%a %m/%d") for i in range(3)]

    row = 1

    # Title
    ws.update(
        range_name="A1",
        values=[
            [f"3-DAY MOVEMENT FORECAST — Starting {today.strftime('%A %B %d, %Y')}"],
        ],
    )
    ws.update(
        range_name="A2",
        values=[
            ["How many cases will move out in the next 3 days, adjusted for day-of-week patterns and seasonal demand."],
        ],
    )
    row = 4

    # Main forecast table
    headers = [
        "Item",
        "Description",
        "Warehouse",
        "WH Name",
        f"{day_labels[0]}",
        f"{day_labels[1]}",
        f"{day_labels[2]}",
        "3-Day Total",
    ]
    data = [
        [
            r["item"],
            r["description"],
            r["warehouse"],
            r["warehouse_name"],
            r["day1_cases"],
            r["day2_cases"],
            r["day3_cases"],
            r["total_3day"],
        ]
        for r in forecast
    ]
    print(f"  Main forecast: {len(data)} rows")
    row = write_section(ws, row, "FORECAST: Next 3 Days", headers, data)
    time.sleep(2)

    # Comparison: what if you started on a different day?
    headers_cmp = [
        "Item",
        "Description",
        "Warehouse",
        "WH Name",
        "3-Day if Mon Start",
        "3-Day if Wed Start",
        "3-Day if Fri Start",
        "Fri-to-Mon Difference",
    ]
    data_cmp = [
        [
            r["item"],
            r["description"],
            r["warehouse"],
            r["warehouse_name"],
            r["if_mon_start"],
            r["if_wed_start"],
            r["if_fri_start"],
            r["if_fri_start"] - r["if_mon_start"],
        ]
        for r in forecast
    ]
    print(f"  DOW comparison: {len(data_cmp)} rows")
    row = write_section(
        ws,
        row,
        "COMPARISON: 3-Day Movement by Starting Day (same month, different DOW)",
        headers_cmp,
        data_cmp,
    )

    sheet_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}"
    print(f"\n  Done! Tab: {tab_name}")
    print(f"  Sheet URL: {sheet_url}")


# ---------------------------------------------------------------------------
# Step 7: Interactive Calculator tab (formulas + dropdowns)
# ---------------------------------------------------------------------------
def build_calculator_reference_data(df, item_descs):
    """Build the reference table that Sheet formulas will look up against.

    Returns list of dicts with: key, item, desc, warehouse, wh_name,
    base_rate, dow_factors (Mon-Sun), seasonal_indices (Jan-Dec).
    """
    df_active = df[df["warehouse"].isin(WAREHOUSE_NAMES.keys()) & df["is_weekday"]].copy()

    ref_rows = []
    for (item, wh), grp in df_active.groupby(["item_code", "warehouse"]):
        total_days = grp["date"].dt.date.nunique()
        total_cases = grp["cases"].sum()
        base_rate = total_cases / total_days if total_days > 0 else 0
        if base_rate == 0:
            continue

        # DOW factors
        dow_f = {}
        for dow in range(5):
            d = grp[grp["date"].dt.dayofweek == dow]
            dd = d["date"].dt.date.nunique()
            dt = d["cases"].sum()
            avg = dt / dd if dd > 0 else 0
            dow_f[dow] = round(avg / base_rate, 4) if base_rate > 0 else 0
        for dow in [5, 6]:
            all_dow = df[(df["item_code"] == item) & (df["warehouse"] == wh) & (df["dow"] == dow)]
            dd = all_dow["date"].dt.date.nunique()
            dt = all_dow["cases"].sum()
            avg = dt / dd if dd > 0 else 0
            dow_f[dow] = round(avg / base_rate, 4) if base_rate > 0 else 0

        # Seasonal factors
        seas = {}
        for mo in range(1, 13):
            md = grp[grp["date"].dt.month == mo]
            mdd = md["date"].dt.date.nunique()
            mt = md["cases"].sum()
            mavg = mt / mdd if mdd > 0 else 0
            seas[mo] = round(mavg / base_rate, 4) if base_rate > 0 else 1.0

        ref_rows.append(
            {
                "key": f"{item}|{wh}",
                "item": item,
                "desc": item_descs.get(item, ""),
                "warehouse": wh,
                "wh_name": WAREHOUSE_NAMES.get(wh, wh),
                "base_rate": round(base_rate, 2),
                "mon_f": dow_f[0],
                "tue_f": dow_f[1],
                "wed_f": dow_f[2],
                "thu_f": dow_f[3],
                "fri_f": dow_f[4],
                "sat_f": dow_f[5],
                "sun_f": dow_f[6],
                "jan": seas[1],
                "feb": seas[2],
                "mar": seas[3],
                "apr": seas[4],
                "may": seas[5],
                "jun": seas[6],
                "jul": seas[7],
                "aug": seas[8],
                "sep": seas[9],
                "oct": seas[10],
                "nov": seas[11],
                "dec": seas[12],
            }
        )

    return sorted(ref_rows, key=lambda r: (r["item"], r["warehouse"]))


def write_calculator_tab(ref_data, item_descs):
    """Create the interactive calculator tab with dropdowns and live formulas."""
    print("\nStep 7: Building interactive calculator tab...")

    gc = get_sheets_client()
    spreadsheet = gc.open_by_key(SHEET_ID)

    tab_name = "3_Day_Calculator"
    try:
        ws = spreadsheet.worksheet(tab_name)
        ws.clear()
    except gspread.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(title=tab_name, rows=200, cols=30)

    ws.resize(rows=max(len(ref_data) + 30, 100), cols=26)

    # --- Build item and warehouse dropdown lists ---
    items_list = sorted(set(r["item"] for r in ref_data))
    [f"{code} - {item_descs.get(code, '')[:40]}" for code in items_list]
    wh_list = sorted(set(r["warehouse"] for r in ref_data))
    [f"{code} - {WAREHOUSE_NAMES.get(code, code)}" for code in wh_list]

    # --- Write dropdown source lists (columns T-U, hidden area) ---
    # Items in T2:T{n}, Warehouses in U2:U{n}
    item_dropdown_data = [[code] for code in items_list]
    wh_dropdown_data = [[code] for code in wh_list]
    # Item labels for display in V
    [[code, item_descs.get(code, "")] for code in items_list]
    # WH labels for display in W
    [[code, WAREHOUSE_NAMES.get(code, code)] for code in wh_list]

    ws.update(range_name="T1", values=[["Items"]])
    ws.update(range_name="T2", values=item_dropdown_data)
    ws.update(range_name="U1", values=[["Item Desc"]])
    ws.update(range_name="U2", values=[[item_descs.get(c, "")] for c in items_list])
    ws.update(range_name="V1", values=[["Warehouses"]])
    ws.update(range_name="V2", values=wh_dropdown_data)
    ws.update(range_name="W1", values=[["WH Name"]])
    ws.update(range_name="W2", values=[[WAREHOUSE_NAMES.get(c, c)] for c in wh_list])
    time.sleep(1)

    # --- Write reference data table starting at row 20 ---
    ref_headers = [
        "Key",
        "Item",
        "Description",
        "Warehouse",
        "WH Name",
        "Base Rate",
        "Mon",
        "Tue",
        "Wed",
        "Thu",
        "Fri",
        "Sat",
        "Sun",
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]
    ref_rows_data = [
        [
            r["key"],
            r["item"],
            r["desc"],
            r["warehouse"],
            r["wh_name"],
            r["base_rate"],
            r["mon_f"],
            r["tue_f"],
            r["wed_f"],
            r["thu_f"],
            r["fri_f"],
            r["sat_f"],
            r["sun_f"],
            r["jan"],
            r["feb"],
            r["mar"],
            r["apr"],
            r["may"],
            r["jun"],
            r["jul"],
            r["aug"],
            r["sep"],
            r["oct"],
            r["nov"],
            r["dec"],
        ]
        for r in ref_data
    ]

    ws.update(range_name="A19", values=[["REFERENCE DATA (used by calculator formulas)"]])
    ws.update(range_name="A20", values=[ref_headers])
    ws.update(range_name="A21", values=ref_rows_data)
    time.sleep(2)

    last_ref_row = 20 + len(ref_rows_data)
    last_item_row = 1 + len(items_list)
    last_wh_row = 1 + len(wh_list)

    # --- Write Calculator UI ---
    today_str = date.today().strftime("%m/%d/%Y")

    ws.update(
        range_name="A1",
        values=[
            ["3-DAY MOVEMENT CALCULATOR"],
        ],
    )
    ws.update(range_name="A3", values=[["Select Date:", today_str]])
    ws.update(range_name="A4", values=[["Select Product:"]])
    ws.update(range_name="B4", values=[["=T2"]], raw=False)
    ws.update(range_name="A5", values=[["Select Warehouse:"]])
    ws.update(range_name="B5", values=[["=V2"]], raw=False)

    # --- Exclude-days checkboxes (E2:L3) ---
    ws.update(range_name="E2", values=[["EXCLUDE DAYS"]])
    ws.update(range_name="F2:L2", values=[["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]])
    ws.update(range_name="F3:L3", values=[[False, False, False, False, False, True, True]])
    ws.update(range_name="E3", values=[["(check = skip)"]])

    # Product description auto-lookup
    ws.update(range_name="C4", values=[[f'=IFERROR(VLOOKUP(B4,T2:U{last_item_row},2,FALSE),"")']], raw=False)
    # Warehouse name auto-lookup
    ws.update(range_name="C5", values=[[f'=IFERROR(VLOOKUP(B5,V2:W{last_wh_row},2,FALSE),"")']], raw=False)
    time.sleep(1)

    # --- Output section ---
    ws.update(range_name="A7", values=[["3-DAY FORECAST"]])
    ws.update(range_name="A8", values=[["", "Date", "Day", "Expected Cases"]])

    # The lookup key formula
    # key = B4 & "|" & B5
    key_formula = 'B4&"|"&B5'
    match_formula = f"MATCH({key_formula},$A$21:$A${last_ref_row},0)"

    # --- Date formulas that skip excluded days using WORKDAY.INTL ---
    # Checkboxes F3:L3 (Mon-Sun) build a 7-char weekend string for WORKDAY.INTL
    # "1" = non-working day, "0" = working day, starting from Monday
    wkend = "$F$3*1&$G$3*1&$H$3*1&$I$3*1&$J$3*1&$K$3*1&$L$3*1"

    # Demand = base_rate * dow_factor * seasonal_factor
    # DOW factor column: WEEKDAY(date,2) gives 1=Mon..7=Sun, factors are in cols G-M (7-13)
    # Within the ref row A21:Z{last}, base_rate=col6, Mon=col7, so dow col = 6 + WEEKDAY(date,2)
    # Seasonal: Jan=col14, so month col = 13 + MONTH(date)
    def make_demand_formula(cell_ref):
        return (
            f"=IFERROR(ROUND("
            f"INDEX($A$21:$Z${last_ref_row},{match_formula},6)"  # base_rate
            f"*INDEX($A$21:$Z${last_ref_row},{match_formula},6+WEEKDAY({cell_ref},2))"  # dow_factor
            f"*INDEX($A$21:$Z${last_ref_row},{match_formula},13+MONTH({cell_ref}))"  # seasonal
            f"),0)"
        )

    # Day 1: first valid day on or after B3 (use B3-1 so WORKDAY.INTL includes B3 itself)
    ws.update(range_name="A9", values=[["Day 1"]])
    ws.update(range_name="B9", values=[[f'=IFERROR(WORKDAY.INTL($B$3-1,1,{wkend}),"")']], raw=False)
    ws.update(range_name="C9", values=[['=TEXT(B9,"ddd")']], raw=False)
    ws.update(range_name="D9", values=[[make_demand_formula("B9")]], raw=False)

    # Day 2: next valid day after Day 1
    ws.update(range_name="A10", values=[["Day 2"]])
    ws.update(range_name="B10", values=[[f'=IFERROR(WORKDAY.INTL(B9,1,{wkend}),"")']], raw=False)
    ws.update(range_name="C10", values=[['=TEXT(B10,"ddd")']], raw=False)
    ws.update(range_name="D10", values=[[make_demand_formula("B10")]], raw=False)

    # Day 3: next valid day after Day 2
    ws.update(range_name="A11", values=[["Day 3"]])
    ws.update(range_name="B11", values=[[f'=IFERROR(WORKDAY.INTL(B10,1,{wkend}),"")']], raw=False)
    ws.update(range_name="C11", values=[['=TEXT(B11,"ddd")']], raw=False)
    ws.update(range_name="D11", values=[[make_demand_formula("B11")]], raw=False)

    # Total
    ws.update(range_name="A12", values=[["TOTAL"]])
    ws.update(range_name="D12", values=[["=SUM(D9:D11)"]], raw=False)
    time.sleep(1)

    # --- Extra info ---
    ws.update(
        range_name="A14",
        values=[
            [
                "Base Daily Rate (weekday avg):",
                f'=IFERROR(INDEX($A$21:$Z${last_ref_row},{match_formula},6),"Select valid combo")',
            ],
        ],
        raw=False,
    )
    ws.update(
        range_name="A15",
        values=[
            [
                "Seasonal Index (this month):",
                f'=IFERROR(INDEX($A$21:$Z${last_ref_row},{match_formula},13+MONTH(B3)),"")',
            ],
        ],
        raw=False,
    )
    ws.update(
        range_name="A16",
        values=[
            ["DOW Factor (Day 1):", f'=IFERROR(INDEX($A$21:$Z${last_ref_row},{match_formula},6+WEEKDAY(B9,2)),"")'],
        ],
        raw=False,
    )
    time.sleep(1)

    # --- Data validation (dropdowns) ---
    print("  Setting up dropdowns...")
    item_range = f"'{tab_name}'!T2:T{last_item_row}"
    wh_range = f"'{tab_name}'!V2:V{last_wh_row}"

    body = {
        "requests": [
            # Product dropdown on B4 — references column T
            {
                "setDataValidation": {
                    "range": {
                        "sheetId": ws.id,
                        "startRowIndex": 3,
                        "endRowIndex": 4,
                        "startColumnIndex": 1,
                        "endColumnIndex": 2,
                    },
                    "rule": {
                        "condition": {
                            "type": "ONE_OF_RANGE",
                            "values": [{"userEnteredValue": f"={item_range}"}],
                        },
                        "showCustomUi": True,
                        "strict": False,
                    },
                }
            },
            # Warehouse dropdown on B5 — references column V
            {
                "setDataValidation": {
                    "range": {
                        "sheetId": ws.id,
                        "startRowIndex": 4,
                        "endRowIndex": 5,
                        "startColumnIndex": 1,
                        "endColumnIndex": 2,
                    },
                    "rule": {
                        "condition": {
                            "type": "ONE_OF_RANGE",
                            "values": [{"userEnteredValue": f"={wh_range}"}],
                        },
                        "showCustomUi": True,
                        "strict": False,
                    },
                }
            },
            # Date validation on B3
            {
                "setDataValidation": {
                    "range": {
                        "sheetId": ws.id,
                        "startRowIndex": 2,
                        "endRowIndex": 3,
                        "startColumnIndex": 1,
                        "endColumnIndex": 2,
                    },
                    "rule": {
                        "condition": {
                            "type": "DATE_IS_VALID",
                        },
                        "showCustomUi": True,
                        "strict": True,
                    },
                }
            },
            # Checkbox validation on F3:L3 (exclude-days)
            {
                "setDataValidation": {
                    "range": {
                        "sheetId": ws.id,
                        "startRowIndex": 2,
                        "endRowIndex": 3,
                        "startColumnIndex": 5,  # col F
                        "endColumnIndex": 12,  # through col L
                    },
                    "rule": {
                        "condition": {"type": "BOOLEAN"},
                        "showCustomUi": True,
                        "strict": True,
                    },
                }
            },
            # Bold title
            {
                "repeatCell": {
                    "range": {
                        "sheetId": ws.id,
                        "startRowIndex": 0,
                        "endRowIndex": 1,
                        "startColumnIndex": 0,
                        "endColumnIndex": 4,
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "textFormat": {"bold": True, "fontSize": 14},
                        }
                    },
                    "fields": "userEnteredFormat.textFormat",
                }
            },
            # Bold section header
            {
                "repeatCell": {
                    "range": {
                        "sheetId": ws.id,
                        "startRowIndex": 6,
                        "endRowIndex": 7,
                        "startColumnIndex": 0,
                        "endColumnIndex": 4,
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "textFormat": {"bold": True, "fontSize": 12},
                        }
                    },
                    "fields": "userEnteredFormat.textFormat",
                }
            },
            # Bold labels col A
            {
                "repeatCell": {
                    "range": {
                        "sheetId": ws.id,
                        "startRowIndex": 2,
                        "endRowIndex": 6,
                        "startColumnIndex": 0,
                        "endColumnIndex": 1,
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "textFormat": {"bold": True},
                        }
                    },
                    "fields": "userEnteredFormat.textFormat",
                }
            },
            # Bold total row
            {
                "repeatCell": {
                    "range": {
                        "sheetId": ws.id,
                        "startRowIndex": 11,
                        "endRowIndex": 12,
                        "startColumnIndex": 0,
                        "endColumnIndex": 5,
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "textFormat": {"bold": True},
                        }
                    },
                    "fields": "userEnteredFormat.textFormat",
                }
            },
            # Column widths
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": ws.id,
                        "dimension": "COLUMNS",
                        "startIndex": 0,
                        "endIndex": 1,
                    },
                    "properties": {"pixelSize": 200},
                    "fields": "pixelSize",
                }
            },
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": ws.id,
                        "dimension": "COLUMNS",
                        "startIndex": 1,
                        "endIndex": 2,
                    },
                    "properties": {"pixelSize": 120},
                    "fields": "pixelSize",
                }
            },
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": ws.id,
                        "dimension": "COLUMNS",
                        "startIndex": 2,
                        "endIndex": 3,
                    },
                    "properties": {"pixelSize": 250},
                    "fields": "pixelSize",
                }
            },
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": ws.id,
                        "dimension": "COLUMNS",
                        "startIndex": 3,
                        "endIndex": 4,
                    },
                    "properties": {"pixelSize": 140},
                    "fields": "pixelSize",
                }
            },
            # --- Exclude-days formatting ---
            # Bold "EXCLUDE DAYS" label (E2)
            {
                "repeatCell": {
                    "range": {
                        "sheetId": ws.id,
                        "startRowIndex": 1,
                        "endRowIndex": 2,
                        "startColumnIndex": 4,  # col E
                        "endColumnIndex": 5,
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "textFormat": {"bold": True},
                        }
                    },
                    "fields": "userEnteredFormat.textFormat",
                }
            },
            # Bold + center day name headers (F2:L2)
            {
                "repeatCell": {
                    "range": {
                        "sheetId": ws.id,
                        "startRowIndex": 1,
                        "endRowIndex": 2,
                        "startColumnIndex": 5,  # col F
                        "endColumnIndex": 12,  # through col L
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "textFormat": {"bold": True},
                            "horizontalAlignment": "CENTER",
                        }
                    },
                    "fields": "userEnteredFormat.textFormat,userEnteredFormat.horizontalAlignment",
                }
            },
            # Center-align checkboxes (F3:L3)
            {
                "repeatCell": {
                    "range": {
                        "sheetId": ws.id,
                        "startRowIndex": 2,
                        "endRowIndex": 3,
                        "startColumnIndex": 5,
                        "endColumnIndex": 12,
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "horizontalAlignment": "CENTER",
                        }
                    },
                    "fields": "userEnteredFormat.horizontalAlignment",
                }
            },
            # Column E width (label)
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": ws.id,
                        "dimension": "COLUMNS",
                        "startIndex": 4,
                        "endIndex": 5,
                    },
                    "properties": {"pixelSize": 110},
                    "fields": "pixelSize",
                }
            },
            # Columns F-L width (day checkboxes)
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": ws.id,
                        "dimension": "COLUMNS",
                        "startIndex": 5,
                        "endIndex": 12,
                    },
                    "properties": {"pixelSize": 50},
                    "fields": "pixelSize",
                }
            },
        ]
    }
    spreadsheet.batch_update(body)

    sheet_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}"
    print("  Calculator tab ready!")
    print(f"  Sheet URL: {sheet_url}#gid={ws.id}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("Days on Hand / Sales Velocity Analysis")
    print("10 Demo Products x 7 Warehouses")
    print("=" * 60)

    # Step 1: Query DAILYT
    df = query_dailyt()

    # Step 2: Item descriptions
    item_descs = query_item_descriptions()

    # Step 3: Calculate metrics
    velocity_summary = calc_velocity_summary(df, item_descs)
    dow_pattern = calc_dow_pattern(df)
    seasonality = calc_seasonality(df)
    doh_table = calc_doh_table(df)

    # Step 4: Write to Sheets
    write_to_sheets(velocity_summary, dow_pattern, seasonality, doh_table, item_descs)

    # Step 5: Build interactive calculator
    ref_data = build_calculator_reference_data(df, item_descs)
    write_calculator_tab(ref_data, item_descs)

    print("\nDone!")


if __name__ == "__main__":
    main()
