---
name: applied-math
description: 石川高専・応用数学スライド作成スキル。「応用数学」「スライド」「week」「beamer」「yaml2beamer」「コンパイル」「lualatex」「解答追記」「例題」「演習」「YAML」などのキーワードが出たら必ずこのスキルを参照する。YAML→Beamer変換パイプラインの操作・デバッグ・スライド生成・YAML編集に必要な情報をすべて含む。
version: 3.0.0
---

# 応用数学スライド作成スキル（oapmath）

## 作業フォルダ

```
C:\Users\inazumi\workspace\応用数学\
```

## ファイル構成

```
応用数学/
├── schedule.yaml              # 週→YAML→サブセクション マッピング（重要）
├── yaml2beamer_week.py        # 週次スライド生成（メイン入口）
├── yaml2beamer_chapter.py     # YAML→Beamer フレーム変換コア
├── gen_manual_frames.py       # 手動フレームファイル生成（manual/用）
├── chapter2_section1.yaml     # ラプラス変換（week01〜04）
├── chapter2_section2.yaml     # たたみこみ・伝達関数（week05〜07）
├── chapter3_section1.yaml     # フーリエ級数（week08〜11）
├── chapter3_section2.yaml     # フーリエ変換（week12〜14）
└── lecture/
    ├── weekXX_main.tex/pdf    # カラー版・問題のみ（解答なし）
    ├── weekXX_ans.tex/pdf     # カラー版・問題＋解答インライン
    ├── beamer_template.sty    # Beamer スタイル
    ├── math_macros.sty        # 数学マクロ
    └── manual/                # 手動管理フレームファイル
        └── week01_s1_*.tex    # 参照用手動フレーム（gen_manual_frames.py で生成）
```

> **注意**: `weekXX.tex`（handout版）・`lecture_XX.tex`（旧版）は廃止済み。

---

## よく使うコマンド

```bash
cd C:\Users\inazumi\workspace\応用数学

# 全14週カラー版生成（_main + _ans）
for w in $(seq 1 14); do python yaml2beamer_week.py --week $w --color; done

# 特定週のみ
python yaml2beamer_week.py --week 1 --color

# コンパイル（全14週 _main）
cd lecture
for w in 01 02 03 04 05 06 07 08 09 10 11 12 13 14; do
  lualatex -interaction=nonstopmode week${w}_main.tex
done

# コンパイル（全14週 _ans）
for w in 01 02 03 04 05 06 07 08 09 10 11 12 13 14; do
  lualatex -interaction=nonstopmode week${w}_ans.tex
done

# エラー確認
grep "^!" lecture/week01_main.log | head -10

# 手動フレームファイル生成（week01 subsection1）
python gen_manual_frames.py chapter2_section1.yaml --subsection 1 --week 1
```

---

## _main と _ans の違い

| ファイル | 内容 |
|---------|------|
| `weekXX_main.tex` | 例題（問題＋解答）＋演習問題（問題文のみ） |
| `weekXX_ans.tex`  | 例題（問題＋解答）＋演習問題（問題＋解答インライン） |

演習解答は `_ans` では各演習フレームの直後に挿入される（末尾まとめではない）。

---

## YAML フィールド：フレーム順序制御

week01 の subsection 1 で実装済み。他の週への適用は今後。

### exercises（演習問題）
```yaml
exercises:
  - id: 問1
    after_example: "例題2"    # この例題の直後に挿入
    content: "$L[t^2]$ を求めよ"
    answer:
      steps:
        - "L[t^{n}] = n!/s^{n+1} において n=2 とすると"
      result: "L[t^{2}] = 2/s^{3}  (s > 0)"
```

### mathematical_tools（数学的ツール）
```yaml
mathematical_tools:
  - name: 部分積分法
    before_example: "例題2"   # この例題の直前に挿入
    formula: "∫_a^b f(t)g'(t) dt = ..."
    note: "u = f(t), dv = g'(t)dt とおくと..."
```

### properties（性質）
```yaml
properties:
  - name: 線形性
    position: after_definition   # 定義フレームの直後に挿入
    formula: "L[c₁f₁(t) + c₂f₂(t)] = ..."
    note: "$c_1,\\, c_2$ は定数"
```

### special_functions（特殊関数）
```yaml
special_functions:
  - name: 双曲線関数
    after_example: "例題4"    # この例題の演習問題グループの後に挿入
    definitions:
      sinh: "sinh t = (e^t - e^{-t}) / 2"
      cosh: "cosh t = (e^t + e^{-t}) / 2"
    transforms:
      - "L[sinh t] = 1/(s²-1)  (s > 1)"

  - name: 単位ステップ関数
    after_example: "例題4"    # 双曲線関数の後（YAML 順）
    definition: "U(t-a) = { 1  (t ≥ a),  0  (t < a) }"
    graph_note: "t = a で 0 から 1 に跳躍"
    example:                  # 埋め込み例題（例題5）
      id: 例題5
      problem: "a ≥ 0 のとき U(t-a) のラプラス変換を求めよ"
      solution:
        - "F(s) = ∫ₐ^∞ e^{-st}dt = e^{-as}/s"
      result: "L[U(t-a)] = e^{-as}/s  (s > 0)"
```

