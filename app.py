"""
╔══════════════════════════════════════════════════════════════╗
║         🌙 HALAL STOCK SCREENER — Streamlit Web App        ║
║     Full-featured client-facing dashboard                  ║
╚══════════════════════════════════════════════════════════════╝

Run locally:     streamlit run app.py
Deploy:          Push to GitHub → share.streamlit.io
"""

import streamlit as st
import pandas as pd
import io
import json
from datetime import datetime

from halal_screener import (
    screen_stock,
    THRESHOLDS,
)

# ─────────────────────────────────────────────
#  PAGE CONFIG — Must be FIRST Streamlit call
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="🌙 Halal Stock Screener",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "🌙 Halal Stock Screener | AAOIFI Standards | Built with QuantGPT"
    }
)

# ─────────────────────────────────────────────
#  GLOBAL CSS  (theme + tiny utility classes)
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Crimson+Pro:wght@300;400&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --gold:      #C9A84C;
    --gold-dim:  #8B6914;
    --navy:      #0A0F1E;
    --navy-mid:  #111827;
    --navy-card: #161D2E;
    --navy-edge: #1E2D45;
    --text:      #F0EBE0;
    --dim:       #8B9BB4;
    --green:     #27A86E;
    --amber:     #D4A017;
    --red:       #E74C3C;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--navy) !important;
    color: var(--text) !important;
    font-family: 'Crimson Pro', Georgia, serif !important;
}
#MainMenu, footer { visibility: hidden; }

[data-testid="stSidebar"] {
    background: var(--navy-mid) !important;
    border-right: 1px solid var(--navy-edge) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

[data-testid="metric-container"] {
    background: var(--navy-card) !important;
    border: 1px solid var(--navy-edge) !important;
    border-radius: 12px !important;
    padding: 1rem !important;
}
[data-testid="stMetricValue"] {
    color: var(--gold) !important;
    font-family: 'Cinzel', serif !important;
}
[data-testid="stMetricLabel"] {
    color: var(--dim) !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    font-size: 0.75rem !important;
}

.stButton > button {
    background: linear-gradient(135deg, var(--gold-dim), var(--gold)) !important;
    color: var(--navy) !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Cinzel', serif !important;
    font-weight: 700 !important;
    letter-spacing: 0.06em !important;
    transition: all 0.25s ease !important;
    width: 100%;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(201,168,76,0.35) !important;
}

.stTextArea textarea {
    background: var(--navy-card) !important;
    border: 1px solid var(--navy-edge) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.9rem !important;
}

[data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--navy-edge) !important;
}
[data-baseweb="tab"] {
    background: transparent !important;
    color: var(--dim) !important;
    font-family: 'Cinzel', serif !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.08em !important;
}
[aria-selected="true"] {
    color: var(--gold) !important;
    border-bottom: 2px solid var(--gold) !important;
    background: transparent !important;
}

[data-testid="stExpander"] {
    background: var(--navy-card) !important;
    border: 1px solid var(--navy-edge) !important;
    border-radius: 12px !important;
    margin-bottom: 0.75rem !important;
}
details summary p {
    font-family: 'Cinzel', serif !important;
    font-size: 0.88rem !important;
    letter-spacing: 0.04em !important;
    color: var(--text) !important;
}

.stProgress > div > div > div {
    background: linear-gradient(90deg, var(--gold-dim), var(--gold)) !important;
}

[data-baseweb="select"] > div {
    background: var(--navy-card) !important;
    border-color: var(--navy-edge) !important;
    color: var(--text) !important;
}

hr { border-color: var(--navy-edge) !important; margin: 1.5rem 0 !important; }
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: var(--navy); }
::-webkit-scrollbar-thumb { background: var(--navy-edge); border-radius: 3px; }

