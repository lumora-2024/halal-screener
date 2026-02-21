"""
╔══════════════════════════════════════════════════════════════════════════╗
║              🌙 HALAL STOCK SCREENER — Core Engine                    ║
║     AAOIFI Shariah-Compliant Equity Screening                         ║
╚══════════════════════════════════════════════════════════════════════════╝

Standard: AAOIFI (Accounting & Auditing Organization for Islamic Financial Institutions)

Three-Tier Rating System:
  ✅ COMPLIANT      — Passes all business activity + financial screens
  🟡 QUESTIONABLE   — Gray-area sector OR data insufficient for firm ruling
  ❌ NON-COMPLIANT  — Fails business activity or financial ratio screen

Two Screens (AAOIFI standard):
  Screen 1 — Business Activity:
    • Primary haram (auto-fail): alcohol, gambling, adult content, pork,
      conventional banking/insurance, weapons of mass destruction
    • Revenue from ALL impermissible activities < 5% of total revenue
    • Gray-area (questionable): advertising, media/entertainment, defence,
      supermarkets (sell alcohol/pork), hotels, diversified conglomerates

  Screen 2 — Financial Ratios:
    • Interest-bearing debt   / Market Cap  <  30%
    • Interest-bearing assets / Market Cap  <  30%  (cash + deposits)
    • Impermissible revenue   / Total revenue < 5%

  Purification:
    • Impermissible revenue / total revenue = % of returns to donate to charity

Dependencies:
    pip install yfinance pandas tabulate colorama openpyxl requests streamlit
"""