> **ポイント**: `after_example` 未指定の演習問題は従来通り末尾に「演習問題」フレームとしてまとめられる（後方互換）。

---

## YAML の数式記法ルール

### すでに `$...$` が含まれる場合
`fmt()` は `$` を検出したら `mfunc()` のみ適用し、二重ラップしない。

```yaml
# OK: content に $...$ を書けば fmt() がそのまま通す
content: "$L[t^2]$ を線形性を用いて求めよ"

# OK: math 環境内フィールドは u2l+mfunc のみ（$なし）
definition: "U(t-a) = { 1  (t ≥ a),  0  (t < a) }"
```

### align* 環境内（definitions/transforms）
`$...$` を書かない。`build_special_function_def_frame` が `math_line()` で変換する。

```yaml
# OK（$なし）
definitions:
  sinh: "sinh t = (e^t - e^{-t}) / 2"
# NG（$あり → 二重になる）
# definitions:
#   sinh: "$\\sinh t = ...$"
```

---

## フレームスタイルルール

### 例題（build_example_frame）
- **問題フレーム**: `\begin{exampleblock}{問題}` あり
- **解答フレーム**: **枠なし**。ステップは `\\[4pt]` 区切りの plain テキスト。答えは `\medskip\textbf{答}：...`

```latex
\begin{frame}{例題2　解答}
  分部積分を用いると\\[4pt]
  $F(s) = \int_0^\infty e^{-st} t\,dt = \cdots$\\[4pt]
  よって $F(s) = 1/s^2$
  \medskip\textbf{答}：$L[t] = 1/s^2 \quad (s > 0)$
\end{frame}
```

### 演習問題（build_exercise_frame_group）
- `\begin{exampleblock}{自分で解いてみよう}` + `description` 環境
- タイトル：`問1・問2` など `・` 区切り

### 演習解答（build_exercise_answer_frames）
- **枠なし**。ステップは `\\[4pt]` 区切り。答えは `\medskip\textbf{答}：...`

---

## yaml2beamer_chapter.py — 重要な関数（最新）

```python
# テキスト変換
fmt(raw)                      # YAML テキスト→LaTeX。$があればmfuncのみ
fmt_display(formula)          # \[ \] display math
u2l(text)                     # Unicode数学記号→LaTeX
mfunc(text)                   # sin/cos等に\を付加
convert_cases(text)           # { val (cond) } → \begin{cases}

# フレーム生成
build_example_frame(ex, skip_todo)             # 例題（問題+解答、解答は枠なし）
build_exercise_frame(exercises, title, ...)    # 演習問題フレーム
build_exercise_frame_group(exercises, ...)     # 例題直後挿入用グループ
build_exercise_answer_frames(exercises, ...)   # 演習解答フレーム（枠なし）
build_property_frame_single(prop)              # 単一性質フレーム（線形性等）
build_tool_frame_single(tool)                  # 数学ツールフレーム
build_special_function_def_frame(sf)           # 特殊関数定義フレーム
build_separator_frame(label)                   # 区切りスライド

# アセンブラ
assemble_subsection(sub, skip_todo, include_exercise_answers)
# include_exercise_answers=True → 演習解答をインラインに挿入（color_ans用）
```

---

## schedule.yaml の構造

```yaml
weeks:
  - week: 1
    title: ラプラス変換の定義
    source: chapter2_section1.yaml
    subsections:
      - id: 1
        # include_after: manual/week01_extra.tex  # 手動フレーム追加（オプション）
```

---

## 現在のステータス（2026-04-04）

- ✅ 全14週 `_main` / `_ans` コンパイル成功
- ✅ week01 subsection1：`after_example` / `before_example` / `position` による順序制御実装済み
- ✅ 例題・演習解答フレーム：枠なしスタイルに統一
- ✅ `fmt()` の二重 `$` バグ修正済み
- ✅ `build_special_function_def_frame` の align* 内 `$` バグ修正済み
- ✅ 不要ファイル削除済み（旧 lecture_*.tex、week*.tex handout版、中間ファイル）
- ⚠ week02〜14 の exercises に `after_example` 未設定（現在は演習まとめて末尾）
- ⚠ 全14週 PDF 見た目確認未実施
- ⚠ 要目視：week08-09 問3(3)・問4(3)、week11 練習問題2(1)(2)・問4

---

## Git 管理

```bash
cd C:\Users\inazumi\workspace\応用数学

# 変更をコミット
git add chapter2_section1.yaml yaml2beamer_chapter.py yaml2beamer_week.py
git add schedule.yaml gen_manual_frames.py skills/applied-math/SKILL.md
git commit -m "変更内容の説明"

# GitHub に push
GH_TOKEN=<MEMORY.md参照> git -c credential.helper='!f(){ echo username=x-access-token; echo password=$GH_TOKEN; };f' push origin master
```

- リポジトリ：`Inazumi35/applied-mathematics-2026`（プライベート）
- `.gitignore`：`*.pdf` / `*.nav` / `*.snm` / `*.log` / `*.aux` / `scan_pages/` を除外

---

## スキャン画像パス

```
C:\Users\inazumi\workspace\応用数学\scan_pages\
```

教科書ページとファイル名の対応は画像を順に開いて確認する。
