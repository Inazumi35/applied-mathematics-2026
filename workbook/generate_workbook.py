#!/usr/bin/env python3
"""
applied_math_problems.yaml から問題集 LaTeX ファイルを生成する。
kaitoushu.sty の mondai{番号}{問題文} 形式で出力。

使い方:
  python generate_workbook.py <yaml_path>

出力先: 同じディレクトリに workbook_ch2.tex, workbook_ch3.tex を生成
"""

import sys
import yaml
import os
import re


def escape_for_mondai(text: str) -> str:
    """YAML中のLaTeX文字列をmondaiコマンド内で安全に使えるよう整形する。"""
    text = text.strip()
    # 複数行テキストの改行を適切に処理
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text


def format_parts(parts_list):
    """小問リストを enumerate 環境で整形する。"""
    lines = []
    lines.append(r"\begin{enumerate}")
    for part in parts_list:
        part_text = part.strip()
        lines.append(f"  \\item {part_text}")
    lines.append(r"\end{enumerate}")
    return "\n".join(lines)


def get_no(item):
    """問題番号を取得する。YAMLでは 'no' が boolean False に変換されるため対策。"""
    if "no" in item:
        return item["no"]
    if False in item:
        return item[False]
    return 0


def has_answer(item):
    """解答が入力されているか判定する。"""
    ans = item.get("answer", "")
    if isinstance(ans, list):
        return any(a for a in ans if isinstance(a, str) and a.strip())
    return isinstance(ans, str) and ans.strip() != ""


def format_answer(item) -> str:
    r"""解答部分の \kotae{} ブロックを生成する。"""
    ans = item.get("answer", "")
    if isinstance(ans, list):
        # 小問ごとの解答
        parts = []
        for i, a in enumerate(ans):
            if isinstance(a, str) and a.strip():
                parts.append(f"({i+1}) {a.strip()}")
        if not parts:
            return ""
        body = "\n\n".join(parts)
    else:
        body = ans.strip()
    if not body:
        return ""
    return f"\\kotae{{\n{body}\n}}\n"


def format_problem(item) -> str:
    r"""1問分の \mondai{}{} + \kotae{}{} ブロックを生成する。"""
    no = get_no(item)
    problem = escape_for_mondai(item["problem"])

    # 問題文をそのまま使用（YAML内に完全なLaTeX数式が含まれている）
    body = problem

    # ref があれば小さく表示
    ref_line = ""
    if "ref" in item and item["ref"]:
        ref_line = f"\n\\hfill {{\\scriptsize [{item['ref']}]}}"

    result = f"\\mondai{{{no}}}{{\n{body}{ref_line}\n}}\n"

    # 解答があれば追加
    if has_answer(item):
        result += "\n" + format_answer(item)

    return result


def generate_chapter_tex(chapter_key, chapter_data, header_title, problem_range_str):
    """1章分の .tex ファイル内容を生成する。"""
    lines = []
    lines.append(r"% !TEX program = lualatex")
    lines.append(r"\documentclass[a4paper,10pt,twocolumn]{article}")
    lines.append(r"\usepackage{kaitoushu}")
    lines.append(r"\renewcommand{\baselinestretch}{1.2}")
    lines.append(f"\\lhead{{応用数学 問題集・解答}}")
    lines.append(f"\\problemrange{{{problem_range_str}}}")
    lines.append("")
    lines.append(r"\begin{document}")
    lines.append(r"\thispagestyle{fancy}")
    lines.append("")

    # 章タイトル
    title = chapter_data.get("title", "")
    lines.append(f"\\begin{{center}}")
    lines.append(f"  {{\\Large \\textbf{{{header_title}　{title}}}}}")
    lines.append(f"\\end{{center}}")
    lines.append(r"\vspace{0.5em}")
    lines.append("")

    # Basic セクション
    if "basic" in chapter_data and chapter_data["basic"]:
        lines.append(r"% ===== Basic =====")
        lines.append(r"\noindent\textbf{\large【Basic】}")
        lines.append(r"\vspace{0.3em}")
        lines.append("")
        for item in chapter_data["basic"]:
            lines.append(format_problem(item))

    # Check セクション
    if "check" in chapter_data and chapter_data["check"]:
        lines.append(r"% ===== Check =====")
        lines.append(r"\vspace{1em}")
        lines.append(r"\noindent\textbf{\large【Check】}")
        lines.append(r"\vspace{0.3em}")
        lines.append("")
        for item in chapter_data["check"]:
            lines.append(format_problem(item))

    lines.append(r"\end{document}")
    return "\n".join(lines)


def get_problem_range(chapter_data):
    """章内の問題番号の範囲を取得する。"""
    numbers = []
    for section in ["basic", "check"]:
        if section in chapter_data and chapter_data[section]:
            for item in chapter_data[section]:
                numbers.append(get_no(item))
    if numbers:
        return min(numbers), max(numbers)
    return 0, 0


def main():
    if len(sys.argv) < 2:
        # デフォルトパス
        yaml_path = os.path.join(
            os.path.expanduser("~"),
            "OneDrive - 独立行政法人 国立高等専門学校機構",
            "デスクトップ",
            "applied_math_problems.yaml"
        )
    else:
        yaml_path = sys.argv[1]

    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # 出力先ディレクトリ（このスクリプトと同じ場所）
    out_dir = os.path.dirname(os.path.abspath(__file__))

    # 2章: ラプラス変換
    if "chapter2" in data:
        ch2 = data["chapter2"]
        lo, hi = get_problem_range(ch2)
        tex = generate_chapter_tex(
            "chapter2", ch2,
            "2章", f"問{lo}〜{hi}"
        )
        out_path = os.path.join(out_dir, "workbook_ch2.tex")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(tex)
        print(f"Generated: {out_path}")

    # 3章: フーリエ解析
    if "chapter3" in data:
        ch3 = data["chapter3"]
        lo, hi = get_problem_range(ch3)
        tex = generate_chapter_tex(
            "chapter3", ch3,
            "3章", f"問{lo}〜{hi}"
        )
        out_path = os.path.join(out_dir, "workbook_ch3.tex")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(tex)
        print(f"Generated: {out_path}")

    print("Done.")


if __name__ == "__main__":
    main()
