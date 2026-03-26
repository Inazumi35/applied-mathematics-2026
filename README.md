# 応用数学（2026年度）

## 概要
- **対象**: 応用数学履修クラス
- **構成**: 前期・後期

## ファイル構成
```
応用数学/
├── topics_applied_math.yaml   # 授業トピック定義
├── generate_weeks.py          # TeXファイル生成スクリプト
├── lecture/                   # 各回のTeXファイル
│   ├── lecture_01.tex
│   └── ...
└── workbook/                  # 問題集
    ├── workbook_ch2.tex
    ├── workbook_ch3.tex
    ├── generate_workbook.py
    └── fill_answers.py
```

## 使い方
1. `topics_applied_math.yaml` を編集して授業内容を更新する
2. `generate_weeks.py` を実行してTeXファイルを生成する
3. TeXファイルをコンパイルしてPDFを作成する
