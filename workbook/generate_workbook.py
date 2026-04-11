#!/usr/bin/env python3
"""
applied_math_problems.yaml から問題集 LaTeX ファイルを生成する。
kaitoushu.sty の mondai{番号}{問題文} 形式で出力。

出力ファイル:
  week01.tex 〜 week14.tex  授業回ごとの Basic 問題
  check_ch2.tex              2章 Check 問題
  check_ch3.tex              3章 Check 問題

使い方:
  python generate_workbook.py [yaml_path]
"""

import sys
import yaml
import os


# 授業回ごとの Basic 問題番号範囲
BASIC_GROUPS = [
    (1,  "2章", list(range(74, 81))),    # 74-80
    (2,  "2章", list(range(81, 86))),    # 81-85
    (3,  "2章", list(range(86, 90))),    # 86-89
    (4,  "2章", list(range(90, 93))),    # 90-92
    (5,  "2章", list(range(106, 110))),  # 106-109
    (6,  "2章", list(range(110, 115))),  # 110-114
    (7,  "2章", list(range(115, 118))),  # 115-117
    (8,  "3章", list(range(140, 142))),  # 140-141
    (9,  "3章", list(range(142, 143))),  # 142
    (10, "3章", list(range(143, 145))),  # 143-144
    (11, "3章", list(range(145, 147))),  # 145-146
    (12, "3章", list(range(152, 156))),  # 152-155
    (13, "3章", list(range(156, 161))),  # 156-160
    (14, "3章", list(range(161, 163))),  # 161-162
]

# Basic に含まれる全問題番号
ALL_BASIC_NOS = set(no for _, _, nos in BASIC_GROUPS for no in nos)


def escape_for_mondai(text: str) -> str:
    text = text.strip()
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text


def get_no(item):
    """問題番号を取得する。YAMLでは 'no' が boolean False に変換されるため対策。"""
    if "no" in item:
        return item["no"]
    if False in item:
        return item[False]
    return 0


def format_number_ranges(nos):
    """番号リストを '問93〜105, 118〜124' 形式に変換する。"""
    sorted_nos = sorted(set(nos))
    groups = []
    start = prev = sorted_nos[0]
    for n in sorted_nos[1:]:
        if n == prev + 1:
            prev = n
        else:
            groups.append((start, prev))
            start = prev = n
    groups.append((start, prev))
    parts = []
    for s, e in groups:
        parts.append(f"{s}" if s == e else f"{s}\u301c{e}")
    return "\u554f" + ", ".join(parts)


def has_answer(item):
    ans = item.get("answer", "")
    if isinstance(ans, list):
        return any(a for a in ans if isinstance(a, str) and a.strip())
    return isinstance(ans, str) and ans.strip() != ""


def format_answer(item) -> str:
    ans = item.get("answer", "")
    if isinstance(ans, list):
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


def format_problem(item, with_answer: bool = False) -> str:
    no = get_no(item)
    problem = escape_for_mondai(item["problem"])
    ref_line = ""
    if "ref" in item and item["ref"]:
        ref_line = f"\n\\hfill {{\\scriptsize [{item['ref']}]}}"
    result = f"\\mondai{{{no}}}{{\n{problem}{ref_line}\n}}\n"
    if with_answer and has_answer(item):
        result += "\n" + format_answer(item)
    return result


def make_header(problem_range_str):
    lines = []
    lines.append(r"% !TEX program = lualatex")
    lines.append(r"\documentclass[a4paper,10pt,twocolumn]{article}")
    lines.append(r"\usepackage{kaitoushu}")
    lines.append(r"\renewcommand{\baselinestretch}{1.2}")
    lines.append(r"\lhead{応用数学 問題集}")
    lines.append(f"\\problemrange{{{problem_range_str}}}")
    lines.append("")
    lines.append(r"\begin{document}")
    lines.append(r"\thispagestyle{fancy}")
    lines.append("")
    return lines


