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

瀏覽器將顯示三組工具：公曆轉新曆、新曆轉公曆，以及規則驗證／全年 CSV 匯出。

## 開發

安裝開發工具並執行所有檢查：

```bash
python -m pip install -e ".[dev]"
ruff check .
pytest
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
tests/                          邊界、規則與雙向轉換測試
AGENTS.md                       Codex／coding agent 開發指引
```

領域層不依賴 Streamlit 或 pandas，因此可以安全地用於腳本、其他介面或後續 API。`AGENTS.md` 記錄不可破壞的曆法規則與完成標準，方便新的 Codex 工作階段快速接手。

## 授權

本專案使用 MIT License，詳見 [LICENCE](LICENCE)。
