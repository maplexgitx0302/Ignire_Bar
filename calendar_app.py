# calendar_app.py
# Run: streamlit run calendar_app.py

from __future__ import annotations
import streamlit as st
import pandas as pd
from datetime import date, timedelta

# ======================
# 固定紀元與規則
# ======================
EPOCH_START = date(2023, 8, 23)   # 新曆 1 年 1/1
EPOCH_YEAR = 1


def is_leap_year(y: int) -> bool:
    """公曆閏年：4 整除且 100 不整除，或 400 整除。"""
    return (y % 4 == 0 and y % 100 != 0) or (y % 400 == 0)


def new_year_start_for_gregorian_year(Y: int) -> date:
    """
    規則修正（關鍵）：
    某公曆年 Y 的新曆 1/1 = 
      - Y-08-23 若 (Y+1) 為閏年
      - Y-08-22 否則
    這確保 8/17 永遠為年末1、3/1 永遠為 7/12。
    """
    return date(Y, 8, 23 if is_leap_year(Y + 1) else 22)


def next_start(cur_start: date) -> date:
    """由當前新曆年起點 cur_start 推算下一個新曆年起點。"""
    Y_next = cur_start.year + 1
    return new_year_start_for_gregorian_year(Y_next)


def prev_start(cur_start: date) -> date:
    """由當前新曆年起點 cur_start 推算上一個新曆年起點。"""
    Y_prev = cur_start.year - 1
    return new_year_start_for_gregorian_year(Y_prev)


def locate_new_year(g: date):
    """
    將公曆日期 g 歸屬到某個新曆年：
      回傳 (n_year, start_greg, next_greg)
    說明：
      - n_year >= 1 表示第 n 年；
      - n_year <= 0 僅作內部計算用，對外顯示為「前一年 / 前 X 年」，不使用 0 年字樣。
    """
    S = EPOCH_START
    ny = EPOCH_YEAR

    if g >= S:
        while True:
            Sn = next_start(S)
            if g < Sn:
                return ny, S, Sn
            S, ny = Sn, ny + 1
    else:
        while g < S:
            Sp = prev_start(S)
            S, ny = Sp, ny - 1
        return ny, S, next_start(S)


def year_label(ny: int) -> str:
    """外部顯示年份：不顯示 0 年，改為『前一年 / 前 X 年』。"""
    if ny >= 1:
        return f"{ny} 年"
    k = 1 - ny
    return "前一年" if k == 1 else f"前{k}年"


def to_new_calendar(g: date) -> dict:
    """
    公曆 → 新曆資訊：
      - display_year: 顯示用年份（不會出現 0 年）
      - n_year: 內部整數年號（可為 <=0）
      - n_month, n_day: 1..12 月各 30 天；年末日以 n_month=0, n_day=1..5/6
      - doy: 年內序日（1..360；年末 361..365/366）
      - is_ep: 是否年末日
    """
    ny, S, Sn = locate_new_year(g)
    doy = (g - S).days + 1
    year_len = (Sn - S).days  # 365 或 366

    if doy <= 360:
        n_month = (doy - 1) // 30 + 1
        n_day = (doy - 1) % 30 + 1
        is_ep = False
    else:
        n_month = 0
        n_day = doy - 360     # 1..5/6
        is_ep = True

    return dict(
        display_year=year_label(ny),
        n_year=ny,
        n_month=n_month,
        n_day=n_day,
        doy=doy,
        is_ep=is_ep,
        start=S,
        end=Sn,
        year_len=year_len,
    )


def start_of_year(ny: int) -> date:
    """由新曆年號（>=1）求該年的公曆起點；不允許 ny < 1。"""
    if ny < 1:
        raise ValueError("新曆年必須從 1 開始（不支援 0 或負年份輸入）。")
    S = EPOCH_START
    cur = EPOCH_YEAR
    while cur < ny:
        S = next_start(S)
        cur += 1
    return S


def to_gregorian(n_year: int, n_month: int, n_day: int) -> date:
    """
    新曆 → 公曆；僅支援 n_year >= 1。
    - 1..12 月各 30 天
    - 年末日：n_month = 0, n_day = 1..5/6（依該年長度而定）
    """
    S = start_of_year(n_year)
    Sn = next_start(S)
    year_len = (Sn - S).days
    max_ep = year_len - 360       # 5 或 6

    if n_month == 0:
        if not (1 <= n_day <= max_ep):
            raise ValueError(f"該年只有 {max_ep} 個年末日")
        offset = 360 + (n_day - 1)
    else:
        if not (1 <= n_month <= 12):
            raise ValueError("月份需介於 1..12（年末日請用月份 0）")
        if not (1 <= n_day <= 30):
            raise ValueError("每個月份僅有 30 天")
        offset = (n_month - 1) * 30 + (n_day - 1)

    return S + timedelta(days=offset)