def build_problem_dict(data):
    """全問題を番号 → データ のdictに変換する。"""
    prob_dict = {}
    for ch_key in ["chapter2", "chapter3"]:
        ch = data.get(ch_key, {})
        for sec_key in ["basic", "check"]:
            for item in ch.get(sec_key, []):
                no = get_no(item)
                prob_dict[no] = item
    return prob_dict


def generate_week_tex(week, chapter_label, nos, prob_dict, with_answer: bool = False):
    """1授業回分の Basic 問題ファイルを生成する。"""
    items = [prob_dict[n] for n in nos if n in prob_dict]
    if not items:
        return None

    actual_nos = [get_no(it) for it in items]
    range_str = f"問{min(actual_nos)}〜{max(actual_nos)}" if len(actual_nos) > 1 else f"問{actual_nos[0]}"
    ans_label = "　解答" if with_answer else ""

    lines = make_header(range_str)
    lines.append(r"\begin{center}")
    lines.append(f"  {{\\Large \\textbf{{応用数学　{chapter_label}　第{week}回　Basic{ans_label}}}}}")
    lines.append(r"\end{center}")
    lines.append(r"\vspace{0.5em}")
    lines.append("")
    lines.append(r"\noindent\textbf{\large【Basic】}")
    lines.append(r"\vspace{0.3em}")
    lines.append("")
    for item in items:
        lines.append(format_problem(item, with_answer=with_answer))
    lines.append(r"\end{document}")
    return "\n".join(lines)


def generate_check_tex(chapter_key, chapter_data, chapter_label, prob_dict, with_answer: bool = False):
    """章単位の Check 問題ファイルを生成する。"""
    check_items = []
    for sec_key in ["basic", "check"]:
        for item in chapter_data.get(sec_key, []):
            no = get_no(item)
            if no not in ALL_BASIC_NOS:
                check_items.append(item)
    check_items.sort(key=get_no)

    if not check_items:
        return None

    actual_nos = [get_no(it) for it in check_items]
    range_str = format_number_ranges(actual_nos)
    ans_label = "　解答" if with_answer else ""

    lines = make_header(range_str)
    lines.append(r"\begin{center}")
    lines.append(f"  {{\\Large \\textbf{{応用数学　{chapter_label}　Check{ans_label}}}}}")
    lines.append(r"\end{center}")
    lines.append(r"\vspace{0.5em}")
    lines.append("")
    lines.append(r"\noindent\textbf{\large【Check】}")
    lines.append(r"\vspace{0.3em}")
    lines.append("")
    for item in check_items:
        lines.append(format_problem(item, with_answer=with_answer))
    lines.append(r"\end{document}")
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        yaml_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "applied_math_problems.yaml"
        )
    else:
        yaml_path = sys.argv[1]

    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    out_dir = os.path.dirname(os.path.abspath(__file__))
    prob_dict = build_problem_dict(data)

    # 授業回ごとの Basic ファイル（問題のみ・解答付き）
    for week, chapter_label, nos in BASIC_GROUPS:
        for with_answer, suffix in [(False, ""), (True, "_ans")]:
            tex = generate_week_tex(week, chapter_label, nos, prob_dict, with_answer=with_answer)
            if tex:
                fname = f"basic_week{week:02d}{suffix}.tex"
                out_path = os.path.join(out_dir, fname)
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(tex)
                print(f"Generated: {fname}")

    # Check ファイル（章単位・問題のみ・解答付き）
    for ch_key, ch_label, base in [
        ("chapter2", "2章", "check_ch2"),
        ("chapter3", "3章", "check_ch3"),
    ]:
        if ch_key in data:
            for with_answer, suffix in [(False, ""), (True, "_ans")]:
                tex = generate_check_tex(ch_key, data[ch_key], ch_label, prob_dict, with_answer=with_answer)
                if tex:
                    fname = f"{base}{suffix}.tex"
                    out_path = os.path.join(out_dir, fname)
                    with open(out_path, "w", encoding="utf-8") as f:
                        f.write(tex)
                    print(f"Generated: {fname}")

    print("Done.")


if __name__ == "__main__":
    main()