/* Tiny reusable classes */
.sec-label {
    font-family: 'Cinzel', serif;
    font-size: 0.6rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: #8B6914;
    margin-bottom: 0.4rem;
}
.badge-pass   { display:inline-block; padding:3px 14px; border-radius:999px; font-family:'Cinzel',serif; font-size:0.72rem; font-weight:700; letter-spacing:0.08em; background:rgba(39,168,110,0.15); color:#27A86E; border:1px solid rgba(39,168,110,0.35); }
.badge-review { display:inline-block; padding:3px 14px; border-radius:999px; font-family:'Cinzel',serif; font-size:0.72rem; font-weight:700; letter-spacing:0.08em; background:rgba(212,160,23,0.15); color:#D4A017; border:1px solid rgba(212,160,23,0.35); }
.badge-fail   { display:inline-block; padding:3px 14px; border-radius:999px; font-family:'Cinzel',serif; font-size:0.72rem; font-weight:700; letter-spacing:0.08em; background:rgba(231,76,60,0.15);  color:#E74C3C; border:1px solid rgba(231,76,60,0.35); }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════

def badge_html(verdict: str) -> str:
    """Tiny HTML badge — safe for st.markdown as a one-liner."""
    if "HALAL" in verdict and "NOT" not in verdict:
        return f'<span class="badge-pass">{verdict}</span>'
    elif "REVIEW" in verdict:
        return f'<span class="badge-review">{verdict}</span>'
    else:
        return f'<span class="badge-fail">{verdict}</span>'


def fmt(value, suffix="%", decimals=1):
    if value is None:
        return "N/A"
    return f"{value:.{decimals}f}{suffix}"


# ═══════════════════════════════════════════════════════════════
#  RESULT CARD  — 100% native Streamlit components
# ═══════════════════════════════════════════════════════════════

def render_result_card(r: dict):
    """Render a single stock result using only native Streamlit widgets."""

    if r.get("overall") == "⚠️ ERROR":
        st.warning(f"⚠️ **{r['ticker']}** — Could not fetch data: {r.get('error', 'Unknown error')}")
        return

    verdict   = r.get("overall", "")
    compliant = r.get("compliant")

    # ── Expander title ────────────────────────────────────────
    icon  = "✅" if compliant is True else ("⚠️" if compliant is None else "❌")
    label = f"{icon}  {r['ticker']}  ·  {(r.get('name') or '')[:38]}  ·  {r.get('market_cap','N/A')}"

    with st.expander(label, expanded=True):

        # Row 1: sector info + badge
        col_info, col_badge = st.columns([4, 1])
        with col_info:
            st.caption(
                f"📂 {r.get('sector','N/A')}  ·  {(r.get('industry','N/A'))[:35]}  ·  🌍 {r.get('country','N/A')}"
            )
        with col_badge:
            st.markdown(badge_html(verdict), unsafe_allow_html=True)

        st.divider()

        # Row 2: quick stats
        s1, s2, s3, s4 = st.columns(4)
        with s1:
            st.metric("💰 Price",       f"${r['price']:.2f}" if r.get("price") else "N/A")
        with s2:
            st.metric("📈 P/E Ratio",   f"{r['pe_ratio']:.1f}×" if r.get("pe_ratio") else "N/A")
        with s3:
            st.metric("💵 Div Yield",   f"{r.get('dividend_yield', 0):.2f}%")
        with s4:
            purify = r.get("purification_pct") or 0
            st.metric("🤲 Purification", f"{purify:.3f}%" if purify > 0 else "—")

        st.divider()

        # Row 3: business + financial screens side by side
        biz_col, fin_col = st.columns(2)

        with biz_col:
            st.markdown("**🕌 Business Activity**")
            biz = r.get("biz_status", "")
            reason = r.get("biz_reason", "")
            if "PASS" in biz:
                st.success(f"✅ PASS — {reason}")
            elif "REVIEW" in biz:
                st.warning(f"⚠️ NEEDS REVIEW — {reason}")
            else:
                st.error(f"❌ FAIL — {reason}")

        with fin_col:
            st.markdown("**📊 Financial Ratios**")

            debt_lim = THRESHOLDS["max_debt_to_market_cap"] * 100
            int_lim  = THRESHOLDS["max_interest_income_ratio"] * 100
            recv_lim = THRESHOLDS["max_receivables_ratio"] * 100

            dv = r.get("debt_ratio_pct")
            iv = r.get("interest_ratio_pct")
            rv = r.get("recv_ratio_pct")

            def ratio_line(label, val, limit):
                if val is None:
                    icon, color = "⚪", "color:#8B9BB4"
                elif val > limit:
                    icon, color = "❌", "color:#E74C3C"
                else:
                    icon, color = "✅", "color:#27A86E"
                val_str = f"{val:.1f}%" if val is not None else "N/A"
                st.markdown(
                    f"{icon} **{label}:** "
                    f"<span style='{color}; font-family:monospace'>{val_str}</span>"
                    f" <span style='color:#8B9BB4; font-size:0.8rem;'>(max {limit:.0f}%)</span>",
                    unsafe_allow_html=True
                )

            ratio_line("Debt / Mkt Cap",  dv, debt_lim)
            ratio_line("Interest Income", iv, int_lim)
            ratio_line("Receivables",     rv, recv_lim)

        # Purification box
        if purify > 0:
            st.info(
                f"🤲 **Purification Required:** Donate **{purify:.3f}%** of your "
                f"returns to charity to cleanse any residual impermissible income."
            )


# ═══════════════════════════════════════════════════════════════
#  HEADER
# ═══════════════════════════════════════════════════════════════

def render_header():
    st.markdown("""
    <div style="text-align:center; padding:2.5rem 0 1.5rem;">
        <div style="font-size:2.8rem; margin-bottom:0.4rem;">🌙</div>
        <h1 style="font-family:'Cinzel',serif; font-size:2.2rem; font-weight:700;
                   color:#C9A84C; letter-spacing:0.12em; margin:0;">
            HALAL STOCK SCREENER
        </h1>
        <p style="font-family:'Crimson Pro',serif; font-size:1.05rem; color:#8B9BB4;
                  letter-spacing:0.06em; margin-top:0.4rem;">
            Shariah-Compliant Equity Analysis · AAOIFI Standards
        </p>
        <div style="width:80px; height:1px;
                    background:linear-gradient(90deg,transparent,#C9A84C,transparent);
                    margin:1rem auto;"></div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════

def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center; padding:1rem 0 0.5rem;">
            <span style="font-size:1.8rem;">🌙</span>
            <p style="font-family:'Cinzel',serif; color:#C9A84C; font-size:0.85rem;
                      letter-spacing:0.1em; margin:0.3rem 0 0;">HALAL SCREENER</p>
        </div>
        """, unsafe_allow_html=True)

        st.divider()
        st.markdown('<p class="sec-label">⚙️ Screening Standards</p>', unsafe_allow_html=True)

        standard = st.selectbox(
            "Shariah Standard",
            ["AAOIFI (Default)", "Dow Jones Islamic", "S&P Shariah", "Custom"],
            help="Different scholars/indices use different ratio thresholds."
        )

        if standard == "Dow Jones Islamic":
            st.info("All three ratios capped at 33%.")
            debt_lim, int_lim, recv_lim = 33, 5, 33
        elif standard == "S&P Shariah":
            st.info("33% debt · 5% interest · 49% receivables.")
            debt_lim, int_lim, recv_lim = 33, 5, 49
        elif standard == "Custom":
            debt_lim  = st.slider("Max Debt / MktCap (%)",   10, 50, 33)
            int_lim   = st.slider("Max Interest Income (%)",  1, 15,  5)
            recv_lim  = st.slider("Max Receivables (%)",     20, 70, 49)
        else:
            debt_lim, int_lim, recv_lim = 33, 5, 49

        THRESHOLDS["max_debt_to_market_cap"]    = debt_lim  / 100
        THRESHOLDS["max_interest_income_ratio"] = int_lim   / 100
        THRESHOLDS["max_receivables_ratio"]     = recv_lim  / 100

        st.divider()
        st.markdown('<p class="sec-label">📋 Quick Watchlists</p>', unsafe_allow_html=True)

        presets = {
            "🖥️ Big Tech":     "AAPL, MSFT, GOOGL, META, AMZN, NVDA, TSLA",
            "🏥 Healthcare":   "JNJ, PFE, ABBV, MRK, UNH, BMY, AMGN",
            "🛒 Consumer":     "WMT, COST, TGT, MCD, PG, KO, SBUX",
            "🌙 Islamic ETFs": "SPUS, HLAL, ISDU, UMMA",
            "🏦 Banks (Test)": "JPM, BAC, GS, WFC, C",
            "⚡ Energy":       "XOM, CVX, COP, SLB, OXY",
        }

        chosen = st.selectbox("Load a preset", ["— Select —"] + list(presets.keys()))
        if chosen != "— Select —":
            st.session_state["input_tickers"] = presets[chosen]
            st.rerun()

        st.divider()
        st.markdown('<p class="sec-label">ℹ️ About</p>', unsafe_allow_html=True)
        st.caption(
            "Screens stocks using **AAOIFI** Shariah standards across "
            "business activity, three financial ratio tests, and "
            "purification calculation.\n\n"
            "_⚠️ For informational purposes only. Consult a qualified "
            "Islamic finance scholar for authoritative rulings._"
        )


# ═══════════════════════════════════════════════════════════════
#  EXPORT HELPERS
# ═══════════════════════════════════════════════════════════════

def to_excel_bytes(results: list) -> bytes:
    rows = [{
        "Ticker":           r.get("ticker"),
        "Company":          r.get("name"),
        "Sector":           r.get("sector"),
        "Country":          r.get("country"),
        "Price ($)":        r.get("price"),
        "Market Cap":       r.get("market_cap"),
        "P/E Ratio":        r.get("pe_ratio"),
        "Div Yield (%)":    r.get("dividend_yield"),
        "Debt/MktCap (%)":  r.get("debt_ratio_pct"),
        "Interest Inc (%)": r.get("interest_ratio_pct"),
        "Receivables (%)":  r.get("recv_ratio_pct"),
        "Purification (%)": r.get("purification_pct"),
        "Biz Screen":       r.get("biz_status"),
        "Biz Reason":       r.get("biz_reason"),
        "Fin Screen":       r.get("fin_status"),
        "Fin Reason":       r.get("fin_reason"),
        "Overall Verdict":  r.get("overall"),
        "Screened At":      datetime.now().strftime("%Y-%m-%d %H:%M"),
    } for r in results]

    df  = pd.DataFrame(rows)
    buf = io.BytesIO()

    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Halal Screening", index=False)
        from openpyxl.styles import PatternFill, Font, Alignment
        ws = writer.sheets["Halal Screening"]

        for cell in ws[1]:
            cell.fill      = PatternFill("solid", fgColor="0A0F1E")
            cell.font      = Font(name="Calibri", bold=True, color="C9A84C", size=11)
            cell.alignment = Alignment(horizontal="center")

        green  = PatternFill("solid", fgColor="E8F5E9")
        yellow = PatternFill("solid", fgColor="FFF9E6")
        red    = PatternFill("solid", fgColor="FFEBEE")
        vcol   = df.columns.get_loc("Overall Verdict") + 1

        for i, row in enumerate(ws.iter_rows(min_row=2, max_row=len(rows)+1), 1):
            v    = str(ws.cell(row=i+1, column=vcol).value or "")
            fill = green if "✅ HALAL" in v else (yellow if "REVIEW" in v else red)
            for c in row:
                c.fill = fill

        for col in ws.columns:
            ws.column_dimensions[col[0].column_letter].width = min(
                max(len(str(c.value or "")) for c in col) + 3, 45
            )

    buf.seek(0)
    return buf.read()


def to_csv(results: list) -> str:
    return pd.DataFrame([{
        "Ticker":    r.get("ticker"),
        "Company":   r.get("name"),
        "Sector":    r.get("sector"),
        "Price":     r.get("price"),
        "Verdict":   r.get("overall"),
        "Debt%":     r.get("debt_ratio_pct"),
        "Interest%": r.get("interest_ratio_pct"),
        "Purify%":   r.get("purification_pct"),
    } for r in results]).to_csv(index=False)


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    render_header()
    render_sidebar()

    # Session state defaults
    if "results"       not in st.session_state:
        st.session_state.results = []
    if "input_tickers" not in st.session_state:
        st.session_state.input_tickers = "AAPL, MSFT, TSLA, NVDA, JNJ, WMT, JPM, GOOGL"

    # ─────────────────────────────────────────────────────────
    #  INPUT ROW
    # ─────────────────────────────────────────────────────────
    st.markdown('<p class="sec-label">🔍 Tickers to Screen</p>', unsafe_allow_html=True)

    col_ta, col_btn1, col_btn2 = st.columns([5, 1, 1])

    with col_ta:
        tickers_raw = st.text_area(
            label="tickers",
            label_visibility="collapsed",
            value=st.session_state.input_tickers,
            height=80,
            placeholder="Enter tickers separated by commas:  AAPL, MSFT, TSLA ..."
        )

    with col_btn1:
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        screen_btn = st.button("🔍 Screen", use_container_width=True)

    with col_btn2:
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        if st.button("✕ Clear", use_container_width=True):
            st.session_state.results = []
            st.rerun()

    # ─────────────────────────────────────────────────────────
    #  RUN SCREENING
    # ─────────────────────────────────────────────────────────
    if screen_btn and tickers_raw.strip():
        tickers = [
            t.strip().upper()
            for t in tickers_raw.replace("\n", ",").split(",")
            if t.strip()
        ]
        tickers = list(dict.fromkeys(tickers))   # dedupe

        if len(tickers) > 30:
            st.warning("⚠️ Maximum 30 tickers per screen. Using first 30.")
            tickers = tickers[:30]

        progress_bar = st.progress(0, text="Starting analysis...")
        results      = []

        for i, ticker in enumerate(tickers):
            progress_bar.progress(
                (i + 1) / len(tickers),
                text=f"Analyzing **{ticker}** ({i+1}/{len(tickers)})..."
            )
            results.append(screen_stock(ticker))

        progress_bar.empty()

        order = {"✅ HALAL": 0, "⚠️ NEEDS REVIEW": 1, "❌ NOT HALAL": 2, "⚠️ ERROR": 3}
        results.sort(key=lambda x: order.get(x.get("overall", ""), 99))
        st.session_state.results = results
        st.rerun()

    # ─────────────────────────────────────────────────────────
    #  EMPTY STATE
    # ─────────────────────────────────────────────────────────
    results = st.session_state.results

    if not results:
        st.markdown("""
        <div style="text-align:center; padding:5rem 1rem; color:#8B9BB4;">
            <div style="font-size:3rem; margin-bottom:1rem;">🌙</div>
            <p style="font-family:'Cinzel',serif; color:#C9A84C; letter-spacing:0.12em; font-size:0.9rem;">
                AWAITING ANALYSIS
            </p>
            <p style="font-size:0.9rem; max-width:420px; margin:0.5rem auto; line-height:1.7;">
                Enter stock tickers above and press <strong>Screen</strong>
                to begin your Shariah-compliant equity analysis.
            </p>
        </div>
        """, unsafe_allow_html=True)
        return

    # ─────────────────────────────────────────────────────────
    #  SUMMARY METRICS
    # ─────────────────────────────────────────────────────────
    total  = len(results)
    halal  = sum(1 for r in results if r.get("compliant") is True)
    review = sum(1 for r in results if r.get("compliant") is None)
    haram  = sum(1 for r in results if r.get("compliant") is False)

    st.divider()
    st.markdown('<p class="sec-label">📊 Screening Summary</p>', unsafe_allow_html=True)

    m1, m2, m3, m4, m5 = st.columns(5)
    with m1: st.metric("Total Screened",  total)
    with m2: st.metric("✅ Halal",        halal,  delta=f"{int(halal/total*100)}% compliant" if total else None)
    with m3: st.metric("⚠️ Needs Review", review)
    with m4: st.metric("❌ Not Halal",     haram)
    with m5: st.metric("Screened At",     datetime.now().strftime("%H:%M"))

    st.divider()

    # ─────────────────────────────────────────────────────────
    #  TABS
    # ─────────────────────────────────────────────────────────
    tab_all, tab_halal, tab_table = st.tabs(["📋  All Results", "✅  Halal Only", "📊  Data Table"])

    # ── Tab 1: All Results ────────────────────────────────────
    with tab_all:
        fc1, fc2 = st.columns(2)
        with fc1:
            filter_by = st.selectbox(
                "Filter by",
                ["All", "✅ Halal", "⚠️ Needs Review", "❌ Not Halal"],
                key="filter_tab1"
            )
        with fc2:
            sort_by = st.selectbox(
                "Sort by",
                ["Compliance Status", "Ticker A→Z", "Debt %", "Interest %"],
                key="sort_tab1"
            )

        filtered = {
            "All":             results,
            "✅ Halal":        [r for r in results if r.get("compliant") is True],
            "⚠️ Needs Review": [r for r in results if r.get("compliant") is None],
            "❌ Not Halal":    [r for r in results if r.get("compliant") is False],
        }[filter_by]

        if sort_by == "Ticker A→Z":
            filtered = sorted(filtered, key=lambda x: x.get("ticker", ""))
        elif sort_by == "Debt %":
            filtered = sorted(filtered, key=lambda x: x.get("debt_ratio_pct") or 999)
        elif sort_by == "Interest %":
            filtered = sorted(filtered, key=lambda x: x.get("interest_ratio_pct") or 999)

        for r in filtered:
            render_result_card(r)

    # ── Tab 2: Halal Only ─────────────────────────────────────
    with tab_halal:
        halal_list = [r for r in results if r.get("compliant") is True]

        if not halal_list:
            st.info("No fully compliant stocks found. Try different tickers or adjust thresholds in the sidebar.")
        else:
            pills = "  ".join(f"`{r['ticker']}`" for r in halal_list)
            st.markdown(f"**Compliant tickers ({len(halal_list)}):** {pills}")
            st.divider()
            for r in halal_list:
                render_result_card(r)

    # ── Tab 3: Data Table ─────────────────────────────────────
    with tab_table:
        table_rows = [r for r in results if r.get("overall") != "⚠️ ERROR"]
        if table_rows:
            df = pd.DataFrame([{
                "Ticker":     r.get("ticker"),
                "Company":    (r.get("name") or "")[:35],
                "Sector":     (r.get("sector") or "")[:22],
                "Price":      f"${r['price']:.2f}" if r.get("price") else "N/A",
                "Mkt Cap":    r.get("market_cap", "N/A"),
                "Debt %":     fmt(r.get("debt_ratio_pct")),
                "Interest %": fmt(r.get("interest_ratio_pct"), decimals=2),
                "Recv %":     fmt(r.get("recv_ratio_pct")),
                "Purify %":   f"{r['purification_pct']:.3f}%" if (r.get("purification_pct") or 0) > 0 else "—",
                "Verdict":    r.get("overall", ""),
            } for r in table_rows])

            st.dataframe(df, use_container_width=True, hide_index=True, height=420)

    # ─────────────────────────────────────────────────────────
    #  EXPORT ROW
    # ─────────────────────────────────────────────────────────
    st.divider()
    st.markdown('<p class="sec-label">📥 Export Results</p>', unsafe_allow_html=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M")
    e1, e2, e3 = st.columns(3)

    with e1:
        st.download_button(
            "📊 Download Excel",
            data=to_excel_bytes(results),
            file_name=f"halal_screening_{ts}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    with e2:
        st.download_button(
            "📄 Download CSV",
            data=to_csv(results),
            file_name=f"halal_screening_{ts}.csv",
            mime="text/csv",
            use_container_width=True
        )
    with e3:
        st.download_button(
            "🗂 Download JSON",
            data=json.dumps(results, indent=2, default=str),
            file_name=f"halal_screening_{ts}.json",
            mime="application/json",
            use_container_width=True
        )

    # ─────────────────────────────────────────────────────────
    #  FOOTER
    # ─────────────────────────────────────────────────────────
    st.divider()
    st.markdown("""
    <div style="text-align:center; padding:0.5rem 0 1.5rem; color:#8B9BB4; font-size:0.8rem;">
        🌙 <strong style="color:#C9A84C;">Halal Stock Screener</strong> · Built with QuantGPT<br>
        <em>For informational purposes only. This is not a fatwa.
        Consult a qualified Islamic finance scholar for authoritative rulings.</em>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
if __name__ == "__main__":
    main()
