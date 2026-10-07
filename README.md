# Ignire Calendar

Ignire Calendar 是一個以 Streamlit 製作的雙向曆法轉換器。新曆由 12 個 30 天的月份組成，年末另有 5 或 6 個祭典日。

[Instagram](https://www.instagram.com/ignire.bar/)

## 曆法規則

- 新曆 1 年 1/1 是公曆 `2023-08-23`。
- 公曆 Y 年的新曆元旦：若 Y+1 是閏年則為 8/23，否則為 8/22。
- 公曆 3/1 固定對應新曆 7/12。
- 公曆 8/17 固定對應祭典第 1 天。
- 程式只接受可以用 Python `date` 完整表示的新曆年；公曆有效範圍為 `0001-08-22` 至 `9999-08-22`。

## 安裝與執行

使用 Conda：

```bash
conda env create -f environment.yml
conda activate calendar-app
./run.sh
```

或使用一般 Python 虛擬環境：

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
./run.sh
```

瀏覽器頂端會顯示「今日新曆」（以台北時間計算），下方有四個分頁：公曆轉新曆、新曆轉公曆、月曆檢視，以及規則驗證／全年 CSV 匯出。

## 開發

安裝開發工具並執行所有檢查：

```bash
python -m pip install -e ".[dev]"
ruff check .
pytest
```

測試涵蓋手算的參考日期、與逐日推算版本的全範圍比對、所有公曆年份的固定對齊規則，以及以 Streamlit `AppTest` 執行的介面測試。

若要確認 iOS 的 Swift 引擎與 Python 引擎在全部 3,651,695 個支援日期上完全一致（需要 `swiftc`，約一分鐘）：

```bash
IGNIRE_SWIFT_PARITY=1 pytest tests/test_swift_parity.py
```

如果尚未安裝開發相依套件，核心測試仍可只用 Python 標準函式庫執行：

```bash
python -m unittest discover -v
```

## 專案結構

```text
calendar_app.py                 Streamlit 啟動入口
ignire_calendar/
  calendar.py                   純曆法領域邏輯
  verification.py               固定對齊規則驗證
  app.py                        Streamlit 使用者介面
tests/                          邊界、規則、雙向轉換、介面與 Swift 一致性測試
ios/                            SwiftUI app、鎖定畫面 widget 與 Swift 曆法引擎
ios/ParityTool/                 輸出 Swift 引擎全範圍結果的命令列工具
AGENTS.md                       Codex／coding agent 開發指引
```

領域層不依賴 Streamlit 或 pandas，因此可以安全地用於腳本、其他介面或後續 API。`AGENTS.md` 記錄不可破壞的曆法規則與完成標準，方便新的 Codex 工作階段快速接手。

## iPhone 鎖定畫面 Widget

`ios/IgnireCalendar.xcodeproj` 是獨立的 iOS 16+ SwiftUI app，內含 WidgetKit extension，可在鎖定畫面顯示今天的新曆日期。它支援 inline、circular 與 rectangular 三種 Lock Screen widget 版型，一次提供未來七天的午夜時間軸，因此即使系統延後重新載入也會準時換日。App 本身也提供今日新曆與雙向轉換。

在 macOS 以 Xcode 開啟專案：

```bash
open ios/IgnireCalendar.xcodeproj
```

在 **Signing & Capabilities** 選擇你的 Apple 開發團隊，並將預設 bundle identifier `com.ignire.calendar` 改為你擁有的唯一識別碼。接著選取 iOS 16+ 模擬器或已連接的 iPhone 執行 app，長按鎖定畫面後即可加入「今日新曆」widget。

核心 Swift 測試可在 Xcode 執行，或在已安裝完整 Xcode 的環境中使用：

```bash
xcodebuild -project ios/IgnireCalendar.xcodeproj -scheme IgnireCalendar -destination 'platform=iOS Simulator,name=iPhone 16' test
```

若 shell 仍指向 macOS Command Line Tools，可只在該指令前加上 `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer`，或將完整 Xcode 設為 active developer directory：

```bash
sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer
sudo xcodebuild -runFirstLaunch
```

## 授權

本專案使用 MIT License，詳見 [LICENCE](LICENCE)。
