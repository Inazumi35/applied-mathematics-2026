---
name: applied-math
description: 石川高専・応用数学スライド作成スキル。「応用数学」「スライド」「week」「beamer」「yaml2beamer」「コンパイル」「lualatex」「解答追記」などのキーワードが出たら必ずこのスキルを参照する。YAML→Beamer変換パイプラインの操作・デバッグ・解答スライド追記に必要な情報をすべて含む。
version: 2.0.0
---

# 応用数学スライド作成スキル（oapmath）

## 作業フォルダ

```
C:\Users\inazumi\workspace\応用数学\
```

## 主要ファイル

| ファイル | 役割 |
|---------|------|
| `yaml2beamer_chapter.py` | YAML → Beamer フレーム変換コア |
| `yaml2beamer_week.py` | 週次スライド生成（chapter YAML を読み込み） |
| `chapter2_section1.yaml` | ラプラス変換（week01〜07） |
| `chapter2_section2.yaml` | たたみこみ・伝達関数（week05〜07） |
| `chapter3_section1.yaml` | フーリエ級数（week08〜11） |
| `chapter3_section2.yaml` | フーリエ変換（week12〜14） |
| `lecture/weekXX.tex` | 生成済み Beamer TeX |
| `lecture/weekXX.pdf` | コンパイル済み PDF |

## よく使うコマンド

```bash
# 全14週 tex 再生成
cd C:\Users\inazumi\workspace\応用数学
python yaml2beamer_week.py

# 特定週だけ再生成
python yaml2beamer_week.py --week 4,7,12

# コンパイル（1週）
cd lecture
lualatex -interaction=nonstopmode week07.tex

# 全14週コンパイル（Bash ループ）
cd C:\Users\inazumi\workspace\応用数学\lecture
for w in week01 week02 week03 week04 week05 week06 week07 week08 week09 week10 week11 week12 week13 week14; do
  lualatex -interaction=nonstopmode ${w}.tex > ${w}.log 2>&1
  echo "${w}: $?"
done

# エラー確認
grep "^!" lecture/week07.log | head -10
```

## スライド構成ルール

- **形式**：16:9 Beamer（handout オプションなし）
- **pause 不使用**
- **解答は別スライド**：演習問題フレームの後に区切りスライド（`build_separator_frame()`）→ 解答フレーム群（`build_exercise_answer_frames()`）
- 解答フレームのタイトル形式：`問1　解答`、`問13_演習　解答` など

## 14週スケジュール

| week | 章・節 | 内容 |
|------|-------|------|
| 01 | ch2-s1 sub1 | ラプラス変換の定義・基本公式 |
| 02 | ch2-s1 sub2 | ラプラス変換の性質 |
| 03 | ch2-s1 sub3 | 微分方程式への応用 |
| 04 | ch2-s1 sub4 + ch2-s2 sub1 | 逆ラプラス変換・伝達関数導入 |
| 05 | ch2-s2 sub1 | たたみこみ定理 |
| 06 | ch2-s2 sub2 | たたみこみ応用 |
| 07 | ch2-s2 sub2-3 | インパルス応答・伝達関数まとめ |
| 08 | ch3-s1 sub1 | フーリエ級数展開 |
| 09 | ch3-s1 sub2 | 奇関数・偶関数展開 |
| 10 | ch3-s1 sub3 | 複素フーリエ級数 |
| 11 | ch3-s1 sub4 | フーリエ級数まとめ・演習 |
| 12 | ch3-s2 sub1 | フーリエ変換の定義 |
| 13 | ch3-s2 sub2 | フーリエ変換の性質 |
| 14 | ch3-s2 sub3 | フーリエ変換まとめ・演習 |

## yaml2beamer_chapter.py — 重要な関数

```python
UMAP        # Unicode → LaTeX 変換テーブル（∴ → \therefore 含む）
MATH_IND    # 数式自動判定インジケータリスト
fmt(raw)    # YAML テキスト → LaTeX インライン変換
fmt_display(formula)  # \[ \] ディスプレイ数式
build_exercise_frame(exercises, title, skip_todo)   # 演習問題フレーム
build_exercise_answer_frames(exercises, skip_todo)  # 解答フレーム群
build_separator_frame(label)  # 「解説（試験前配布）」区切り
build_definition_frame(...)   # 定義フレーム
build_example_frame(ex, ...)  # 例題フレーム
assemble_subsection(sub, ...) # サブセクション全フレーム
```

