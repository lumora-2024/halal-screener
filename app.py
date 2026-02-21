"""
🌙 Halal Stock Screener — Streamlit Web App
Methodology: Zoya (https://zoya.finance) + Islamicly (https://www.islamicly.com)
Standard:    AAOIFI (Accounting & Auditing Organization for Islamic Financial Institutions)
"""

import streamlit as st
import pandas as pd
import io
import json
from datetime import datetime

from halal_screener import screen_stock, THRESHOLDS

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="🌙 Halal Stock Screener",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": (
            "🌙 Halal Stock Screener\n"
            "Methodology: Zoya + Islamicly (AAOIFI Standard)\n"
            "Built with QuantGPT"
        )
    }
)

# ─────────────────────────────────────────────
#  CSS
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

/* Verdict badges */
.badge-compliant    { display:inline-block; padding:3px 14px; border-radius:999px; font-family:'Cinzel',serif; font-size:0.72rem; font-weight:700; letter-spacing:0.08em; background:rgba(39,168,110,0.15); color:#27A86E; border:1px solid rgba(39,168,110,0.35); }
.badge-questionable { display:inline-block; padding:3px 14px; border-radius:999px; font-family:'Cinzel',serif; font-size:0.72rem; font-weight:700; letter-spacing:0.08em; background:rgba(212,160,23,0.15); color:#D4A017; border:1px solid rgba(212,160,23,0.35); }
.badge-fail         { display:inline-block; padding:3px 14px; border-radius:999px; font-family:'Cinzel',serif; font-size:0.72rem; font-weight:700; letter-spacing:0.08em; background:rgba(231,76,60,0.15);  color:#E74C3C; border:1px solid rgba(231,76,60,0.35); }

/* Labels */
.sec-label { font-family:'Cinzel',serif; font-size:0.6rem; letter-spacing:0.22em; text-transform:uppercase; color:#8B6914; margin-bottom:0.4rem; }

/* Source tag */
.source-tag { display:inline-block; background:rgba(201,168,76,0.08); border:1px solid rgba(201,168,76,0.2); border-radius:4px; padding:1px 8px; font-size:0.72rem; color:#C9A84C; margin-right:4px; font-family:'JetBrains Mono',monospace; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════

def badge_html(verdict: str) -> str:
    if "COMPLIANT" in verdict and "NON" not in verdict:
        return f'<span class="badge-compliant">{verdict}</span>'
    elif "QUESTIONABLE" in verdict:
        return f'<span class="badge-questionable">{verdict}</span>'
    else:
        return f'<span class="badge-fail">{verdict}</span>'


def fmt(value, suffix="%", decimals=1):
    if value is None:
        return "N/A"
    return f"{value:.{decimals}f}{suffix}"


# ═══════════════════════════════════════════════════════════════
#  RESULT CARD
# ═══════════════════════════════════════════════════════════════

def render_result_card(r: dict):
    if r.get("overall") == "⚠️ ERROR":
        st.warning(f"⚠️ **{r['ticker']}** — Could not fetch data: {r.get('error','Unknown')}")
        return

    verdict   = r.get("overall", "")
    compliant = r.get("compliant")

    icon  = "✅" if compliant is True else ("🟡" if compliant is None else "❌")
    label = f"{icon}  {r['ticker']}  ·  {(r.get('name') or '')[:38]}  ·  {r.get('market_cap','N/A')}"

    with st.expander(label, expanded=True):

        # ── Header row ────────────────────────────────────────
        col_info, col_badge = st.columns([4, 1])
        with col_info:
            st.caption(
                f"📂 {r.get('sector','N/A')}  ·  "
                f"{(r.get('industry','N/A'))[:35]}  ·  "
                f"🌍 {r.get('country','N/A')}"
            )
        with col_badge:
            st.markdown(badge_html(verdict), unsafe_allow_html=True)

        # ── Methodology source tags ───────────────────────────
        st.markdown(
            '<span class="source-tag">Zoya</span>'
            '<span class="source-tag">Islamicly</span>'
            '<span class="source-tag">AAOIFI</span>',
            unsafe_allow_html=True
        )

        st.divider()

        # ── Quick stats ───────────────────────────────────────
        s1, s2, s3, s4 = st.columns(4)
        with s1: st.metric("💰 Price",      f"${r['price']:.2f}" if r.get("price") else "N/A")
        with s2: st.metric("📈 P/E",        f"{r['pe_ratio']:.1f}×" if r.get("pe_ratio") else "N/A")
        with s3: st.metric("💵 Div Yield",  f"{r.get('dividend_yield',0):.2f}%")
        with s4:
            purify = r.get("purification_pct") or 0
            st.metric("🤲 Purify %", f"{purify:.3f}%" if purify > 0 else "—")

        st.divider()

        # ── Two-column screens ────────────────────────────────
        biz_col, fin_col = st.columns(2)

        # ── Screen 1: Business Activity ───────────────────────
        with biz_col:
            st.markdown("**🕌 Screen 1 — Business Activity**")
            st.caption("*Islamicly: <5% haram revenue · Zoya: same + gray-area = Questionable*")

            bv     = r.get("biz_verdict", "fail")
            reason = r.get("biz_reason", "")
            detail = r.get("biz_detail", "")

            if bv == "pass":
                st.success(f"✅ **PASS** — {reason}")
            elif bv == "questionable":
                st.warning(f"🟡 **QUESTIONABLE** — {reason}")
                if detail:
                    st.caption(detail)
            else:
                st.error(f"❌ **NON-COMPLIANT** — {reason}")
                if detail:
                    st.caption(detail)

        # ── Screen 2: Financial Ratios ────────────────────────
        with fin_col:
            st.markdown("**📊 Screen 2 — Financial Ratios**")
            st.caption("*Zoya/AAOIFI: Debt <30% · Interest-bearing securities <30%*")

            debt_lim = THRESHOLDS["max_debt_to_market_cap"] * 100
            sec_lim  = THRESHOLDS["max_interest_bearing_securities"] * 100
            rev_lim  = THRESHOLDS["max_haram_revenue_ratio"] * 100

            dv = r.get("debt_ratio_pct")
            sv = r.get("sec_ratio_pct")
            rv = r.get("haram_rev_pct", 0)

            def ratio_row(label, val, limit, formula_note=""):
                if val is None:
                    icon = "⚪"
                    color = "color:#8B9BB4"
                elif val > limit:
                    icon = "❌"
                    color = "color:#E74C3C"
                else:
                    icon = "✅"
                    color = "color:#27A86E"
                val_str = f"{val:.1f}%" if val is not None else "N/A"
                st.markdown(
                    f"{icon} **{label}:** "
                    f"<span style='{color}; font-family:monospace'>{val_str}</span>"
                    f" <span style='color:#8B9BB4;font-size:0.78rem;'>(max {limit:.0f}%)</span>",
                    unsafe_allow_html=True
                )
                if formula_note:
                    st.caption(formula_note)

            ratio_row(
                "Interest-Bearing Debt",
                dv, debt_lim,
                "Total Debt / Market Cap  [Zoya]"
            )
            ratio_row(
                "Interest-Bearing Securities",
                sv, sec_lim,
                "(Cash + Deposits) / Market Cap  [Zoya]"
            )
            ratio_row(
                "Impermissible Revenue",
                rv, rev_lim,
                "Haram Income / Total Revenue  [Islamicly]"
            )

        # ── Purification ──────────────────────────────────────
        if purify > 0:
            st.info(
                f"🤲 **Purification Required ({purify:.3f}%):** "
                f"{r.get('purification_note','')}  "
                f"*This calculation follows the Zoya & Islamicly methodology.*"
            )

        # ── Questionable detail ───────────────────────────────
        if compliant is None and r.get("biz_detail"):
            st.caption(f"ℹ️ {r.get('biz_detail')}")


# ═══════════════════════════════════════════════════════════════
#  HEADER
# ═══════════════════════════════════════════════════════════════

def render_header():
    st.markdown("""
    <div style="text-align:center; padding:2.5rem 0 1rem;">
        <div style="font-size:2.8rem; margin-bottom:0.4rem;">🌙</div>
        <h1 style="font-family:'Cinzel',serif; font-size:2.1rem; font-weight:700;
                   color:#C9A84C; letter-spacing:0.12em; margin:0;">
            HALAL STOCK SCREENER
        </h1>
        <p style="font-family:'Crimson Pro',serif; font-size:1rem; color:#8B9BB4;
                  letter-spacing:0.06em; margin-top:0.4rem;">
            AAOIFI Standard · Methodology aligned with
            <a href="https://zoya.finance" target="_blank"
               style="color:#C9A84C; text-decoration:none;">Zoya</a>
            &amp;
            <a href="https://www.islamicly.com" target="_blank"
               style="color:#C9A84C; text-decoration:none;">Islamicly</a>
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

        # ── Methodology info ──────────────────────────────────
        st.markdown('<p class="sec-label">📖 Methodology</p>', unsafe_allow_html=True)
        st.markdown("""
        <div style="font-size:0.82rem; color:#8B9BB4; line-height:1.6; margin-bottom:0.5rem;">
            Screening follows
            <a href="https://zoya.finance" target="_blank" style="color:#C9A84C;">Zoya</a>
            +
            <a href="https://www.islamicly.com" target="_blank" style="color:#C9A84C;">Islamicly</a>
            — both certified AAOIFI.<br><br>
            <strong style="color:#F0EBE0;">3-Tier Rating:</strong><br>
            ✅ <strong>Compliant</strong> — passes all screens<br>
            🟡 <strong>Questionable</strong> — gray-area (Zoya)<br>
            ❌ <strong>Non-Compliant</strong> — fails a screen
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        # ── Threshold display (not editable in standard mode) ─
        st.markdown('<p class="sec-label">⚙️ AAOIFI Thresholds</p>', unsafe_allow_html=True)

        standard = st.selectbox(
            "Standard",
            ["Zoya / Islamicly (AAOIFI)", "Dow Jones Islamic (33%)", "Custom"],
            help=(
                "Zoya & Islamicly both use 30% thresholds derived from the hadith "
                "of Saad Bin Abi Waqas. DJIM uses 33%."
            )
        )

        if standard == "Dow Jones Islamic (33%)":
            debt_lim, sec_lim, rev_lim = 33, 33, 5
            st.info("DJIM uses 33% for debt & securities thresholds.")
        elif standard == "Custom":
            debt_lim = st.slider("Max Debt / MktCap (%)",             10, 50, 30)
            sec_lim  = st.slider("Max Interest Securities / MktCap (%)", 10, 50, 30)
            rev_lim  = st.slider("Max Impermissible Revenue (%)",       1, 15,  5)
        else:
            debt_lim, sec_lim, rev_lim = 30, 30, 5

        THRESHOLDS["max_debt_to_market_cap"]          = debt_lim / 100
        THRESHOLDS["max_interest_bearing_securities"] = sec_lim  / 100
        THRESHOLDS["max_haram_revenue_ratio"]         = rev_lim  / 100

        # Show current thresholds
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Debt limit",       f"{debt_lim}%")
            st.metric("Securities limit", f"{sec_lim}%")
        with col_b:
            st.metric("Haram rev limit",  f"{rev_lim}%")

        st.divider()

        # ── Quick watchlists ──────────────────────────────────
        st.markdown('<p class="sec-label">📋 Quick Watchlists</p>', unsafe_allow_html=True)

        presets = {
            "🖥️ Big Tech":     "AAPL, MSFT, GOOGL, META, AMZN, NVDA, TSLA",
            "🏥 Healthcare":   "JNJ, PFE, ABBV, MRK, UNH, BMY, AMGN",
            "🛒 Consumer":     "WMT, COST, TGT, MCD, PG, KO, SBUX",
            "🌙 Islamic ETFs": "SPUS, HLAL, ISDU, UMMA",
            "🏦 Banks (Test)": "JPM, BAC, GS, WFC, C",
            "⚡ Energy":       "XOM, CVX, COP, SLB, OXY",
        }

        chosen = st.selectbox("Load preset", ["— Select —"] + list(presets.keys()))
        if chosen != "— Select —":
            st.session_state["input_tickers"] = presets[chosen]
            st.rerun()

        st.divider()

        # ── Disclaimer ────────────────────────────────────────
        st.markdown('<p class="sec-label">⚠️ Disclaimer</p>', unsafe_allow_html=True)
        st.caption(
            "For informational purposes only. This tool mirrors the public "
            "methodologies of Zoya and Islamicly but is **not affiliated** with either. "
            "Consult a qualified Islamic finance scholar for authoritative rulings."
        )


# ═══════════════════════════════════════════════════════════════
#  EXPORT HELPERS
# ═══════════════════════════════════════════════════════════════

def to_excel_bytes(results: list) -> bytes:
    rows = [{
        "Ticker":                   r.get("ticker"),
        "Company":                  r.get("name"),
        "Sector":                   r.get("sector"),
        "Country":                  r.get("country"),
        "Price ($)":                r.get("price"),
        "Market Cap":               r.get("market_cap"),
        "P/E":                      r.get("pe_ratio"),
        "Div Yield (%)":            r.get("dividend_yield"),
        "Debt / MktCap (%)":        r.get("debt_ratio_pct"),
        "Int. Securities / MktCap": r.get("sec_ratio_pct"),
        "Haram Revenue (%)":        r.get("haram_rev_pct"),
        "Purification (%)":         r.get("purification_pct"),
        "Business Screen":          r.get("biz_status"),
        "Business Reason":          r.get("biz_reason"),
        "Financial Screen":         r.get("fin_status"),
        "Financial Reason":         r.get("fin_reason"),
        "Overall Verdict":          r.get("overall"),
        "Methodology":              r.get("methodology"),
        "Screened At":              r.get("screened_at"),
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
            fill = green if "COMPLIANT" in v and "NON" not in v else (
                   yellow if "QUESTIONABLE" in v else red)
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
        "Ticker":           r.get("ticker"),
        "Company":          r.get("name"),
        "Sector":           r.get("sector"),
        "Price":            r.get("price"),
        "Debt/MktCap%":     r.get("debt_ratio_pct"),
        "IntSec/MktCap%":   r.get("sec_ratio_pct"),
        "HaramRev%":        r.get("haram_rev_pct"),
        "Purify%":          r.get("purification_pct"),
        "Verdict":          r.get("overall"),
        "ScreenedAt":       r.get("screened_at"),
    } for r in results]).to_csv(index=False)


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    render_header()
    render_sidebar()

    if "results"       not in st.session_state: st.session_state.results       = []
    if "input_tickers" not in st.session_state: st.session_state.input_tickers = "AAPL, MSFT, TSLA, NVDA, JNJ, WMT, JPM, GOOGL"

    # ─────────────────────────────────────────────────────────
    #  INPUT ROW
    # ─────────────────────────────────────────────────────────
    st.markdown('<p class="sec-label">🔍 Enter Tickers</p>', unsafe_allow_html=True)

    col_ta, col_btn1, col_btn2 = st.columns([5, 1, 1])

    with col_ta:
        tickers_raw = st.text_area(
            label="tickers",
            label_visibility="collapsed",
            value=st.session_state.input_tickers,
            height=80,
            placeholder="AAPL, MSFT, TSLA, NVDA, ..."
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
        tickers = list(dict.fromkeys(tickers))

        if len(tickers) > 30:
            st.warning("⚠️ Max 30 tickers per screen. Using first 30.")
            tickers = tickers[:30]

        progress_bar = st.progress(0, text="Initialising...")
        results      = []

        for i, ticker in enumerate(tickers):
            progress_bar.progress(
                (i + 1) / len(tickers),
                text=f"Screening **{ticker}** using Zoya/Islamicly methodology... ({i+1}/{len(tickers)})"
            )
            results.append(screen_stock(ticker))

        progress_bar.empty()

        order = {
            "✅ COMPLIANT":    0,
            "🟡 QUESTIONABLE": 1,
            "❌ NON-COMPLIANT": 2,
            "⚠️ ERROR":        3
        }
        results.sort(key=lambda x: order.get(x.get("overall", ""), 99))
        st.session_state.results = results
        st.rerun()

    # ─────────────────────────────────────────────────────────
    #  EMPTY STATE
    # ─────────────────────────────────────────────────────────
    results = st.session_state.results

    if not results:
        st.markdown("""
        <div style="text-align:center; padding:4rem 1rem; color:#8B9BB4;">
            <div style="font-size:3rem; margin-bottom:1rem;">🌙</div>
            <p style="font-family:'Cinzel',serif; color:#C9A84C; letter-spacing:0.12em; font-size:0.9rem;">
                AWAITING ANALYSIS
            </p>
            <p style="font-size:0.9rem; max-width:460px; margin:0.5rem auto; line-height:1.8;">
                Enter stock tickers above and press <strong>Screen</strong>.<br>
                Methodology follows
                <a href="https://zoya.finance" target="_blank" style="color:#C9A84C;">Zoya</a>
                and
                <a href="https://www.islamicly.com" target="_blank" style="color:#C9A84C;">Islamicly</a>
                — both AAOIFI certified.
            </p>
        </div>
        """, unsafe_allow_html=True)
        return

    # ─────────────────────────────────────────────────────────
    #  SUMMARY METRICS
    # ─────────────────────────────────────────────────────────
    total  = len(results)
    comp   = sum(1 for r in results if r.get("compliant") is True)
    quest  = sum(1 for r in results if r.get("compliant") is None)
    fail   = sum(1 for r in results if r.get("compliant") is False)

    st.divider()
    st.markdown('<p class="sec-label">📊 Summary</p>', unsafe_allow_html=True)

    m1, m2, m3, m4, m5 = st.columns(5)
    with m1: st.metric("Total",              total)
    with m2: st.metric("✅ Compliant",        comp,  delta=f"{int(comp/total*100)}%" if total else None)
    with m3: st.metric("🟡 Questionable",     quest)
    with m4: st.metric("❌ Non-Compliant",     fail)
    with m5: st.metric("🕐 Screened At",      datetime.now().strftime("%H:%M"))

    # Methodology note
    st.markdown(
        '<p style="font-size:0.78rem; color:#8B9BB4; margin-top:0.3rem;">'
        '📖 Screening methodology: '
        '<a href="https://help.zoya.finance/en/articles/4189798" target="_blank" style="color:#C9A84C;">Zoya (AAOIFI)</a>'
        ' · '
        '<a href="https://www.islamicly.com/home/screeningProcess" target="_blank" style="color:#C9A84C;">Islamicly (AAOIFI)</a>'
        ' · Thresholds: Debt &lt;30%, Securities &lt;30%, Haram revenue &lt;5%'
        '</p>',
        unsafe_allow_html=True
    )

    st.divider()

    # ─────────────────────────────────────────────────────────
    #  TABS
    # ─────────────────────────────────────────────────────────
    tab_all, tab_comp, tab_quest, tab_table = st.tabs([
        "📋  All Results",
        "✅  Compliant",
        "🟡  Questionable",
        "📊  Data Table"
    ])

    # ── All Results ───────────────────────────────────────────
    with tab_all:
        fc1, fc2 = st.columns(2)
        with fc1:
            filter_by = st.selectbox(
                "Filter",
                ["All", "✅ Compliant", "🟡 Questionable", "❌ Non-Compliant"],
                key="filter_tab1"
            )
        with fc2:
            sort_by = st.selectbox(
                "Sort by",
                ["Compliance Status", "Ticker A→Z", "Debt %", "Securities %"],
                key="sort_tab1"
            )

        filtered = {
            "All":               results,
            "✅ Compliant":      [r for r in results if r.get("compliant") is True],
            "🟡 Questionable":   [r for r in results if r.get("compliant") is None],
            "❌ Non-Compliant":  [r for r in results if r.get("compliant") is False],
        }[filter_by]

        if sort_by == "Ticker A→Z":
            filtered = sorted(filtered, key=lambda x: x.get("ticker",""))
        elif sort_by == "Debt %":
            filtered = sorted(filtered, key=lambda x: x.get("debt_ratio_pct") or 999)
        elif sort_by == "Securities %":
            filtered = sorted(filtered, key=lambda x: x.get("sec_ratio_pct") or 999)

        for r in filtered:
            render_result_card(r)

    # ── Compliant ─────────────────────────────────────────────
    with tab_comp:
        comp_list = [r for r in results if r.get("compliant") is True]
        if not comp_list:
            st.info("No fully compliant stocks in this screen. Try different tickers.")
        else:
            pills = "  ".join(f"`{r['ticker']}`" for r in comp_list)
            st.markdown(f"**Compliant tickers ({len(comp_list)}):** {pills}")
            st.divider()
            for r in comp_list:
                render_result_card(r)

    # ── Questionable ──────────────────────────────────────────
    with tab_quest:
        quest_list = [r for r in results if r.get("compliant") is None]
        if not quest_list:
            st.info("No questionable stocks in this screen.")
        else:
            st.markdown("""
            **About Questionable stocks** *(Zoya definition)*

            A stock is rated Questionable when either:
            1. The company operates in a gray-area industry where scholars disagree on permissibility
               *(e.g. advertising platforms, supermarkets, hotels, diversified conglomerates)*
            2. There is insufficient public data to make a confident compliance determination

            *Exercise caution and do your own research before investing in these.*
            """)
            st.divider()
            for r in quest_list:
                render_result_card(r)

    # ── Data Table ────────────────────────────────────────────
    with tab_table:
        table_rows = [r for r in results if r.get("overall") != "⚠️ ERROR"]
        if table_rows:
            df = pd.DataFrame([{
                "Ticker":         r.get("ticker"),
                "Company":        (r.get("name") or "")[:32],
                "Sector":         (r.get("sector") or "")[:22],
                "Price":          f"${r['price']:.2f}" if r.get("price") else "N/A",
                "Mkt Cap":        r.get("market_cap","N/A"),
                "Debt %":         fmt(r.get("debt_ratio_pct")),
                "Int. Sec %":     fmt(r.get("sec_ratio_pct")),
                "Haram Rev %":    fmt(r.get("haram_rev_pct"), decimals=3),
                "Purify %":       f"{r['purification_pct']:.3f}%" if (r.get("purification_pct") or 0) > 0 else "—",
                "Verdict":        r.get("overall",""),
            } for r in table_rows])

            st.dataframe(df, use_container_width=True, hide_index=True, height=420)
            st.caption("Debt % and Int. Sec % use Zoya's 30% threshold. Haram Rev % uses Islamicly's 5% threshold.")

    # ─────────────────────────────────────────────────────────
    #  EXPORT
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
    <div style="text-align:center; padding:0.5rem 0 1.5rem; color:#8B9BB4; font-size:0.8rem; line-height:1.8;">
        🌙 <strong style="color:#C9A84C;">Halal Stock Screener</strong> · Built with QuantGPT<br>
        Methodology aligned with
        <a href="https://zoya.finance" target="_blank" style="color:#C9A84C;">Zoya</a>
        and
        <a href="https://www.islamicly.com" target="_blank" style="color:#C9A84C;">Islamicly</a>
        · AAOIFI Certified Standard<br>
        <em>Not affiliated with Zoya or Islamicly.
        For informational purposes only. Not a fatwa.
        Consult a qualified Islamic finance scholar.</em>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
