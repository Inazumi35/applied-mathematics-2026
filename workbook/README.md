# 応用数学 問題集パイプライン

## 概要

`applied_math_problems.yaml`（問題データ）から LaTeX 問題集（`kaitoushu.sty` 形式）を自動生成する。

## ファイル構成

```
workspace/応用数学/workbook/       ← 作業場所（git管理）
  generate_workbook.py             YAML→LaTeX 変換スクリプト
  fill_answers.py                  解答データ＋YAML更新スクリプト
  workbook_ch2.tex                 生成物: 2章 ラプラス変換（問74〜124）
  workbook_ch3.tex                 生成物: 3章 フーリエ解析（問140〜169）
  README.md                       このファイル

OneDrive/応用数学/2026/            ← コンパイル・配布用コピー
  （上記ファイル + kaitoushu.sty）

OneDrive/デスクトップ/
  applied_math_problems.yaml       元データ（82問）
```

## 作業フロー

```
workspace で編集 → OneDrive にコピー → git コミット
```

### 1. スクリプト・解答の編集（workspace）

`~/workspace/応用数学/workbook/` 内のファイルを直接編集する。

- `fill_answers.py` の `ANSWERS` 辞書に解答を追加・修正
- `generate_workbook.py` の出力形式を変更

### 2. 解答を YAML に反映（fill_answers.py）

```bash
cd ~/workspace/応用数学/workbook
python fill_answers.py
```

- `ANSWERS` 辞書（問題番号 → LaTeX解答文字列）から YAML を更新
- YAML の `answer: ""` を `answer: |` ブロック形式に置換
- バックアップ: 元ファイルを `.bak` として保存
- LaTeX の `\` を含むため、必ず `|` ブロックスカラーで書き出す

### 3. LaTeX 問題集の生成（generate_workbook.py）

```bash
cd ~/workspace/応用数学/workbook
python generate_workbook.py [yaml_path]
```

- 引数なしの場合、デフォルトパス（OneDrive/デスクトップ/applied_math_problems.yaml）を使用
- 出力: `workbook_ch2.tex`（2章）、`workbook_ch3.tex`（3章）
- 形式: A4・2段組み・`\mondai{番号}{問題文}` + `\kotae{解答}`
- Basic 問題には教科書参照 `\hfill {\scriptsize [教p.XX]}` 付き

### 4. OneDrive にコピー

```bash
cp ~/workspace/応用数学/workbook/{generate_workbook.py,fill_answers.py,workbook_ch2.tex,workbook_ch3.tex} \
   "$HOME/OneDrive - 独立行政法人 国立高等専門学校機構/応用数学/2026/"
```

### 5. PDF コンパイル（OneDrive 側）

```bash
cd "$HOME/OneDrive - 独立行政法人 国立高等専門学校機構/応用数学/2026"
lualatex workbook_ch2.tex
lualatex workbook_ch3.tex
```

- エンジン: LuaLaTeX（luatexja）
- `kaitoushu.sty` が同じディレクトリに必要

### 6. git コミット

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
| 2章 ラプラス変換 | Basic | 問74〜92 | 19問 |
| 2章 ラプラス変換 | Check | 問93〜124 | 28問（104,105欠番） |
| 3章 フーリエ解析 | Basic | 問140〜162 | 16問 |
| 3章 フーリエ解析 | Check | 問147〜169 | 19問 |
| **合計** | | | **82問** |

解答入力済み: 77問 / 82問
