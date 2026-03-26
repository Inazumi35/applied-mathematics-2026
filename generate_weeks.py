#!/usr/bin/env python3
"""
応用数学 全15回 Beamer スライド生成スクリプト
YAML → week01.tex 〜 week15.tex（スライド版・ハンドアウト版）
"""

import yaml
import re
import sys
from pathlib import Path

# ── Unicode → LaTeX 変換テーブル ──
UMAP = {
    'ℒ': r'\mathcal{L}', 'ℱ': r'\mathcal{F}',
    '∫': r'\int', '∞': r'\infty', 'Σ': r'\sum', '√': r'\sqrt',
    'α': r'\alpha', 'β': r'\beta', 'γ': r'\gamma', 'δ': r'\delta',
    'ε': r'\varepsilon', 'θ': r'\theta', 'μ': r'\mu', 'ξ': r'\xi',
    'π': r'\pi', 'σ': r'\sigma', 'τ': r'\tau', 'φ': r'\varphi',
    'ω': r'\omega',
    '²': '^{2}', '³': '^{3}',
    '₀': '_{0}', '₁': '_{1}', '₂': '_{2}', '₃': '_{3}', 'ₙ': '_{n}',
    '≒': r'\approx', '≤': r'\leq', '≥': r'\geq', '≠': r'\neq',
}

MFUNCS = ['sin', 'cos', 'tan', 'log', 'ln', 'exp', 'lim', 'arctan', 'arcsin', 'arccos']

JP_RE = re.compile(r'[\u3000-\u9fff\u3040-\u309f\u30a0-\u30ff]')
JP_SPLIT = re.compile(r'([\u3000-\u9fff\u3040-\u309f\u30a0-\u30ff\uff01-\uff5e（）「」『』・]+)')

MATH_IND = [
    '=', r'\mathcal', r'\int', r'\sum', r'\sqrt',
    r'\alpha', r'\beta', r'\omega', r'\delta', r'\pi',
    r'\tau', r'\mu', r'\sigma', r'\xi', r'\theta',
    r'\varepsilon', r'\varphi', r'\gamma', r'\infty',
    '^{', '_{', r'\frac', r'\approx', r'\leq', r'\geq',
    "f(", "g(", "h(", "x(", "y(", "F(", "G(", "H(",
    "X(", "Y(", "S(", "f'(", "c(", "e^",
]


def u2l(text):
    """Unicode 数学記号を LaTeX コマンドに変換"""
    for k, v in UMAP.items():
        text = text.replace(k, v)
    # \sqrt(xxx) → \sqrt{xxx}
    text = re.sub(r'\\sqrt\(([^)]+)\)', r'\\sqrt{\1}', text)
    # Greek letter commands followed by a letter need a space: \alphat → \alpha t
    _GCMDS = '|'.join([
        'alpha', 'beta', 'gamma', 'delta', 'varepsilon', 'theta',
        'mu', 'xi', 'pi', 'sigma', 'tau', 'varphi', 'omega',
        'infty', 'approx', 'leq', 'geq', 'neq', 'to',
        'int', 'sum', 'sqrt',
    ])
    text = re.sub(
        r'(\\(?:' + _GCMDS + r'))([a-zA-Z])',
        lambda m: m.group(1) + ' ' + m.group(2),
        text,
    )
    return text


def mfunc(text):
    """数学関数名にバックスラッシュ付加（math mode 用）"""
    for f in MFUNCS:
        text = re.sub(r'(?<!\\)\b' + f + r'\b', lambda m: '\\' + m.group(0), text)
    return text


def has_math(text):
    """テキストに数式が含まれるか判定"""
    return any(i in text for i in MATH_IND)


def has_jp(text):
    """テキストに日本語が含まれるか判定"""
    return bool(JP_RE.search(text))


def process_mixed(text):
    """日本語＋数式の混在テキストを処理（→ は分割後に変換）"""
    parts = JP_SPLIT.split(text)
    result = []
    for p in parts:
        if not p or not p.strip():
            result.append(p)
        elif has_jp(p):
            result.append(p)
        else:
            seg = p.strip()
            # → を \to に変換（math mode 内で使う）
            seg = seg.replace('→', r' \to ')
            if has_math(seg) or r'\to' in seg:
                seg = mfunc(seg)
                result.append(f' ${seg}$ ')
            elif seg:
                result.append(f' {seg} ')
    out = ''.join(result)
    out = re.sub(r'\s{2,}', ' ', out).strip()
    # 隣接する $...$ $...$ を結合: $ $ → 削除
    out = re.sub(r'\$\s*\$', ' ', out)
    return out


