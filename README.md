# 火與焰 · 新曆

火神教派「火與焰」的曆法：一年分為 12 個月，每月 30 日，共計 360 日；每年自聖日（公元 8 月 17 日）起有為期五至六日的祭典，祭典所用之日不計入曆法。本專案包含：

- **網頁**：今日新曆、公元與新曆雙向換算、月曆、規則驗證、全年 CSV 匯出，以及《火神信仰與祈禱手冊》。
  👉 <https://maplexgitx0302.github.io/Ignire_Bar/>
- **iPhone 鎖定畫面小工具**：透過免費的 [Scriptable](https://apps.apple.com/app/scriptable/id1405459188) App 顯示今日新曆，不需要 Apple 開發者帳號。
- **教義存檔**：[`doctrine/火神信仰與祈禱手冊.md`](doctrine/火神信仰與祈禱手冊.md)（教主提供的原文）。

[Instagram](https://www.instagram.com/ignire.bar/)

## 聖日與曆法

- **聖日**：每年公元 8 月 17 日，即祭典第 1 日，祭典首日點燃火柱。
- **曆法**：一年 12 個月，每月 30 日，共計 360 日。
- **祭典**：自聖日起計，為期五至六日，不計入曆法。
- **首日**：公元 8 月 22 日；祭典為六日之年（次一公元年為閏年），首日順延為 8 月 23 日。
- **紀元**：新曆 1 年首日為公元 `2023-08-23`；此前之年稱「前一年」、「前2年」⋯⋯，不稱「0 年」。
- 因此公元 3 月 1 日恆為新曆 7 月 12 日。
- 支援範圍：公元 `0001-08-22` 至 `9999-08-22`（完整的新曆 -2021 至 7976 年）。

## 安裝 iPhone 小工具

1. 在 App Store 安裝 **Scriptable**。
2. 用 iPhone 打開[網頁](https://maplexgitx0302.github.io/Ignire_Bar/)，按「複製腳本」（或直接開啟 [`IgnireCalendar.js`](https://maplexgitx0302.github.io/Ignire_Bar/scriptable/IgnireCalendar.js) 全選複製）。
3. 打開 Scriptable，按右上角 **＋** 新增腳本，貼上後將名稱改為「火與焰新曆」。
4. 長按鎖定畫面 →「自訂」→ 選鎖定畫面 → 點小工具區域，加入 Scriptable 的一行、圓形或長方形款式。
5. 點一下剛加入的小工具，在 **Script** 選擇「火與焰新曆」。
6. 在 **When Interacting** 選擇 **Open URL**，URL 填入 `https://maplexgitx0302.github.io/Ignire_Bar/`，之後點一下小工具就會開啟網頁。

主畫面的 Scriptable 小型小工具也能使用。小工具於每日午夜後更新，實際時間由 iOS 決定，偶爾會晚幾分鐘。

## 專案結構

```text
docs/                      GitHub Pages 網站（純 HTML/CSS/JS，不需建置）
  ignire-calendar.js       曆法引擎（唯一的曆法邏輯來源）
  app.js                   網頁互動
  index.html, style.css    曆法網頁
  handbook.html            《火神信仰與祈禱手冊》網頁
  crow.png, crow-128.png   標誌（自 design/hinokarasu.JPEG 去背的金色烏鴉）
  scriptable/IgnireCalendar.js
                           產生的 Scriptable 腳本（內嵌曆法引擎）
scripts/
  scriptable-widget.js     Scriptable widget 原始碼
  build.mjs                把曆法引擎嵌入 widget，並替網頁資源加上版本戳記
test/                      Node 內建測試
doctrine/                  教義原文存檔
design/hinokarasu.JPEG     標誌原檔
```

## 設計與用字

網頁與小工具的設計和用字以《火神信仰與祈禱手冊》為準：

- **標誌**：`design/hinokarasu.JPEG`，金色火焰構成的烏鴉。網頁使用去背版本，只放在焦黑底色上（頁首橫幅、手冊封面）。
- **配色**：焦黑（烏鴉的羽毛）與黃金（神像），火焰橘點綴；七彩只出現在線條末端，對應「唯有尾巴末端還保留著七彩的顏色」。
- **用字**：使用「公元」而非「公曆」；以「日」計（每月 30 日、祭典第 1 日）；公元 8/17 稱「聖日」；每年第一天稱「首日」；祭典期間稱「火柱長燃」；祭典之日不計入曆法，因此不顯示「本年第幾日」。
- **禱詞**：「火焰是淨化，火焰是祝福，火焰是重生。」

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

GitHub Pages 會讓瀏覽器快取每個檔案 10 分鐘（`cache-control: max-age=600`），且無法調整。因此：

- `npm run build` 會在 HTML 中的每個資源網址加上內容雜湊（如 `style.css?v=…`），確保新頁面一定搭配新的 CSS、JS 與圖片。
- `docs/update.js` 在開啟頁面或切回頁面時檢查 `version.json`；若網站已更新，會自動載入新版一次。

修改 `docs/` 內任何檔案後，請先執行 `npm run build` 再 commit（`npm test` 會檢查）。

## 授權

本專案使用 MIT License，詳見 [LICENCE](LICENCE)。