def build_year_table(n_year: int) -> pd.DataFrame:
    """輸出新曆 n_year（>=1）全年對照表。"""
    S = start_of_year(n_year)
    Sn = next_start(S)
    rows = []
    for doy in range(1, (Sn - S).days + 1):
        if doy <= 360:
            n_month = (doy - 1) // 30 + 1
            n_day = (doy - 1) % 30 + 1
            is_ep = "否"
            label_m = n_month
        else:
            n_month = 0
            n_day = doy - 360
            is_ep = "是"
            label_m = "年末"
        g = S + timedelta(days=doy - 1)
        rows.append({
            "新曆年": n_year,
            "新曆月": label_m,
            "新曆日": n_day,
            "新曆序日": doy,
            "是否年末日": is_ep,
            "公曆日期": g.isoformat(),
        })
    return pd.DataFrame(rows)

# ======================
# 驗證輔助：期望規則 & 比對（含 ✅/❌）
# ======================


def expect_for_date(d: date) -> str:
    """
    僅對 3/1、8/17、8/22、8/23、2/28/2/29 定義期望字串。
    """
    Y = d.year
    if d.month == 3 and d.day == 1:
        return "應為 新曆 7/12"
    if d.month == 8 and d.day == 17:
        return "應為 年末日 第1天"
    if d.month == 8 and d.day == 22:
        return "若下一年閏：年末日第6天；否則：新曆 1/1"
    if d.month == 8 and d.day == 23:
        return "若下一年閏：新曆 1/1；否則：新曆 1/2"
    if d.month == 2 and d.day in (28, 29):
        if is_leap_year(Y):
            return "應為 新曆 7/11" if d.day == 29 else "應為 新曆 7/10（當年閏）"
        else:
            return "應為 新曆 7/11（當年平年）"
    return ""


def check_rule(d: date, out: dict) -> bool:
    """
    根據期望規則檢查（只檢 3/1、8/17、8/22、8/23、2/28/2/29）。
    """
    Y = d.year

    def is_new(m, n):  # 一般月份
        return (out["n_month"] == m and out["n_day"] == n and not out["is_ep"])

    def is_ep(n):      # 年末日第 n 天
        return (out["is_ep"] and out["n_day"] == n)

    if d.month == 3 and d.day == 1:
        return is_new(7, 12)
    if d.month == 8 and d.day == 17:
        return is_ep(1)
    if d.month == 8 and d.day == 22:
        return is_ep(6) if is_leap_year(Y + 1) else is_new(1, 1)
    if d.month == 8 and d.day == 23:
        return is_new(1, 1) if is_leap_year(Y + 1) else is_new(1, 2)
    if d.month == 2 and d.day in (28, 29):
        if is_leap_year(Y):
            return is_new(7, 11) if d.day == 29 else is_new(7, 10)
        else:
            return is_new(7, 11)
    return True


def pass_mark(ok: bool) -> str:
    return "✅" if ok else "❌"


# ======================
# Streamlit 介面
# ======================
st.set_page_config(page_title="新曆法 ↔ 公曆（修正版：Y+1 閏年規則）", layout="wide")
st.title("新曆法（12×30天＋年末 5/6 天）↔ 公曆 互動轉換")

with st.expander("📘 本版規則", expanded=False):
    st.markdown("""
- **新曆紀元**：1 年 1/1 = 公曆 **2023-08-23**；不使用「0 年」標示，紀元之前的日期顯示為「**新曆（前一年 / 前 X 年）**」。
- **年界線**（關鍵修正）：**公曆年 Y 的新曆 1/1 為 Y-08-23 若 (Y+1) 閏，否則為 Y-08-22**。
- **固定對齊**：公曆 **8/17 永遠是年末日第 1 天**；**3/1 永遠對應新曆 7/12**。
    """)

tab1, tab2, tab3 = st.tabs(["🔁 公曆 → 新曆", "🔁 新曆 → 公曆", "📚 批次驗證 / 下載"])