import yfinance as yf
import pandas as pd
import logging
import os
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
#  LOGGING
# ─────────────────────────────────────────────
os.makedirs("logs",    exist_ok=True)
os.makedirs("reports", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(
            f"logs/halal_screener_{datetime.now().strftime('%Y%m%d')}.log"
        ),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
#  SECTION 1: SCREENING CONFIGURATION
#  Standard: AAOIFI
# ═══════════════════════════════════════════════════════════════

# ── Thresholds (AAOIFI standard) ─────────────────────────────
THRESHOLDS = {
    # AAOIFI: debt-to-market cap ratio no higher than 30%
    # Based on hadith of Saad bin Abi Waqas: "one third, and one third is much"
    "max_debt_to_market_cap":        0.30,

    # AAOIFI: interest-bearing securities cannot exceed 30% of market cap
    # Formula: (Cash + Cash Equivalents + Deposits) / Market Cap
    "max_interest_bearing_securities": 0.30,

    # AAOIFI: revenue from non-permissible activities must be < 5%
    "max_haram_revenue_ratio":       0.05,
}

# ── Primary Haram Activities (auto-fail) ─────────────────────
# Both AAOIFI auto-fail companies with these as core activities.
PRIMARY_HARAM = {
    "Alcohol": [
        "alcohol", "beer", "wine", "spirits", "brewery", "distillery",
        "brewers", "winery", "malt beverage", "alcoholic drink"
    ],
    "Tobacco": [
        "tobacco", "cigarette", "cigars", "nicotine products"
    ],
    "Gambling": [
        "casino", "gambling", "lottery", "betting", "wagering",
        "sports betting", "horse racing", "gaming machines"
    ],
    "Adult Entertainment": [
        "adult entertainment", "pornography", "adult content", "erotic"
    ],
    "Pork Products": [
        "pork processing", "pig farming", "swine production", "ham producer"
    ],
    "Weapons of Mass Destruction": [
        "nuclear weapons", "biological weapons", "chemical weapons",
        "landmines", "cluster munitions", "cluster bombs"
    ],
    "Conventional Banking": [
        # Full-service conventional banks are non-compliant (interest-based)
        "commercial banking", "retail banking", "savings bank",
        "investment banking", "mortgage banking"
    ],
    "Interest-Based Lending": [
        "consumer finance", "payday loans", "pawnshops", "subprime lending",
        "loan shark"
    ],
    "Conventional Insurance": [
        # Conventional insurance involves gharar (uncertainty) — non-compliant
        "life insurance", "property insurance", "casualty insurance",
        "conventional insurance"
    ],
}

# ── Gray-Area Activities (Questionable — Questionable status) ──
# Companies in gray-area industries,
# (differing scholarly opinions)
GRAY_AREA = {
    "Advertising Platforms": [
        "digital advertising", "online advertising", "ad-supported",
        "advertising platform"
    ],
    "Media & Entertainment": [
        "music streaming", "video streaming", "entertainment content",
        "social media"
    ],
    "Diversified Retail": [
        # Supermarkets that sell alcohol/pork — questionable, not auto-fail
        "supermarket", "hypermarket", "grocery store", "wholesale club"
    ],
    "Conventional Fintech": [
        "digital payments", "credit card network", "buy now pay later",
        "payment processing"
    ],
    "Defense & Aerospace": [
        "defense", "aerospace", "military", "arms", "weapons", "ammunition",
        "firearms", "ordnance"
    ],
    "Hotels & Hospitality": [
        "hotel", "resort", "hospitality", "lodging", "accommodation"
    ],
    "Diversified Conglomerates": [
        "conglomerate", "diversified holdings"
    ],
}

# ── Sector-Level Flags ────────────────────────────────────────
# Sectors flagged for closer review
HARAM_SECTORS = [
    "Banks—Regional", "Banks—Diversified", "Banks—Global",
    "Insurance—Life", "Insurance—Diversified", "Insurance—Property & Casualty",
    "Gambling", "Beverages—Brewers", "Beverages—Wineries & Distilleries",
    "Tobacco",
]

QUESTIONABLE_SECTORS = [
    "Financial Services",           # May include interest products
    "Capital Markets",              # Investment banking activities
    "Asset Management",             # May manage non-compliant funds
    "Credit Services",              # Credit cards, BNPL
    "Entertainment",                # Music, streaming, gaming
    "Advertising Agencies",         # May promote haram products
    "Specialty Retail",             # Could sell prohibited items
    "Grocery Stores",               # Sell alcohol/pork
    "Department Stores",            # Sell alcohol/pork
    "Aerospace & Defense",          # Weapons manufacturing
    "Hotels & Motels",              # Serve alcohol
    "Resorts & Casinos",            # Gambling + alcohol
    "Broadcasting",                 # Entertainment content
]

# ── Default Watchlist ─────────────────────────────────────────
DEFAULT_TICKERS = [
    # Big Tech
    "AAPL", "MSFT", "GOOGL", "META", "AMZN", "NVDA", "TSLA",
    # Healthcare
    "JNJ", "PFE", "ABBV", "MRK", "UNH",
    # Consumer
    "MCD", "KO", "PEP", "PG", "WMT", "COST",
    # Islamic ETFs
    "SPUS", "HLAL",
    # Finance (likely to fail)
    "JPM", "BAC", "GS", "V", "MA",
]


# ═══════════════════════════════════════════════════════════════
#  SECTION 2: DATA FETCHING
# ═══════════════════════════════════════════════════════════════

def fetch_stock_data(ticker: str) -> dict:
    """
    Fetch financial data from Yahoo Finance.
    Returns all fields needed for AAOIFI screening.
    """
    try:
        stock = yf.Ticker(ticker)
        info  = stock.info

        name        = info.get("longName", ticker)
        sector      = info.get("sector", "N/A") or "N/A"
        industry    = info.get("industry", "N/A") or "N/A"
        description = (info.get("longBusinessSummary", "") or "").lower()
        country     = info.get("country", "N/A") or "N/A"
        market_cap  = info.get("marketCap")
        price       = info.get("currentPrice") or info.get("regularMarketPrice")

        # ── Balance Sheet ────────────────────────────────────
        # AAOIFI screens for interest-bearing debt.
        # yfinance "totalDebt" = long-term + short-term debt (good proxy)
        total_debt  = info.get("totalDebt", 0) or 0
        total_cash  = info.get("totalCash", 0) or 0  # cash + short-term investments

        # ── Income Statement ─────────────────────────────────
        total_revenue    = info.get("totalRevenue")
        # interestExpense is our best proxy for interest income from operations
        interest_expense = abs(info.get("interestExpense", 0) or 0)

        # ── Valuation ────────────────────────────────────────
        pe_ratio       = info.get("trailingPE")
        pb_ratio       = info.get("priceToBook")
        dividend_yield = info.get("dividendYield", 0) or 0
        eps            = info.get("trailingEps")
        roe            = info.get("returnOnEquity")

        return {
            "ticker":           ticker,
            "name":             name,
            "sector":           sector,
            "industry":         industry,
            "description":      description,
            "country":          country,
            "market_cap":       market_cap,
            "price":            price,
            "total_debt":       total_debt,
            "total_cash":       total_cash,
            "total_revenue":    total_revenue,
            "interest_expense": interest_expense,
            "pe_ratio":         pe_ratio,
            "pb_ratio":         pb_ratio,
            "dividend_yield":   dividend_yield,
            "eps":              eps,
            "roe":              roe,
        }

    except Exception as e:
        logger.warning(f"[{ticker}] Failed to fetch data: {e}")
        return {"ticker": ticker, "error": str(e)}


# ═══════════════════════════════════════════════════════════════
#  SECTION 3: BUSINESS ACTIVITY SCREEN
#  Methodology: AAOIFI (both AAOIFI)
# ═══════════════════════════════════════════════════════════════

def screen_business_activity(data: dict) -> dict:
    """
    Screen 1 — Business Activity (AAOIFI standard).

    - Primary haram core business → NON-COMPLIANT
    - Revenue from impermissible sources must be < 5% of total revenue
    - Gray-area industries → QUESTIONABLE (scholars differ on permissibility)
    """
    sector      = (data.get("sector",      "") or "").strip()
    industry    = (data.get("industry",    "") or "").strip()
    description = (data.get("description", "") or "").lower()

    combined = f"{sector} {industry} {description}".lower()

    # ── 1. Primary haram keyword check ───────────────────────
    primary_violations = []
    for category, keywords in PRIMARY_HARAM.items():
        for kw in keywords:
            if kw in combined:
                primary_violations.append(f"{category}")
                break

    if primary_violations:
        return {
            "verdict": "fail",
            "status":  "❌ NON-COMPLIANT",
            "reason":  f"Primary haram activity: {primary_violations[0]}",
            "detail":  (
                "Core business involves a prohibited activity under AAOIFI "
                "standards (AAOIFI). This activity is impermissible."
            )
        }

    # ── 2. Haram sector check ─────────────────────────────────
    for hs in HARAM_SECTORS:
        if hs.lower() in combined or sector == hs or industry == hs:
            return {
                "verdict": "fail",
                "status":  "❌ NON-COMPLIANT",
                "reason":  f"Haram sector: {hs}",
                "detail":  (
                    "Company operates in a sector classified as non-permissible "
                    "by AAOIFI standards. Flagged by AAOIFI."
                )
            }

    # ── 3. Gray-area keyword check (Questionable) ────────────
    gray_flags = []
    for category, keywords in GRAY_AREA.items():
        for kw in keywords:
            if kw in combined:
                gray_flags.append(category)
                break

    if not gray_flags:
        for qs in QUESTIONABLE_SECTORS:
            if qs.lower() in combined or sector == qs or industry == qs:
                gray_flags.append(qs)
                break

    if gray_flags:
        return {
            "verdict": "questionable",
            "status":  "🟡 QUESTIONABLE",
            "reason":  f"Gray-area industry: {gray_flags[0]}",
            "detail":  (
                f"Scholars differ on permissibility "
                f"for '{gray_flags[0]}'. Review the business model carefully before investing."
            )
        }

    # ── 4. Clean pass ─────────────────────────────────────────
    return {
        "verdict": "pass",
        "status":  "✅ PASS",
        "reason":  "No haram or gray-area business activity detected",
        "detail":  "Core business activity appears permissible under AAOIFI Shariah standards."
    }


# ═══════════════════════════════════════════════════════════════
#  SECTION 4: FINANCIAL RATIO SCREEN
#  AAOIFI Financial Ratio Screen
# ═══════════════════════════════════════════════════════════════

def screen_financial_ratios(data: dict) -> dict:
    """
    Screen 2 — Financial Ratios (AAOIFI standard).

    Ratio 1 — Interest-Bearing Debt:
        Total Debt / Market Cap  <  30%

    Ratio 2 — Interest-Bearing Securities:
        (Cash + Cash Equivalents + Deposits) / Market Cap  <  30%

    Ratio 3 — Impermissible Revenue:
        Haram Income / Total Revenue  <  5%

    Basis for 30%: Derived from the hadith of Saad Bin Abi Waqas where
    the Prophet ﷺ said "one third, and one third is much."
    """
    market_cap = data.get("market_cap")
    total_debt  = data.get("total_debt",  0) or 0
    total_cash  = data.get("total_cash",  0) or 0
    total_revenue    = data.get("total_revenue")    or 0
    interest_expense = data.get("interest_expense", 0) or 0

    ratios    = {}
    failures  = []
    warnings_ = []

    debt_limit = THRESHOLDS["max_debt_to_market_cap"]
    sec_limit  = THRESHOLDS["max_interest_bearing_securities"]

    # ── Ratio 1: Interest-bearing debt / Market Cap ───────────
    if market_cap and market_cap > 0:
        debt_ratio         = total_debt / market_cap
        ratios["debt_ratio"] = round(debt_ratio * 100, 2)

        if debt_ratio > debt_limit:
            failures.append(
                f"Debt/MktCap {debt_ratio:.1%} exceeds {debt_limit:.0%} limit"
            )
    else:
        ratios["debt_ratio"] = None
        warnings_.append("Market cap unavailable — debt ratio skipped")

    # ── Ratio 2: Interest-bearing securities / Market Cap ─────
    # AAOIFI formula: (Cash + Cash Equivalents + Deposits) / Market Cap
    if market_cap and market_cap > 0:
        sec_ratio             = total_cash / market_cap
        ratios["sec_ratio"]   = round(sec_ratio * 100, 2)

        if sec_ratio > sec_limit:
            failures.append(
                f"Interest-bearing securities {sec_ratio:.1%} exceeds {sec_limit:.0%} limit"
            )
    else:
        ratios["sec_ratio"] = None
        warnings_.append("Market cap unavailable — securities ratio skipped")

    # ── Ratio 3: Haram Revenue % (AAOIFI 5% rule) ──
    # We use interest_expense as proxy for impermissible income
    if total_revenue > 0 and interest_expense > 0:
        haram_rev_ratio           = interest_expense / total_revenue
        ratios["haram_rev_ratio"] = round(haram_rev_ratio * 100, 4)

        haram_limit = THRESHOLDS["max_haram_revenue_ratio"]
        if haram_rev_ratio > haram_limit:
            failures.append(
                f"Impermissible revenue {haram_rev_ratio:.1%} exceeds {haram_limit:.0%} limit"
            )
    else:
        ratios["haram_rev_ratio"] = 0.0

    # ── Final verdict ─────────────────────────────────────────
    if failures:
        return {
            "verdict":  "fail",
            "status":   "❌ FAIL",
            "reason":   failures[0],
            "ratios":   ratios,
            "warnings": warnings_
        }

    return {
        "verdict":  "pass",
        "status":   "✅ PASS",
        "reason":   "All financial ratios within AAOIFI limits",
        "ratios":   ratios,
        "warnings": warnings_
    }


# ═══════════════════════════════════════════════════════════════
#  SECTION 5: PURIFICATION CALCULATION
#  Both AAOIFI provide purification %
# ═══════════════════════════════════════════════════════════════

def calculate_purification(data: dict) -> dict:
    """
    Purification = Impermissible Income / Total Revenue × 100

    This is the percentage of any dividends or capital gains the investor
    should donate to charity to purify their returns from any residual
    impermissible income — in accordance with AAOIFI Shariah principles.
    """
    total_revenue    = data.get("total_revenue")    or 0
    interest_expense = data.get("interest_expense", 0) or 0
    dividend_yield   = data.get("dividend_yield",   0) or 0

    if total_revenue > 0 and interest_expense > 0:
        purification_pct = (interest_expense / total_revenue) * 100
    else:
        purification_pct = 0.0

    return {
        "purification_pct": round(purification_pct, 4),
        "explanation": (
            f"Donate {purification_pct:.3f}% of your returns from this stock "
            f"to charity to purify any residual impermissible income."
        ) if purification_pct > 0 else "No purification required."
    }


# ═══════════════════════════════════════════════════════════════
#  SECTION 6: MASTER SCREENING FUNCTION
# ═══════════════════════════════════════════════════════════════

def screen_stock(ticker: str) -> dict:
    """
    Full halal screening pipeline for a single ticker.

    Overall rating (AAOIFI 3-tier system):
      ✅ COMPLIANT      — Passes both screens
      🟡 QUESTIONABLE   — Gray-area business OR borderline financials
      ❌ NON-COMPLIANT  — Fails business activity or financial screen
    """
    logger.info(f"Screening {ticker}...")

    data = fetch_stock_data(ticker)
    if "error" in data:
        return {
            "ticker":    ticker,
            "name":      ticker,
            "overall":   "⚠️ ERROR",
            "error":     data["error"],
            "compliant": False
        }

    biz_result   = screen_business_activity(data)
    fin_result   = screen_financial_ratios(data)
    purification = calculate_purification(data)

    # ── Overall verdict ───────────────────────────────────────
    if biz_result["verdict"] == "fail" or fin_result["verdict"] == "fail":
        overall   = "❌ NON-COMPLIANT"
        compliant = False
    elif biz_result["verdict"] == "questionable":
        overall   = "🟡 QUESTIONABLE"
        compliant = None
    else:
        overall   = "✅ COMPLIANT"
        compliant = True

    # Format market cap
    mc = data.get("market_cap")
    if mc:
        if mc >= 1e12:  mc_str = f"${mc/1e12:.2f}T"
        elif mc >= 1e9: mc_str = f"${mc/1e9:.2f}B"
        else:           mc_str = f"${mc/1e6:.2f}M"
    else:
        mc_str = "N/A"

    ratios = fin_result.get("ratios", {})

    return {
        # Identity
        "ticker":             ticker,
        "name":               data.get("name", ticker),
        "sector":             data.get("sector", "N/A"),
        "industry":           data.get("industry", "N/A"),
        "country":            data.get("country", "N/A"),
        "market_cap":         mc_str,
        "price":              data.get("price"),
        "pe_ratio":           data.get("pe_ratio"),
        "dividend_yield":     round((data.get("dividend_yield") or 0) * 100, 2),

        # Verdicts
        "overall":            overall,
        "compliant":          compliant,

        # Business screen
        "biz_verdict":        biz_result["verdict"],
        "biz_status":         biz_result["status"],
        "biz_reason":         biz_result["reason"],
        "biz_detail":         biz_result.get("detail", ""),

        # Financial screen
        "fin_verdict":        fin_result["verdict"],
        "fin_status":         fin_result["status"],
        "fin_reason":         fin_result["reason"],

        # Ratios (all as % values)
        "debt_ratio_pct":     ratios.get("debt_ratio"),
        "sec_ratio_pct":      ratios.get("sec_ratio"),
        "haram_rev_pct":      ratios.get("haram_rev_ratio", 0),

        # Purification
        "purification_pct":   purification["purification_pct"],
        "purification_note":  purification["explanation"],

        # Metadata
        "methodology":        "AAOIFI Shariah Standard",
        "screened_at":        datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


def screen_portfolio(tickers: list) -> list:
    """Screen a list of tickers. Returns sorted results."""
    results = []
    for i, ticker in enumerate(tickers, 1):
        print(f"  [{i:>2}/{len(tickers)}] {ticker.upper():<8}", end="\r")
        results.append(screen_stock(ticker.upper().strip()))

    order = {
        "✅ COMPLIANT":    0,
        "🟡 QUESTIONABLE": 1,
        "❌ NON-COMPLIANT": 2,
        "⚠️ ERROR":        3
    }
    results.sort(key=lambda x: order.get(x.get("overall", ""), 99))
    return results


# ─────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="🌙 Halal Stock Screener")
    parser.add_argument("--tickers", nargs="+")
    args = parser.parse_args()

    tickers = args.tickers or DEFAULT_TICKERS
    results = screen_portfolio(tickers)

    for r in results:
        print(
            f"{r['overall']:<22} {r['ticker']:<7} "
            f"Debt:{r.get('debt_ratio_pct') or 'N/A':>6}% | "
            f"Sec:{r.get('sec_ratio_pct') or 'N/A':>6}% | "
            f"Purify:{r.get('purification_pct',0):.3f}%"
        )
