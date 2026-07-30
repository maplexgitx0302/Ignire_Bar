"""Streamlit interface for the Ignire calendar."""

from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from .calendar import (
    MAX_GREGORIAN_DATE,
    MAX_NEW_YEAR,
    MIN_GREGORIAN_DATE,
    build_year_rows,
    get_calendar_year,
    to_gregorian,
    to_new_calendar,
)
from .verification import build_verification_rows


def format_conversion(gregorian_date: date) -> str:
    """Return a localized, human-readable Gregorian-to-Ignire result."""

    result = to_new_calendar(gregorian_date)
    return (
        f"{gregorian_date.isoformat()} → {result.display_date}"
        f"（序日 {result.day_of_year}）"
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


def _render_gregorian_to_ignire() -> None:
    st.subheader("公曆 → 新曆")
    with st.form("gregorian_to_ignire"):
        selected = st.date_input(
            "選擇公曆日期",
            value=date.today()
            if MIN_GREGORIAN_DATE <= date.today() <= MAX_GREGORIAN_DATE
            else date(2023, 8, 23),
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
            f"{(calendar_year.end - date.resolution).isoformat()}"
        )


def _render_ignire_to_gregorian() -> None:
    st.subheader("新曆 → 公曆")
    st.caption(f"可輸入完整可表示的新曆年份：1–{MAX_NEW_YEAR}。")
    year = int(
        st.number_input(
            "新曆年",
            min_value=1,
            max_value=MAX_NEW_YEAR,
            value=1,
            step=1,
        )
    )
    festival_days = get_calendar_year(year).festival_days
    with st.form("ignire_to_gregorian"):
        mode = st.radio("日期類型", ("一般月份", "祭典"), horizontal=True)
        if mode == "一般月份":
            col1, col2 = st.columns(2)
            month = int(col1.number_input("新曆月", 1, 12, 1, 1))
            day = int(col2.number_input("新曆日", 1, 30, 1, 1))
        else:
            month = 0
            day = int(st.number_input("祭典日", 1, festival_days, 1, 1))
        submitted = st.form_submit_button("轉換為公曆", type="primary")
    if submitted:
        converted = to_gregorian(year, month, day)
        source = f"祭典第 {day} 天" if month == 0 else f"{month}/{day}"
        st.success(f"新曆 {year} 年 {source} → 公曆 {converted.isoformat()}")


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
            st.session_state["verification_rows"] = build_verification_rows(
                first_year, last_year
            )
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
        st.dataframe(frame, use_container_width=True, hide_index=True)
        st.download_button(
            "下載驗證 CSV",
            frame.to_csv(index=False).encode("utf-8-sig"),
            "ignire-calendar-verification.csv",
            "text/csv",
        )

    st.divider()
    st.markdown("#### 全年對照表")
    export_year = int(
        st.number_input("匯出的新曆年", 1, MAX_NEW_YEAR, 1, 1, key="export_year")
    )
    export_frame = pd.DataFrame(build_year_rows(export_year))
    details = get_calendar_year(export_year)
    st.caption(
        f"新曆 {export_year} 年共有 {details.length} 天，"
        f"其中 {details.festival_days} 天為祭典。"
    )
    st.download_button(
        "下載全年 CSV",
        export_frame.to_csv(index=False).encode("utf-8-sig"),
        f"ignire-calendar-year-{export_year}.csv",
        "text/csv",
    )
    with st.expander("預覽全年對照表"):
        st.dataframe(export_frame, use_container_width=True, hide_index=True)


def main() -> None:
    """Render the Streamlit application."""

    st.set_page_config(
        page_title="Ignire 新曆轉換器",
        page_icon="🔥",
        layout="wide",
    )
    st.title("Ignire 新曆轉換器")
    st.caption("12 × 30 天，加上年末 5／6 個祭典日的互動曆法工具")
    _render_rules()

    tab1, tab2, tab3 = st.tabs(("公曆 → 新曆", "新曆 → 公曆", "驗證與匯出"))
    with tab1:
        _render_gregorian_to_ignire()
    with tab2:
        _render_ignire_to_gregorian()
    with tab3:
        _render_tools()

    st.divider()
    st.caption("Ignire Calendar · 紀元：公曆 2023-08-23")


if __name__ == "__main__":
    main()
