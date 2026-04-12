# Lecture スライドの未解決イシュー

未対応の修正項目をここに集約する。対応したらチェックを入れる、または項目ごと削除する。

## week14（スペクトル）

### I-14-1. 例題番号の表記ゆれ

- ファイル: [week14_main.tex](week14_main.tex), [week14_ans.tex](week14_ans.tex)
- 該当: line 43, 60（`\begin{frame}{例2　（p.\,100）}`, `{例3　（p.\,101）}`）
- 内容: 他の週は `例題N` で統一しているが、week14 だけ `例N` になっている。番号も `例2`/`例3` から始まっており、`例題1` がない。
- 対応案:
  - (a) `例題1`/`例題2` にリナンバリング（章内通しで再採番）
  - (b) `例題N` の表記に揃えつつ番号は教科書に合わせて `例題2`/`例題3` のままにする
  - 教科書側の表記を確認してから決定する
- 関連: 問解答も対応する番号にする必要あり

### I-14-2. 「例2」問題定義の不連続点表現

- ファイル: [week14_main.tex:46](week14_main.tex#L46), [week14_ans.tex:46](week14_ans.tex#L46)
- 該当:
  ```
  f(x) = \begin{cases} 1 & (-1 < x < 1) \\ 1/2 & (x = 1, 3) \\ 0 & (1 < x < 3) \end{cases}
  ```
- 問題: 周期 4 の関数なので、不連続点は $x = \pm 1, \pm 3, \pm 5, \ldots$ すべて。`x = 1, 3` だけ書くのは中途半端。基本周期内の表示なら `x = 1` のみで足り、両端の扱いを明示すべき。
- 対応案: 教科書の書き方に合わせて、基本区間 $[-1, 3]$ 上で `x = 1` のみ書くか、すべての不連続点を `x = \pm 1, \pm 3, \ldots` と書く

### I-14-3. 連続スペクトル定義式の根拠

- ファイル: [week14_main.tex:34](week14_main.tex#L34), [week14_ans.tex:34](week14_ans.tex#L34)
- 該当: `S(\omega) = |F(\omega)| / \pi`
- 問題: フーリエ変換の定義（係数 $1/(2\pi)$ の置き方）次第で式が変わる。教科書のフーリエ変換の規約を確認し、整合させる必要がある。脚注で導出が説明されているがやや唐突。
- 対応案: 教科書のフーリエ変換定義（week12 で導入）の規約と一致しているか再確認

### I-14-4. 線スペクトル答の場合分け表記

- ファイル: [week14_main.tex:57](week14_main.tex#L57), [week14_ans.tex:57](week14_ans.tex#L57)
- 該当:
  ```
  $|c_{0}| = 1/2,\ |c_{n}| = 1/(|n|\pi)$ （ $n=\pm 1,\pm 3,\ldots$ ）, $0$ （ $n=\pm 2,\pm 4,\ldots$ ）
  ```
- 問題: 複数項を `,` で並べていて読みにくい。通常は cases 環境で書くと整理される。
- 対応案: `\begin{cases}` か、改行で 3 行に分けて書く

## 章末練習問題（採点用）

章末練習問題（教科書の「練習問題1/2」）は [practice/](practice/) サブディレクトリで workbook 形式に統一して管理する。
weekNN ファイルからは練習問題フレームを削除済み（学生用配布は別途）。

- [practice/practice_ch2_s1.tex](practice/practice_ch2_s1.tex) — 第2章 §1 練習問題1（p.\,61）✅
- [practice/practice_ch2_s2.tex](practice/practice_ch2_s2.tex) — 第2章 §2 練習問題2（p.\,72）✅
- [practice/practice_ch3_s1.tex](practice/practice_ch3_s1.tex) — 第3章 §1 練習問題1（p.\,90）✅
- [practice/practice_ch3_s2.tex](practice/practice_ch3_s2.tex) — 第3章 §2 練習問題2（p.\,104）✅

## 他の週の保留事項

### I-12-1 / I-13-1. フーリエ変換の実部極限の表現

- ファイル: [week12_main.tex](week12_main.tex), [week13_main.tex](week13_main.tex) 等
- 内容: SKILL.md §3 にあるとおり、$\lim_{x\to\pm\infty} e^{(1-iu)x}$ のような形を一括 `\to 0` と書いていないか確認が必要（要調査）

### I-09〜11-1. フーリエ級数の冗長条件

- ファイル: [week09_main.tex](week09_main.tex)〜[week11_main.tex](week11_main.tex)
- 内容: SKILL.md §5 に従い、「区分的に滑らか」と「区分的に連続」を両方書いていないか確認（要調査）

### I-14-7. 例題番号と例題N表記の統一（B1再掲）

- 上記 I-14-1 と統合