def fmt(raw):
    """YAML アイテムを LaTeX 形式に変換"""
    text = u2l(raw)

    # --- Pattern A: ラベル：数式 ---
    if '：' in text:
        i = text.index('：')
        label = text[:i].strip()
        value = text[i + 1:].strip()
        if has_math(value) and not has_jp(value):
            return f"{label}：${mfunc(value.replace('→', ' \\to '))}$"
        if has_math(value):
            return f"{label}：{process_mixed(value)}"
        return text.replace('→', ' $\\to$ ')

    # --- Pattern B: 数式（注釈） ---
    m = re.match(r'^(.+?)（([^）]+)）$', text)
    if m:
        fp = m.group(1).strip()
        np = m.group(2).strip()
        if has_math(fp) and not has_jp(fp):
            return f"${mfunc(fp.replace('→', ' \\to '))}$（{np}）"

    # --- Pattern C: 純粋な数式（日本語なし） ---
    if not has_jp(text) and has_math(text):
        return f"${mfunc(text.replace('→', ' \\to '))}$"

    # --- Pattern D: 混在 or テキスト ---
    if has_math(text) or '→' in text:
        return process_mixed(text)

    return text


def tex_escape_title(text):
    """フレームタイトル用のエスケープ"""
    return text.replace('&', r'\&').replace('#', r'\#').replace('%', r'\%')


def gen_frame(slide, week_data):
    """スライドデータから Beamer frame を生成"""
    stype = slide.get('type', 'content')
    title = tex_escape_title(slide.get('title', ''))
    items = slide.get('items', [])

    lines = []

    if stype == 'title':
        lines.append(
            r'\begin{frame}{\CourseName\quad 第\LectureNum 回「\LectureTitle」}')
        lines.append(
            r'  {\small \TermName\quad \TeacherName\quad ／\quad 教科書 \TextPages}')
        lines.append('')
        goal = week_data.get('goal', '')
        if goal:
            lines.append(f'  \\textbf{{目標}}：{goal}')
        lines.append('')
        if items:
            lines.append(r'  \begin{block}{概要}')
            lines.append(r'  \begin{itemize}')
            for item in items:
                lines.append(f'    \\item {fmt(item)}')
            lines.append(r'  \end{itemize}')
            lines.append(r'  \end{block}')
        lines.append(r'\end{frame}')

    elif stype == 'content':
        lines.append(f'\\begin{{frame}}{{{title}}}')
        if items:
            lines.append(r'  \begin{block}{}')
            lines.append(r'  \begin{itemize}')
            for item in items:
                lines.append(f'    \\item {fmt(item)}')
            lines.append(r'  \end{itemize}')
            lines.append(r'  \end{block}')
        lines.append(r'\end{frame}')

    elif stype == 'exercise':
        lines.append(f'\\begin{{frame}}{{{title}}}')
        if items:
            lines.append(r'  \begin{exampleblock}{自分で解いてみよう}')
            lines.append(r'  \begin{itemize}')
            for item in items:
                lines.append(f'    \\item {fmt(item)}')
            lines.append(r'  \end{itemize}')
            lines.append(r'  \end{exampleblock}')
        lines.append(r'\end{frame}')

    elif stype == 'summary':
        lines.append(f'\\begin{{frame}}{{{title}}}')
        if items:
            lines.append(r'  \begin{itemize}')
            for item in items:
                lines.append(f'    \\item {fmt(item)}')
            lines.append(r'  \end{itemize}')
        lines.append(r'\end{frame}')

    return '\n'.join(lines)


def gen_tex(week_data, mode='slide'):
    """1回分の完全な .tex ファイルを生成"""
    week = week_data['week']
    title = week_data['title']
    pages = str(week_data.get('pages', ''))

    slides = week_data.get('slide_structure', [])

    if mode == 'slide':
        docclass = r'\documentclass[aspectratio=43,professionalfonts]{beamer}'
        slidemode_line = r'\newcommand{\slidemode}{1}'
    else:
        docclass = r'\documentclass[aspectratio=43,professionalfonts,handout]{beamer}'
        slidemode_line = ''

    header = [r'% !TEX program = lualatex', docclass]
    if slidemode_line:
        header.append(slidemode_line)
    header += [
        r'\usepackage{beamer_template}',
        '',
        f'\\newcommand{{\\LectureNum}}{{{week}}}',
        f'\\newcommand{{\\LectureTitle}}{{{title}}}',
        f'\\newcommand{{\\TextPages}}{{p.\\,{pages}}}',
        r'\newcommand{\CourseName}{応用数学}',
        r'\renewcommand{\TermName}{前期}',
        '',
        r'\begin{document}',
        '',
    ]

    frames = []
    for slide in slides:
        frames.append(gen_frame(slide, week_data))

    footer = ['', r'\end{document}', '']

    return '\n'.join(header) + '\n' + '\n\n'.join(frames) + '\n' + '\n'.join(footer)


def main():
    yaml_path = sys.argv[1] if len(sys.argv) > 1 else 'applied_math_all_weeks.yaml'
    out_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('lecture')

    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    out_dir.mkdir(parents=True, exist_ok=True)

    weeks = data['weeks']

    for week_data in weeks:
        wn = week_data['week']
        for mode in ('slide', 'handout'):
            content = gen_tex(week_data, mode=mode)
            if mode == 'slide':
                filepath = out_dir / f'week{wn:02d}.tex'
            else:
                filepath = out_dir / f'week{wn:02d}_handout.tex'
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'  {filepath}')

    print(f'\nGenerated: {len(weeks) * 2} files ({len(weeks)} slide + {len(weeks)} handout)')


if __name__ == '__main__':
    main()
