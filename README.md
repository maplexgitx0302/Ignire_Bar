# Ignire 新曆

Ignire 新曆由 12 個 30 天的月份組成，年末另有 5 或 6 個祭典日。本專案包含：

- **網頁**：今日新曆、公曆與新曆雙向轉換、月曆檢視、規則驗證與全年 CSV 匯出。
  👉 <https://maplexgitx0302.github.io/Ignire_Bar/>
- **iPhone 鎖定畫面 widget**：透過免費的 [Scriptable](https://apps.apple.com/app/scriptable/id1405459188) App 顯示今天的新曆日期，不需要 Apple 開發者帳號。

[Instagram](https://www.instagram.com/ignire.bar/)

## 曆法規則

- 新曆 1 年 1/1 是公曆 `2023-08-23`。
- 公曆 Y 年的新曆元旦：若 Y+1 是閏年則為 8/23，否則為 8/22。
- 因此公曆 3/1 固定對應新曆 7/12，公曆 8/17 固定是祭典第 1 天。
- 紀元以前的年份顯示為「前一年」、「前2年」⋯⋯，不使用「0 年」。
- 支援範圍：公曆 `0001-08-22` 至 `9999-08-22`（完整的新曆 -2021 至 7976 年）。

## 安裝 iPhone widget

1. 在 App Store 安裝 **Scriptable**。
2. 用 iPhone 打開[網頁](https://maplexgitx0302.github.io/Ignire_Bar/)，按「複製腳本」（或直接開啟 [`IgnireCalendar.js`](https://maplexgitx0302.github.io/Ignire_Bar/scriptable/IgnireCalendar.js) 全選複製）。
3. 打開 Scriptable，按右上角 **＋** 新增腳本，貼上後將名稱改為「Ignire 新曆」。
4. 長按鎖定畫面 →「自訂」→ 選鎖定畫面 → 點 widget 區域，加入 Scriptable 的 inline、圓形或長方形款式。
5. 點一下剛加入的 widget，在 **Script** 選擇「Ignire 新曆」。

主畫面的 Scriptable 小型 widget 也能使用。Widget 會在每天午夜後更新，實際時間由 iOS 決定，偶爾會晚幾分鐘。

## 專案結構

```text
docs/                      GitHub Pages 網站（純 HTML/CSS/JS，不需建置）
  ignire-calendar.js       曆法引擎（唯一的曆法邏輯來源）
  app.js                   網頁互動
  index.html, style.css    網頁
  scriptable/IgnireCalendar.js
                           產生的 Scriptable 腳本（內嵌曆法引擎）
scripts/
  scriptable-widget.js     Scriptable widget 原始碼
  build-scriptable.mjs     把曆法引擎嵌入 widget，產生上面的腳本
test/                      Node 內建測試
```

曆法引擎以整數日序（自 1970-01-01 起的天數）計算，不使用 JavaScript `Date` 做日期運算，因此不受時區或日光節約時間影響。

## 開發

需要 Node.js 20 以上，沒有任何 npm 相依套件。

```bash
npm test          # 檢查 Scriptable 腳本是否最新，並執行所有測試
npm run build     # 修改引擎或 widget 後重新產生 Scriptable 腳本
npm run serve     # 在 http://localhost:8000 預覽網頁（需要 Python 3）
```

測試涵蓋：

- 全部 3,651,695 個支援日期的雙向轉換，並與舊版 Python 引擎的結果雜湊比對（完全一致）。
- 手算的參考日期、逐年推算的年界線、每個公曆年份的固定對齊規則與錯誤輸入。
- 在模擬的 Scriptable 環境中執行 widget 腳本，檢查各款式顯示內容與午夜更新時間。

舊版 Streamlit（Python）與原生 iOS（Swift）實作保留在 git 歷史中，最後版本為 commit `d56e689`。

## 部署

GitHub Pages 設定為從 `main` 分支的 `/docs` 資料夾發布，push 後約一分鐘自動更新。

## 授權

本專案使用 MIT License，詳見 [LICENCE](LICENCE)。
