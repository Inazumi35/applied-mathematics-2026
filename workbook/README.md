# 応用数学 問題集パイプライン

## 概要

`applied_math_problems.yaml`（問題データ）から LaTeX 問題集（`kaitoushu.sty` 形式）を自動生成する。

## ファイル構成

```
workspace/応用数学/workbook/       ← すべてここで管理（git管理）
  applied_math_problems.yaml       元データ（77問）
  generate_workbook.py             YAML→LaTeX 変換スクリプト
  fill_answers.py                  解答データ＋YAML更新スクリプト
  kaitoushu.sty                    LaTeX スタイルファイル
  workbook_ch2.tex                 生成物: 2章 ラプラス変換（問74〜124）
  workbook_ch3.tex                 生成物: 3章 フーリエ解析（問140〜169）
  README.md                        このファイル
```

## 作業フロー

```
workspace で編集 → git コミット
```

### 1. 解答を YAML に反映（fill_answers.py）

```bash
cd ~/workspace/応用数学/workbook
python fill_answers.py
```

- `ANSWERS` 辞書（問題番号 → LaTeX解答文字列）から YAML を更新
- YAML の `answer: ""` を `answer: |` ブロック形式に置換
- バックアップ: 元ファイルを `.bak` として保存
- LaTeX の `\` を含むため、必ず `|` ブロックスカラーで書き出す

### 2. LaTeX 問題集の生成（generate_workbook.py）

```bash
cd ~/workspace/応用数学/workbook
python generate_workbook.py [yaml_path]
```

- 引数なしの場合、スクリプトと同じディレクトリの `applied_math_problems.yaml` を使用
- 出力: `workbook_ch2.tex`（2章）、`workbook_ch3.tex`（3章）
- 形式: A4・2段組み・`\mondai{番号}{問題文}` + `\kotae{解答}`
- Basic は授業回ごとに細分化（第1〜14回）、Check は章単位

### 3. PDF コンパイル

```bash
cd ~/workspace/応用数学/workbook
lualatex workbook_ch2.tex
lualatex workbook_ch3.tex
```

- エンジン: LuaLaTeX（luatexja）
- `kaitoushu.sty` が同じディレクトリに必要

### 4. git コミット

```bash
cd ~/workspace
git add 応用数学/workbook/
git commit -m "update workbook files"
```

## 注意事項

- **PyYAML の `no` 問題**: YAML の `no` キーは boolean `False` に変換される。`get_no()` で対策済み。
- **LaTeX エスケープ**: YAML 内の LaTeX 文字列は `|` ブロックスカラーで記述すること（`"` で囲むと `\` のエスケープ問題が発生する）。

## データ規模

| 章 | セクション | 問題番号 | 問数 |
|----|-----------|---------|------|
| 2章 ラプラス変換 | Basic | 問74〜92, 106〜117 | 31問 |
| 2章 ラプラス変換 | Check | 問93〜103, 118〜124 | 18問（104,105欠番） |
| 3章 フーリエ解析 | Basic | 問140〜146, 152〜162 | 18問（150,151欠番） |
| 3章 フーリエ解析 | Check | 問147〜149, 163〜169 | 10問 |
| **合計** | | | **77問** |

## Basic 授業回対応表

| 授業回 | 問題番号 | 章 |
|--------|---------|-----|
| 第1回  | 74〜80  | 2章 |
| 第2回  | 81〜85  | 2章 |
| 第3回  | 86〜89  | 2章 |
| 第4回  | 90〜92  | 2章 |
| 第5回  | 106〜109 | 2章 |
| 第6回  | 110〜114 | 2章 |
| 第7回  | 115〜117 | 2章 |
| 第8回  | 140〜141 | 3章 |
| 第9回  | 142      | 3章 |
| 第10回 | 143〜144 | 3章 |
| 第11回 | 145〜146 | 3章 |
| 第12回 | 152〜155 | 3章 |
| 第13回 | 156〜160 | 3章 |
| 第14回 | 161〜162 | 3章 |