# ---- 公曆 → 新曆 ----
with tab1:
    st.subheader("公曆 → 新曆")
    g = st.date_input("選擇公曆日期", value=date(2023, 8, 23), format="YYYY-MM-DD")

    def fmt_result(gd: date) -> str:
        out = to_new_calendar(gd)
        ytxt = out["display_year"]
        if out["is_ep"]:
            return f"{gd.isoformat()} → 新曆（{ytxt}）年末日 第 {out['n_day']} 天（序日 {out['doy']}）"
        else:
            if out["n_year"] >= 1:
                return f"{gd.isoformat()} → 新曆 {ytxt} {out['n_month']}/{out['n_day']}（序日 {out['doy']}）"
            else:
                return f"{gd.isoformat()} → 新曆（{ytxt}）{out['n_month']}/{out['n_day']}（序日 {out['doy']}）"

    col_a, col_b = st.columns([1, 1])
    with col_a:
        if st.button("轉換為新曆", type="primary"):
            st.success(fmt_result(g))

    with col_b:
        st.caption("👇 一鍵驗證（基本關鍵日期）")
        if st.button("跑關鍵測試"):
            tests = [
                date(2023, 8, 16),
                date(2023, 8, 17),
                date(2023, 8, 22),
                date(2023, 8, 23),
                date(2024, 3, 1), date(2025, 3, 1), date(2026, 3, 1),
            ]
            for t in tests:
                st.write("• " + fmt_result(t))

# ---- 新曆 → 公曆 ----
with tab2:
    st.subheader("新曆 → 公曆（僅支援年 ≥ 1）")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        ny = st.number_input("新曆年（≥1）", value=1, min_value=1, step=1, format="%d")
    with col2:
        mode = st.radio("輸入模式", ["一般月份（1..12）", "年末日（月份 0）"], horizontal=True)
        if mode == "一般月份（1..12）":
            nm = st.number_input("新曆月", min_value=1, max_value=12, value=1, step=1)
            nd = st.number_input("新曆日", min_value=1, max_value=30, value=1, step=1)
        else:
            S = start_of_year(int(ny))
            Sn = next_start(S)
            max_ep = (Sn - S).days - 360
            nm = 0
            nd = st.number_input(f"年末日序（1..{max_ep}）", min_value=1, max_value=max_ep, value=1, step=1)

    if st.button("轉換為公曆", type="primary", key="to_g"):
        try:
            g2 = to_gregorian(int(ny), int(nm), int(nd))
            st.success(f"新曆 {int(ny)}/"
                       f"{('年末' if nm == 0 else int(nm))}/"
                       f"{int(nd)} ＝ 公曆 **{g2.isoformat()}**")
        except Exception as e:
            st.error(f"轉換失敗：{e}")

# ---- 批次驗證 / 下載 ----
with tab3:
    st.subheader("📚 2020–2026 年批次驗證（含 ✅/❌）")
    st.caption("檢查：3/1、8/17、8/22、8/23、以及 2/28 或 2/29（依該年閏否）。")
    if st.button("執行 2020–2026 批次驗證"):
        rows = []
        for Y in range(2020, 2027):
            dates = [
                date(Y, 3, 1),
                date(Y, 8, 17),
                date(Y, 8, 22),
                date(Y, 8, 23),
                date(Y, 2, 29) if is_leap_year(Y) else date(Y, 2, 28),
            ]
            for d in dates:
                out = to_new_calendar(d)
                # 實際
                actual = f"年末日 第{out['n_day']}天" if out["is_ep"] else f"{out['n_month']}/{out['n_day']}"
                # 期望 / 檢查
                expected = expect_for_date(d)
                ok = check_rule(d, out)
                rows.append({
                    "年份": d.year,
                    "公曆日期": d.isoformat(),
                    "期望": expected,
                    "實際": actual,
                    "結果": "✅" if ok else "❌",
                    "新曆序日": out["doy"],
                })
        df = pd.DataFrame(rows).sort_values(["年份", "公曆日期"]).reset_index(drop=True)
        st.dataframe(df, use_container_width=True, hide_index=True)
        csv = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button("下載 CSV（2020–2026 驗證）", data=csv,
                           file_name="new_calendar_verification_2020_2026.csv", mime="text/csv")

# Footer
st.caption("紀元：新曆 1 年 1/1 = 公曆 2023-08-23。年界線：Y 年的新曆 1/1 = Y-(8/23) 若 (Y+1) 閏，否則 = Y-(8/22)。8/17 永遠=年末1；3/1 永遠=7/12。")
