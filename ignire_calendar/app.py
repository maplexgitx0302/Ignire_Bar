"""Streamlit interface for the Ignire calendar."""

from __future__ import annotations

import html
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

from .calendar import (
    DAYS_PER_MONTH,
    MAX_GREGORIAN_DATE,
    MAX_NEW_YEAR,
    MIN_GREGORIAN_DATE,
    MONTHS_PER_YEAR,
    build_year_rows,
    get_calendar_year,
    to_gregorian,
    to_new_calendar,
    weekday_label,
)
from .verification import build_verification_rows

# "Today" follows the community's local time rather than the server's clock,
# which is usually UTC on hosted Streamlit deployments.
LOCAL_TIME_ZONE = ZoneInfo("Asia/Taipei")
GRID_COLUMNS = 6


def local_today() -> date:
    return datetime.now(LOCAL_TIME_ZONE).date()


def format_conversion(gregorian_date: date) -> str:
    """Return a localized, human-readable Gregorian-to-Ignire result."""

    result = to_new_calendar(gregorian_date)
    return (
        f"{gregorian_date.isoformat()}（{weekday_label(gregorian_date)}）→ "
        f"{result.display_date}（序日 {result.day_of_year}）"
    )


def _render_today(today: date) -> None:
    result = to_new_calendar(today)
    calendar_year = get_calendar_year(result.year)
    if result.is_festival:
        headline = f"祭典第 {result.day} 天"
    else:
        headline = f"{result.month} 月 {result.day} 日"
    with st.container(border=True):
        st.caption(f"今日 · 公曆 {today.isoformat()}（{weekday_label(today)}）")
        st.markdown(f"## 新曆 {result.display_year} {headline}")
        days_left = calendar_year.length - result.day_of_year
        festival_start = calendar_year.start + timedelta(days=MONTHS_PER_YEAR * DAYS_PER_MONTH)
        if result.is_festival:
            st.caption(f"祭典進行中，距離新年還有 {days_left + 1} 天。")
        else:
            st.caption(
                f"距離祭典（{festival_start.isoformat()}）還有 {(festival_start - today).days} 天；"
                f"今年共有 {calendar_year.festival_days} 個祭典日。"
            )


def _render_rules() -> None:
    with st.expander("曆法規則", expanded=False):
        st.markdown(
            """
- **紀元**：新曆 1 年 1/1 = 公曆 **2023-08-23**。
- **月份**：每年 12 個月、每月 30 天；之後是 5 或 6 個祭典日。
- **年界線**：公曆 Y 年的新曆元旦，在 (Y+1) 為閏年時是 8/23，否則是 8/22。
- **固定對齊**：公曆 8/17 永遠是祭典第 1 天；3/1 永遠是新曆 7/12。
- **紀元以前**：顯示為「前一年／前 X 年」，不使用「0 年」字樣。
            """
        )


def _render_gregorian_to_ignire(today: date) -> None:
    st.subheader("公曆 → 新曆")
    with st.form("gregorian_to_ignire"):
        selected = st.date_input(
            "選擇公曆日期",
            value=today if MIN_GREGORIAN_DATE <= today <= MAX_GREGORIAN_DATE else date(2023, 8, 23),
            min_value=MIN_GREGORIAN_DATE,
            max_value=MAX_GREGORIAN_DATE,
            format="YYYY-MM-DD",
        )
        submitted = st.form_submit_button("轉換為新曆", type="primary")
    if submitted:
        result = to_new_calendar(selected)
        calendar_year = get_calendar_year(result.year)
        st.success(format_conversion(selected))
        col1, col2, col3 = st.columns(3)
        col1.metric("新曆年份", result.display_year)
        col2.metric("全年天數", calendar_year.length)
        col3.metric("祭典日數", calendar_year.festival_days)
        st.caption(
            f"此新曆年：{calendar_year.start.isoformat()} 至 "
            f"{(calendar_year.end - timedelta(days=1)).isoformat()}"
        )


def _render_ignire_to_gregorian() -> None:
    st.subheader("新曆 → 公曆")
    st.caption(f"可輸入完整可表示的新曆年份：1–{MAX_NEW_YEAR}。")
    year = int(st.number_input("新曆年", min_value=1, max_value=MAX_NEW_YEAR, value=1, step=1))
    festival_days = get_calendar_year(year).festival_days
    with st.form("ignire_to_gregorian"):
        mode = st.radio("日期類型", ("一般月份", "祭典"), horizontal=True)
        if mode == "一般月份":
            col1, col2 = st.columns(2)
            month = int(col1.number_input("新曆月", 1, MONTHS_PER_YEAR, 1, 1))
            day = int(col2.number_input("新曆日", 1, DAYS_PER_MONTH, 1, 1))
        else:
            month = 0
            label = f"祭典日（本年共 {festival_days} 天）"
            day = int(st.number_input(label, 1, festival_days, 1, 1))
        submitted = st.form_submit_button("轉換為公曆", type="primary")
    if submitted:
        converted = to_gregorian(year, month, day)
        source = f"祭典第 {day} 天" if month == 0 else f"{month}/{day}"
        st.success(
            f"新曆 {year} 年 {source} → 公曆 {converted.isoformat()}（{weekday_label(converted)}）"
        )