## YAML の answer フィールド形式

```yaml
exercises:
  - id: 問1
    content: "問題文"
    answer:
      steps:
        - "ラプラス変換を取る: L[f'(t)] = sF(s) - f(0)"
        - "F(s) = 1/(s(s+1))"
      result: "f(t) = 1 - e^{-t}"
      # または複数答え:
      results:
        - "(1) f(t) = ..."
        - "(2) f(t) = ..."
      note: "注記（省略可）"
      graph_note: "グラフの説明（省略可）"
```

## 修正済みバグ一覧（2026-03-26）

| 症状 | 原因 | 修正箇所 |
|------|------|---------|
| `Missing $`（`∴`） | UMAP に `∴` 未登録 | UMAP に `'∴': r'\therefore'` 追加 |
| `Missing $`（`$\bigl($...`） | `fmt(sym)` が `$...$` を返し `$\bigl(...)$\bigr)$` で二重 `$` | `build_definition_frame` を `mfunc(u2l(sym))` に変更 |
| empty enumerate（week04） | `flow` が空でも `\begin{enumerate}` を生成 | `if flow:` ガードを追加 |
| `\\` 二重エスケープ（week04） | `tex_title()` を `build_exercise_answer_frames` と `frame_lines` で二重呼び出し | `frame_title = f'{ex_id}　解答'`（`tex_title` を除去） |
| `Missing $`（初期条件の `^{2}`） | Pattern B が注釈部分 `（...d^{2}x...）` を math 外に出す | Pattern B の注釈に `process_mixed(np_)` を適用 |

## 現在のステータス（2026-03-26）

- ✅ 全14週コンパイル成功（lualatex exit:0）
- ✅ 全14週 answer フィールド追記済み（chapter2_section1/2.yaml + chapter3_section1/2.yaml）
- ✅ カラー2バージョン生成：`--color` フラグで `weekXX_main.tex`（解説なし）・`weekXX_ans.tex`（解説あり）を生成
- ✅ サブセクション区切りフレーム：複数サブセクション時のみ表示（week01 冗長スライド解消）
- ⚠ 全14週 PDF 見た目確認（_main / _ans 両バージョン）未実施

## カラーバージョン生成コマンド

```bash
# 全14週カラー版生成（_main + _ans）
cd C:\Users\inazumi\workspace\応用数学
python yaml2beamer_week.py --color

# 特定週のみ
python yaml2beamer_week.py --color --week 8

# コンパイル（_main / _ans 両バージョン）
cd lecture
for w in week01 week02 week03 week04 week05 week06 week07 week08 week09 week10 week11 week12 week13 week14; do
  lualatex -interaction=nonstopmode ${w}_main.tex
  lualatex -interaction=nonstopmode ${w}_ans.tex
done
```

## 次のステップ

1. 全14週 PDF で見た目確認（_main / _ans 両バージョン）
2. （別タスク）kaken2026: `rd_pilot_2axis.pdf` を tex に挿入 → 最終コンパイル

## Git 管理

### リポジトリ
- ローカル：`C:\Users\inazumi\workspace\応用数学\`
- GitHub：`Inazumi35/applied-mathematics-2026`（**プライベート**）
- ブランチ：`master`

### .gitignore（除外ルール）
```
*.pdf          # 生成物
*.nav *.snm    # LaTeX 中間ファイル
*.log *.aux 等 # LaTeX ログ類
scan_pages/    # スキャン画像（大容量）
```

### よく使うコマンド
```bash
cd C:\Users\inazumi\workspace\応用数学

# 状態確認
git status

# YAML・スクリプト変更後にコミット
git add chapter2_section1.yaml yaml2beamer_chapter.py  # など変更ファイル
git commit -m "変更内容の説明"

# GitHub に push（GH_TOKEN は MEMORY.md 参照）
GH_TOKEN=<token> git -c credential.helper='!f(){ echo username=x-access-token; echo password=$GH_TOKEN; };f' push origin master
```

### ノート
- `skills/applied-math/SKILL.md` もこのリポジトリで管理（コミット対象）
- スキルを更新したら `git add skills/applied-math/SKILL.md && git commit` を忘れずに

## iCloud 写真スキャンのパス

```
C:\Users\inazumi\OneDrive\iCloud Photos\Photos\
```

HEIC → JPG 変換は `pillow-heif` を使用済み（111枚変換済み）。
教科書ページとファイル名の対応は写真を順に開いて確認する。
