---
name: applied-math-workbook
description: |
  応用数学の問題集（workbook）パイプラインを管理するスキル。
  以下のような操作を求められたら必ずこのスキルを使うこと：
  - 「workbook」「問題集」に関する作業
  - 解答の追加・修正・反映
  - Basic/Check の PDF 生成・再生成
  - TeXファイルのコンパイル
  - 「応用数学の問題集を更新して」「解答を入れて」「PDFを作って」等
---

# 応用数学 Workbook スキル

## 作業ディレクトリ

```
~/workspace/応用数学/workbook/
```

## ファイル構成

| ファイル | 役割 |
|---|---|
| `applied_math_problems.yaml` | 問題・解答データ（77問）正規データ |
| `fill_answers.py` | ANSWERS辞書 → YAML に反映 |
| `generate_workbook.py` | YAML → LaTeX ファイル生成 |
| `kaitoushu.sty` | LaTeX スタイルファイル |

## 出力ファイル（32ファイル）

| ファイル名 | 内容 |
|---|---|
| `basic_week01〜14.tex/.pdf` | 授業回別 Basic（問題のみ） |
| `basic_week01〜14_ans.tex/.pdf` | 授業回別 Basic（解答付き） |
| `check_ch2.tex/.pdf` | 2章 Check（問題のみ） |
| `check_ch2_ans.tex/.pdf` | 2章 Check（解答付き） |
| `check_ch3.tex/.pdf` | 3章 Check（問題のみ） |
| `check_ch3_ans.tex/.pdf` | 3章 Check（解答付き） |

## Basic 授業回対応表

| 授業回 | 問題番号 | 章 |
|--------|---------|-----|
| 第1回 | 74〜80 | 2章 |
| 第2回 | 81〜85 | 2章 |
| 第3回 | 86〜89 | 2章 |
| 第4回 | 90〜92 | 2章 |
| 第5回 | 106〜109 | 2章 |
| 第6回 | 110〜114 | 2章 |
| 第7回 | 115〜117 | 2章 |
| 第8回 | 140〜141 | 3章 |
| 第9回 | 142 | 3章 |
| 第10回 | 143〜144 | 3章 |
| 第11回 | 145〜146 | 3章 |
| 第12回 | 152〜155 | 3章 |
| 第13回 | 156〜160 | 3章 |
| 第14回 | 161〜162 | 3章 |

## Check 問題

- 2章 Check：問93〜103, 118〜124
- 3章 Check：問147〜149, 163〜169

## 通常の更新フロー

解答を追加・修正したときは以下の順で実行する：

```bash
cd ~/workspace/応用数学/workbook

# 1. fill_answers.py の ANSWERS辞書を編集後、YAMLに反映
python fill_answers.py

# 2. LaTeX ファイルを再生成
python generate_workbook.py

# 3. 全PDF をコンパイル
for f in basic_week*.tex check*.tex; do
  lualatex --interaction=nonstopmode "$f" 2>&1 | grep -E "^!|Output written"
done
```

## 解答の追加方法

`fill_answers.py` の `ANSWERS` 辞書に問題番号をキーとして追記する。

```python
# 単一解答
123: r"$\mathcal{L}^{-1}[\cdots] = \cdots$",

# 小問あり（リスト）
90: [
    r"(1)の解答",
    r"(2)の解答",
    r"(3)の解答",
],
```

**注意点：**
- LaTeX の `\` を含むため必ず raw string `r"..."` を使う
- 複数行は文字列を `"\n\n"` で連結する
- PyYAML の `no` キー問題：問題番号の取得は `get_no()` で対策済み

## 解答検算の方針

解答を追加・修正する際は検算を行い、誤りを見つけたら修正する：

- **部分分数分解**：各極での留数を代入して係数を確認
- **逆ラプラス変換**：変換後の式に別の $s$ 値を代入して一致を確認
- **フーリエ係数**：不連続点や端点での級数収束値で確認
- **たたみ込み**：直接積分とラプラス変換の両方で計算して一致を確認

## git コミット

```bash
cd ~/workspace
git add 応用数学/workbook/
git commit -m "update workbook: <変更内容>"
```