def _month_grid_html(year: int, month: int, today: date) -> str:
    calendar_year = get_calendar_year(year)
    if month == 0:
        first_offset = MONTHS_PER_YEAR * DAYS_PER_MONTH
        length = calendar_year.festival_days
    else:
        first_offset = (month - 1) * DAYS_PER_MONTH
        length = DAYS_PER_MONTH
    cells = []
    for index in range(length):
        gregorian_date = calendar_year.start + timedelta(days=first_offset + index)
        classes = "cell today" if gregorian_date == today else "cell"
        cells.append(
            f'<div class="{classes}"><div class="num">{index + 1}</div>'
            f'<div class="greg">{gregorian_date.month}/{gregorian_date.day} '
            f"{html.escape(weekday_label(gregorian_date)[-1])}</div></div>"
        )
    return f"""
<style>
.ignire-grid {{ display: grid; grid-template-columns: repeat({GRID_COLUMNS}, minmax(0, 1fr));
  gap: 6px; margin: 0.5rem 0 1rem; }}
.ignire-grid .cell {{ border: 1px solid rgba(128,128,128,0.25); border-radius: 8px;
  padding: 6px 8px; min-height: 56px; }}
.ignire-grid .cell.today {{ border: 2px solid #D96C3B; background: rgba(217,108,59,0.12); }}
.ignire-grid .num {{ font-size: 1.15rem; font-weight: 700; }}
.ignire-grid .greg {{ font-size: 0.75rem; opacity: 0.7; }}
</style>
<div class="ignire-grid">{''.join(cells)}</div>
"""


def _render_month_view(today: date) -> None:
    st.subheader("月曆檢視")
    current = to_new_calendar(today)
    col1, col2 = st.columns(2)
    year = int(
        col1.number_input(
            "新曆年", 1, MAX_NEW_YEAR, max(current.year, 1), 1, key="month_view_year"
        )
    )
    options = [*range(1, MONTHS_PER_YEAR + 1), 0]
    default_month = current.month if current.year == year else 1
    month = col2.selectbox(
        "月份",
        options,
        index=options.index(default_month),
        format_func=lambda value: "祭典" if value == 0 else f"{value} 月",
        key="month_view_month",
    )
    title = "祭典" if month == 0 else f"{month} 月"
    first = to_gregorian(year, month, 1)
    st.caption(
        f"新曆 {year} 年 {title}，自公曆 {first.isoformat()} 起。每格下方為對應公曆日期與星期。"
    )
    st.markdown(_month_grid_html(year, month, today), unsafe_allow_html=True)


def _render_tools() -> None:
    st.subheader("驗證與匯出")
    st.markdown("#### 規則驗證")
    col1, col2 = st.columns(2)
    first_year = int(col1.number_input("起始公曆年", 2, 9998, 2020, 1))
    last_year = int(col2.number_input("結束公曆年", 2, 9998, 2026, 1))
    if st.button("執行驗證", type="primary"):
        if first_year > last_year:
            st.error("起始年份不可晚於結束年份。")
        elif last_year - first_year > 499:
            st.error("一次最多驗證 500 年。")
        else:
            st.session_state["verification_rows"] = build_verification_rows(first_year, last_year)
            st.session_state["verification_range"] = (first_year, last_year)
    rows = st.session_state.get("verification_rows")
    if rows:
        frame = pd.DataFrame(rows)
        verified_range = st.session_state["verification_range"]
        st.caption(f"目前結果：公曆 {verified_range[0]}–{verified_range[1]} 年")
        failures = sum(row["結果"] == "❌" for row in rows)
        if failures:
            st.error(f"發現 {failures} 項規則不符。")
        else:
            st.success(f"全部 {len(rows)} 項規則驗證通過。")
        st.dataframe(frame, width="stretch", hide_index=True)
        st.download_button(
            "下載驗證 CSV",
            frame.to_csv(index=False).encode("utf-8-sig"),
            "ignire-calendar-verification.csv",
            "text/csv",
        )

    st.divider()
    st.markdown("#### 全年對照表")
    export_year = int(st.number_input("匯出的新曆年", 1, MAX_NEW_YEAR, 1, 1, key="export_year"))
    export_frame = pd.DataFrame(build_year_rows(export_year))
    details = get_calendar_year(export_year)
    st.caption(
        f"新曆 {export_year} 年共有 {details.length} 天，其中 {details.festival_days} 天為祭典。"
    )
    st.download_button(
        "下載全年 CSV",
        export_frame.to_csv(index=False).encode("utf-8-sig"),
        f"ignire-calendar-year-{export_year}.csv",
        "text/csv",
    )
    with st.expander("預覽全年對照表"):
        st.dataframe(export_frame, width="stretch", hide_index=True)


def main() -> None:
    """Render the Streamlit application."""

    st.set_page_config(page_title="Ignire 新曆轉換器", page_icon="🔥", layout="wide")
    st.title("Ignire 新曆轉換器")
    st.caption("12 × 30 天，加上年末 5／6 個祭典日的互動曆法工具")
    today = local_today()
    _render_today(today)
    _render_rules()

    tabs = st.tabs(("公曆 → 新曆", "新曆 → 公曆", "月曆檢視", "驗證與匯出"))
    with tabs[0]:
        _render_gregorian_to_ignire(today)
    with tabs[1]:
        _render_ignire_to_gregorian()
    with tabs[2]:
        _render_month_view(today)
    with tabs[3]:
        _render_tools()

    st.divider()
    st.caption("Ignire Calendar · 紀元：公曆 2023-08-23 · 「今日」以台北時間計算")


if __name__ == "__main__":
    main()
