#!/usr/bin/env python3
"""
yaml2beamer_chapter.py
chapter*.yaml → Beamer .tex ファイル生成スクリプト

使い方:
  python yaml2beamer_chapter.py chapter3_section1.yaml
  python yaml2beamer_chapter.py chapter3_section1.yaml -o lecture/ch3s1.tex
  python yaml2beamer_chapter.py chapter3_section1.yaml --include-todo
  python yaml2beamer_chapter.py chapter3_section1.yaml --slide

出力: lecture/<yamlファイル名>.tex（ハンドアウトモード）
"""

import yaml
import re
import sys
from pathlib import Path

# ── Unicode → LaTeX 変換テーブル（generate_weeks.py の UMAP を拡張）──
UMAP = {
    'ℒ': r'\mathcal{L}', 'ℱ': r'\mathcal{F}',
    '∫': r'\int', '∞': r'\infty', 'Σ': r'\sum', '√': r'\sqrt',
    '∂': r'\partial',
    'α': r'\alpha', 'β': r'\beta', 'γ': r'\gamma', 'δ': r'\delta',
    'ε': r'\varepsilon', 'θ': r'\theta', 'μ': r'\mu', 'ξ': r'\xi',
    'π': r'\pi', 'σ': r'\sigma', 'τ': r'\tau', 'φ': r'\varphi',
    'ω': r'\omega', 'λ': r'\lambda', 'ρ': r'\rho', 'ψ': r'\psi',
    '²': '^{2}', '³': '^{3}',
    '₀': '_{0}', '₁': '_{1}', '₂': '_{2}', '₃': '_{3}', '₄': '_{4}',
    '₅': '_{5}', '₆': '_{6}', '₇': '_{7}', '₈': '_{8}', '₉': '_{9}',
    'ₙ': '_{n}', 'ₘ': '_{m}', 'ₖ': '_{k}', 'ᵢ': '_{i}', 'ⱼ': '_{j}',
    'ₛ': '_{s}', 'ₜ': '_{t}', 'ₐ': '_{a}',
    '¹': '^{1}', '⁻': '^{-}',
    '≒': r'\approx', '≤': r'\leq', '≥': r'\geq', '≠': r'\neq',
    '·': r'\cdot', '×': r'\times', '∗': r'\ast', '∴': r'\therefore',
    '⟹': r'\Rightarrow', '⟺': r'\Leftrightarrow',
    '…': r'\ldots', '⋯': r'\cdots',
}

MFUNCS = [
    'sin', 'cos', 'tan', 'cot', 'sinh', 'cosh', 'tanh',
    'log', 'ln', 'exp', 'lim', 'arctan', 'arcsin', 'arccos',
    'Re', 'Im', 'det', 'ker',
]

JP_RE = re.compile(r'[\u3000-\u9fff\u3040-\u309f\u30a0-\u30ff]')
JP_SPLIT = re.compile(
    r'([\u3000-\u9fff\u3040-\u309f\u30a0-\u30ff\uff01-\uff5e（）「」『』・]+)'
)

MATH_IND = [
    '=', r'\mathcal', r'\int', r'\sum', r'\sqrt', r'\partial',
    r'\alpha', r'\beta', r'\omega', r'\delta', r'\pi',
    r'\tau', r'\mu', r'\sigma', r'\xi', r'\theta',
    r'\varepsilon', r'\varphi', r'\gamma', r'\infty', r'\lambda',
    '^{', '_{', r'\frac', r'\approx', r'\leq', r'\geq',
    r'\cdot', r'\times', r'\ast',
    'f(', 'g(', 'h(', 'x(', 'y(', 'F(', 'G(', 'H(',
    'X(', 'Y(', 'S(', "f'(", 'c(', 'e^',
    'L[', 'L^{', 'Z[',  # ラプラス・Z 変換記法
]

TODO_MARKER = '要確認'


# ── テキスト変換関数（generate_weeks.py から移植・拡張）──────────

def u2l(text: str) -> str:
    """Unicode 数学記号 → LaTeX コマンド"""
    for k, v in UMAP.items():
        text = text.replace(k, v)
    # ^{-}^{1} → ^{-1}（F⁻¹ などの修正）
    text = re.sub(r'\^\{-\}\^\{(\d+)\}', r'^{-\1}', text)
    # ^{-}1 → ^{-1}（e^{-}1t などの修正）
    text = re.sub(r'\^\{-\}(\d+)', r'^{-\1}', text)
    # \sqrt(xxx) → \sqrt{xxx}
    text = re.sub(r'\\sqrt\(([^)]+)\)', r'\\sqrt{\1}', text)
    # ギリシャ文字コマンドの後に直接アルファベットが続く場合にスペースを挿入
    _GCMDS = '|'.join([
        'alpha', 'beta', 'gamma', 'delta', 'varepsilon', 'theta',
        'mu', 'xi', 'pi', 'sigma', 'tau', 'varphi', 'omega',
        'lambda', 'rho', 'psi', 'infty', 'approx', 'leq', 'geq',
        'neq', 'to', 'partial', 'int', 'sum', 'sqrt', 'cdot',
    ])
    text = re.sub(
        r'(\\(?:' + _GCMDS + r'))([a-zA-Z])',
        lambda m: m.group(1) + ' ' + m.group(2),
        text,
    )
    return text


def mfunc(text: str) -> str:
    """sin/cos/... にバックスラッシュを付加
    注: 後ろを \b でなく (?![a-zA-Z]) にすることで
        lim_{...} や sin^2 など _ ^ { が続く場合にも対応する"""
    for f in MFUNCS:
        text = re.sub(r'(?<!\\)(?<![a-zA-Z])' + f + r'(?![a-zA-Z])', lambda m: '\\' + m.group(0), text)
    return text


def has_math(text: str) -> bool:
    return any(i in text for i in MATH_IND)


def has_jp(text: str) -> bool:
    return bool(JP_RE.search(text))


def process_mixed(text: str) -> str:
    """日本語＋数式混在テキストの処理"""
    parts = JP_SPLIT.split(text)
    result = []
    for p in parts:
        if not p or not p.strip():
            result.append(p)
        elif has_jp(p):
            result.append(p)
        else:
            seg = p.strip()
            seg = seg.replace('→', r' \to ')
            if has_math(seg) or r'\to' in seg:
                seg = mfunc(seg)
                result.append(f' ${seg}$ ')
            elif seg:
                result.append(f' {seg} ')
    out = ''.join(result)
    out = re.sub(r'\s{2,}', ' ', out).strip()
    out = re.sub(r'\$\s*\$', ' ', out)
    return out


def fmt(raw) -> str:
    """YAML テキスト → LaTeX インライン形式"""
    if raw is None:
        return ''
    text = u2l(str(raw))
    # 既に $...$ を含む場合は二重ラップせず mfunc のみ適用
    if '$' in text:
        return mfunc(text)

    # Pattern A: ラベル：数式
    if '：' in text:
        i = text.index('：')
        label = text[:i].strip()
        value = text[i + 1:].strip()
        if has_math(value) and not has_jp(value):
            return f"{label}：${mfunc(value.replace('→', r' \to '))}$"
        if has_math(value):
            return f"{label}：{process_mixed(value)}"
        return text.replace('→', r' $\to$ ')

    # Pattern B: 数式（注釈）
    m = re.match(r'^(.+?)（([^）]+)）$', text)
    if m:
        fp = m.group(1).strip()
        np_ = m.group(2).strip()
        if has_math(fp) and not has_jp(fp):
            note_tex = process_mixed(np_) if (has_math(np_) or has_jp(np_)) else np_
            return f"${mfunc(fp.replace('→', r' \to '))}$（{note_tex}）"

    # Pattern C: 純粋な数式（日本語なし）
    if not has_jp(text) and has_math(text):
        return f"${mfunc(text.replace('→', r' \to '))}$"

    # Pattern D: 混在 or テキスト
    if has_math(text) or '→' in text:
        return process_mixed(text)

    return text


def fmt_display(formula: str) -> str:
    r"""数式を \[ \] で囲んだ display math 形式で返す"""
    text = u2l(str(formula).strip())
    text = mfunc(text.replace('→', r' \to '))
    return f'  \\[\n    {text}\n  \\]'


def join_multiline_cases(text: str) -> str:
    """
    複数行にまたがる場合分け記法を1行に結合する。
    例:
      f(t) = { 0  (0 ≤ t < a)
             { 1  (a ≤ t < b)
             { 0  (b ≤ t)
    →  f(t) = { 0  (0 ≤ t < a),  1  (a ≤ t < b),  0  (b ≤ t) }
    """
    lines = text.split('\n')
    result = []
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        # 行末が (cond) で終わり、かつ次行が { で始まる → 複数行cases の開始
        if (re.search(r'=\s*\{[^}]+\([^)]+\)\s*$', s)
                and i + 1 < len(lines)
                and lines[i + 1].strip().startswith('{')):
            parts = [s]
            j = i + 1
            while j < len(lines) and lines[j].strip().startswith('{'):
                cont = lines[j].strip()[1:].strip()  # 先頭の { を除去
                parts.append(cont)
                j += 1
            result.append(parts[0] + ',  ' + ',  '.join(parts[1:]) + ' }')
            i = j
        else:
            result.append(lines[i])
            i += 1
    return '\n'.join(result)


def fmt_multiline(formulas: list) -> str:
    """複数行数式を align* 環境で返す"""
    lines = ['  \\begin{align*}']
    for f in formulas:
        text = u2l(str(f))
        text = mfunc(text.replace('→', r' \to '))
        # 最初の = を &= に変換（比較演算子 != >= <= は除外）
        text = re.sub(r'(?<![<>!&])=(?!=)', r'&=', text, count=1)
        lines.append(f'    {text} \\\\')
    if lines[-1].endswith(' \\\\'):
        lines[-1] = lines[-1][:-3]
    lines.append('  \\end{align*}')
    return '\n'.join(lines)


def convert_cases(text: str) -> str:
    r"""
    { val1 (cond1), val2 (cond2) } 形式を \begin{cases} 環境に変換。
    LaTeX の _{...} / ^{...} / \cmd{...} は変換しない。
    条件：{ ... } の直前が _ ^ \ でなく、内部に (cond) 形式の要素があること。
    """
    def is_cases_candidate(inner: str) -> bool:
        # 少なくとも (条件) 形式の要素が含まれること
        return bool(re.search(r'\(.+?\)', inner))

    def replace_cases(m):
        # { } の直前が _ ^ \ またはアルファベット（LaTeX コマンド末尾）なら変換しない
        start = m.start()
        if start > 0 and (text[start - 1] in ('_', '^', '\\')
                          or text[start - 1].isalpha()):
            return m.group(0)
        inner = m.group(1)
        if not is_cases_candidate(inner):
            return m.group(0)
        # カンマ区切り
        parts = re.split(r',\s*(?=[^()]*(?:\(|$))', inner)
        case_lines = []
        for part in parts:
            part = part.strip()
            cm = re.match(r'^(.+?)\s+\((.+)\)$', part)
            if cm:
                val = cm.group(1).strip()
                cond = cm.group(2).strip()
                case_lines.append(f'{val} & ({cond})')
            else:
                case_lines.append(part)
        return r'\begin{cases} ' + r' \\ '.join(case_lines) + r' \end{cases}'

    # text の各 { } を位置情報付きで処理するためにイテレータを使う
    result = re.sub(r'\{([^{}]+)\}', replace_cases, text)
    return result


def page_ref(page) -> str:
    """ページ参照: "76-77" → "p.\\,76--77" """
    if not page:
        return ''
    s = str(page).replace('-', '--')
    return f'p.\\,{s}'


def is_todo(text) -> bool:
    return TODO_MARKER in str(text) if text is not None else False


def tex_title(text) -> str:
    """フレームタイトル用エスケープ"""
    return str(text).replace('&', r'\&').replace('#', r'\#').replace('%', r'\%').replace('_', r'\_')


# ── フレーム行リスト生成ヘルパー ─────────────────────────────────

def frame_lines(title: str, body: list, options: str = '') -> list:
    """Beamer frame の行リストを返す（末尾に空行あり）"""
    opt = f'[{options}]' if options else ''
    return [
        f'\\begin{{frame}}{opt}{{{tex_title(title)}}}',
        *body,
        '\\end{frame}',
        '',
    ]


# ── フレームビルダ群 ──────────────────────────────────────────────

def build_section_title_frame(data: dict) -> list:
    ch = data.get('chapter', '')
    ch_title = data.get('chapter_title', '')
    sec = data.get('section', '')
    sec_title = data.get('section_title', '')
    pages = data.get('pages', '')
    title = f'第{ch}章 {ch_title}　{sec}節 {sec_title}'
    body = [
        r'  \begin{block}{本節の内容}',
        r'  \begin{itemize}',
    ]
    for sub in data.get('subsections', []):
        sub_title = sub.get('title', '')
        body.append(f'    \\item {sub_title}')
    body += [
        r'  \end{itemize}',
        r'  \end{block}',
    ]
    return frame_lines(title, body)


def build_definition_frame(defn: dict, page='') -> list:
    name = defn.get('name', '定義')
    title = f'定義：{name}'
    body = [r'  \begin{block}{}']

    cond = defn.get('condition', '')
    if cond and not is_todo(cond):
        for line in cond.strip().split('\n'):
            line = line.strip()
            if line:
                body.append(f'  {fmt(line)}\\\\[2pt]')

    formula = defn.get('formula', '')
    if formula and not is_todo(formula):
        body.append(fmt_display(formula))

    # forward / inverse 形式（フーリエ変換の定義など）
    for key, label in (('forward', 'フーリエ変換'), ('inverse', '逆フーリエ変換')):
        sub = defn.get(key, {})
        if isinstance(sub, dict) and sub:
            sym = sub.get('symbol', '')
            f = sub.get('formula', '')
            if sym:
                sym_tex = mfunc(u2l(str(sym)).replace('→', r' \to '))
                body.append(f'  \\medskip\\textbf{{{label}}}　$\\bigl({sym_tex}\\bigr)$：')
            if f and not is_todo(f):
                body.append(fmt_display(f))

    # note フィールド
    note = defn.get('note', '')
    if note and not is_todo(note):
        body.append(f'  {{\\footnotesize \\textcolor{{gray}}{{{fmt(note)}}}}}')

    # フーリエ係数などの内包フィールド（dict形式 or list形式に対応）
    fc = defn.get('fourier_coefficients', {})
    if isinstance(fc, list):
        # 直接リストの場合（例: section2 の definition.fourier_coefficients）
        if fc:
            body.append(r'  \medskip\textbf{フーリエ係数}：')
            body.append(fmt_multiline(fc))
    elif isinstance(fc, dict):
        fc_name = fc.get('name', '')
        fmls = fc.get('formulas', [])
        if fmls:
            if fc_name:
                body.append(f'  \\medskip\\textbf{{{fc_name}}}：')
            body.append(fmt_multiline(fmls))

    body.append(r'  \end{block}')
    if page:
        body.append(f'  \\vfill\\hfill{{\\scriptsize \\textcolor{{gray}}{{{page_ref(page)}}}}}')
    return frame_lines(title, body)


def build_formulas_frame(name: str, formulas: list, page='') -> list:
    body = [
        r'  \begin{block}{}',
        fmt_multiline(formulas),
        r'  \end{block}',
    ]
    if page:
        body.append(f'  \\vfill\\hfill{{\\scriptsize \\textcolor{{gray}}{{{page_ref(page)}}}}}')
    return frame_lines(name, body)


def build_theorem_frame(thm: dict, page='') -> list:
    name = thm.get('name', thm.get('title', '定理'))
    title = f'定理：{name}'
    body = [r'  \begin{block}{}']

    # 条件リスト
    conditions = thm.get('conditions', [])
    results = thm.get('results', [])
    if conditions:
        body.append(r'  \textbf{条件}：')
        body.append(r'  \begin{itemize}')
        for c in conditions:
            body.append(f'    \\item {fmt(c)}')
        body.append(r'  \end{itemize}')
    if results:
        body.append(r'  \textbf{結論}：')
        body.append(r'  \begin{itemize}')
        for r_ in results:
            body.append(f'    \\item {fmt(r_)}')
        body.append(r'  \end{itemize}')

    # 単一数式
    for key in ('formula', 'generalization', 'dual', 'inverse'):
        val = thm.get(key, '')
        if val and not is_todo(val):
            body.append(fmt_display(val))

    # フォーミュラリスト
    fmls = thm.get('formulas', [])
    if fmls:
        body.append(fmt_multiline(fmls))

    body.append(r'  \end{block}')
    if page:
        body.append(f'  \\vfill\\hfill{{\\scriptsize \\textcolor{{gray}}{{{page_ref(page)}}}}}')
    return frame_lines(title, body)


def build_properties_frame(properties: dict, page='') -> list:
    """フーリエ変換の性質リスト（I〜VI）"""
    title_str = properties.get('title', 'フーリエ変換の性質')
    items = properties.get('items', [])
    if not items:
        return []
    body = [r'  \begin{block}{}', r'  \begin{description}']
    for item in items:
        prop_id = item.get('id', '')
        name = item.get('name', '')
        formula = item.get('formula', '')
        if formula and not is_todo(formula):
            f_tex = f'${mfunc(u2l(formula))}$'
            body.append(f'    \\item[{prop_id}. {name}]\\mbox{{}}\\\\{f_tex}')
    body += [r'  \end{description}', r'  \end{block}']
    if page:
        body.append(f'  \\vfill\\hfill{{\\scriptsize \\textcolor{{gray}}{{{page_ref(page)}}}}}')
    return frame_lines(title_str, body)


def normalize_solution(solution) -> list:
    """solution フィールドを steps のリストに正規化"""
    if solution is None:
        return []
    if isinstance(solution, list):
        # [str, str, ...] or [{steps: [...]}, ...]
        steps = []
        for item in solution:
            if isinstance(item, str):
                steps.append(item)
            elif isinstance(item, dict):
                steps += item.get('steps', [])
        return steps
    if isinstance(solution, dict):
        return solution.get('steps', [])
    return [str(solution)]


def build_example_frame(ex: dict, skip_todo: bool = True) -> list:
    """例題フレーム（問題フレーム + 解答フレーム）"""
    ex_id = str(ex.get('id', '例題'))
    page = ex.get('page', '')
    problem = ex.get('problem', '')
    solution = ex.get('solution', {})
    result = ex.get('result', '')
    note = ex.get('note', '')

    if skip_todo and (is_todo(problem) or is_todo(str(solution))):
        return []

    pr = page_ref(page)
    title_prob = f'{ex_id}　（{pr}）' if pr else ex_id

    # ── 問題フレーム ──
    prob_body = [r'  \begin{exampleblock}{問題}']
    if problem and not is_todo(problem):
        problem_text = join_multiline_cases(str(problem).strip())
        for line in problem_text.split('\n'):
            line = line.strip()
            if line:
                prob_body.append(f'    {fmt(convert_cases(line))}\\\\[2pt]')
    else:
        prob_body.append('    （問題文は原本で確認）')
    prob_body.append(r'  \end{exampleblock}')

    # ── 解答フレーム（枠なし） ──
    steps = normalize_solution(solution)
    sol_body = []
    for step in steps:
        step_tex = fmt(convert_cases(str(step).strip()))
        sol_body.append(f'  {step_tex}\\\\[4pt]')
    # 末尾の改行余白を除去
    if sol_body:
        sol_body[-1] = sol_body[-1].replace('\\\\[4pt]', '')

    if result and not is_todo(result):
        res_tex = fmt(convert_cases(str(result)))
        sol_body.append(f'  \\medskip\\textbf{{答}}：{res_tex}')

    if note and not is_todo(note):
        sol_body.append(
            f'  {{\\footnotesize \\textcolor{{gray}}{{\\textit{{{fmt(str(note))}}}}}}}')

    return frame_lines(title_prob, prob_body) + frame_lines(f'{ex_id}　解答', sol_body)


def build_exercise_frame(exercises: list, title: str = '演習問題',
                         skip_todo: bool = True) -> list:
    """演習問題（問）フレーム"""
    items = []
    for ex in exercises:
        ex_id = str(ex.get('id', ''))
        content = ex.get('content', '')
        if skip_todo and is_todo(content):
            continue
        # 場合分け記法 { val (cond)\n{ val (cond) を1行に結合してから処理
        content = join_multiline_cases(str(content).strip())
        lines = [l.strip() for l in content.split('\n') if l.strip()]
        if not lines:
            continue
        items.append(f'    \\item[{tex_title(ex_id)}] {fmt(lines[0])}')
        for line in lines[1:]:
            items.append(f'    {fmt(line)}\\\\')

    if not items:
        return []

    body = [
        r'  \begin{exampleblock}{自分で解いてみよう}',
        r'  \begin{description}',
        *items,
        r'  \end{description}',
        r'  \end{exampleblock}',
    ]
    return frame_lines(title, body)


def build_practice_frame(practice: dict, skip_todo: bool = True) -> list:
    """練習問題フレーム"""
    p_id = practice.get('id', '練習問題')
    page = practice.get('page', '')
    problems = practice.get('problems', [])

    items = []
    for prob in problems:
        prob_id = str(prob.get('id', ''))
        content = prob.get('content', '')
        if skip_todo and is_todo(content):
            continue
        lines = [l.strip() for l in str(content).strip().split('\n') if l.strip()]
        if not lines:
            continue
        items.append(f'    \\item[問{prob_id}] {fmt(lines[0])}')
        for line in lines[1:]:
            items.append(f'    {fmt(line)}\\\\')

    if not items:
        return []

    pr = page_ref(page)
    title = f'{p_id}　（{pr}）' if pr else p_id
    body = [
        r'  \begin{block}{}',
        r'  \begin{description}',
        *items,
        r'  \end{description}',
        r'  \end{block}',
    ]
    return frame_lines(title, body)


def build_separator_frame(label: str = '解説（試験前配布）') -> list:
    """区切りスライド：ここから解説パート"""
    body = [
        r'  \vfill',
        r'  \begin{center}',
        r'  {\LARGE\bfseries\color{structure.fg} ' + label + r'}\\[1em]',
        r'  {\normalsize\textcolor{gray}{（試験前に Moodle で配布）}}',
        r'  \end{center}',
        r'  \vfill',
    ]
    return frame_lines(label, body)


def build_exercise_frame_group(exercises: list, skip_todo: bool = True) -> list:
    """例題直後に挿入する演習グループフレーム（問N・問M 形式のタイトル）"""
    valid = [ex for ex in exercises
             if not (skip_todo and is_todo(str(ex.get('content', ''))))]
    if not valid:
        return []
    title = '・'.join(str(ex.get('id', '')) for ex in valid)
    return build_exercise_frame(valid, title=title, skip_todo=skip_todo)


def build_property_frame_single(prop: dict) -> list:
    """単一性質（線形性等）のフレーム"""
    name = prop.get('name', '性質')
    formula = prop.get('formula', '')
    note = prop.get('note', '')
    body = []
    if formula:
        body.append(fmt_display(formula))
    if note:
        body.append(f'  {{\\small （{fmt(str(note))}）}}')
    return frame_lines(name, body)


def build_tool_frame_single(tool: dict) -> list:
    """数学的ツール（部分積分・ロピタル等）のフレーム"""
    name = tool.get('name', '')
    formula = tool.get('formula', '')
    note = tool.get('note', '')
    statement = tool.get('statement', '')
    application = tool.get('application', '')
    body = []
    if formula:
        body.append(fmt_display(formula))
        if note:
            body.append(f'  {{\\small {fmt(str(note))}}}')
    if statement:
        for line in statement.strip().split('\n'):
            line = line.strip()
            if line:
                body.append(f'  {fmt(line)}\\\\[2pt]')
    if application:
        body.append(r'  \medskip{\small \textbf{ラプラス変換での使用：}}\\[2pt]')
        for line in application.strip().split('\n'):
            line = line.strip()
            if line:
                body.append(f'  {{\\small {fmt(line)}}}\\\\[1pt]')
    return frame_lines(name, body)


def build_special_function_def_frame(sf: dict) -> list:
    """特殊関数（双曲線関数・単位ステップ関数等）の定義フレーム"""
    name = sf.get('name', '')
    body = []
    def math_line(text: str) -> str:
        """align* 内用：$...$を付けずに LaTeX 変換"""
        return mfunc(u2l(str(text)).replace('→', r' \to '))

    # 複数定義（dict形式: sinh/cosh 等）
    definitions = sf.get('definitions', {})
    if definitions:
        body.append(r'  \begin{align*}')
        items = list(definitions.values())
        for i, val in enumerate(items):
            sep = r' \\' if i < len(items) - 1 else ''
            body.append(f'    {math_line(val)}{sep}')
        body.append(r'  \end{align*}')
    # 単一定義（文字列形式）
    definition = sf.get('definition', '')
    if definition:
        defn_tex = math_line(definition)
        defn_tex = convert_cases(defn_tex)
        body.append(f'  \\[\n    {defn_tex}\n  \\]')
    graph_note = sf.get('graph_note', '')
    if graph_note:
        body.append(f'  $t = a$ で $0$ から $1$ に跳躍する階段状の関数')
    # ラプラス変換の結果（双曲線関数等）
    transforms = sf.get('transforms', [])
    if transforms:
        body.append(r'  \begin{block}{ラプラス変換}')
        body.append(r'  \begin{align*}')
        for i, t in enumerate(transforms):
            # 最初の = を &= に変換
            line = re.sub(r'(?<![<>!&])=(?!=)', '&=', math_line(t), count=1)
            sep = r' \\' if i < len(transforms) - 1 else ''
            body.append(f'    {line}{sep}')
        body.append(r'  \end{align*}')
        body.append(r'  \end{block}')
    return frame_lines(name, body)


def build_exercise_answer_frames(exercises: list, skip_todo: bool = True) -> list:
    """演習問題の解答スライド群を生成（answer フィールドが存在する問のみ）"""
    all_frames = []
    for ex in exercises:
        ex_id = str(ex.get('id', ''))
        answer = ex.get('answer')
        if not answer:
            continue
        content = ex.get('content', '')
        if skip_todo and is_todo(content):
            continue

        body = []

        # グラフの注記
        graph_note = answer.get('graph_note', '')
        if graph_note:
            body.append(f'  \\textbf{{グラフ：}}{fmt(graph_note)}\\\\[0.3em]')

        # 解法ステップ（枠なし）
        steps = answer.get('steps', [])
        for step in steps:
            body.append(f'  {fmt(str(step))}\\\\[4pt]')
        if steps:
            body[-1] = body[-1].replace('\\\\[4pt]', '')

        # 答え（単一 or 複数）
        result = answer.get('result', '')
        results = answer.get('results', [])
        if result:
            body.append(f'  \\medskip\\textbf{{答}}：{fmt(str(result).strip())}')
        elif results:
            body.append(r'  \medskip\textbf{答}：')
            for r_item in results:
                body.append(f'  {fmt(str(r_item))}\\\\')

        # 注記
        note = answer.get('note', '')
        if note:
            body.append(
                f'  {{\\footnotesize \\textcolor{{gray}}{{\\textit{{{fmt(str(note))}}}}}}}')

        frame_title = f'{ex_id}　解答'
        all_frames += frame_lines(frame_title, body)

    return all_frames


# ── セクションアセンブラ ─────────────────────────────────────────

def assemble_subsection(sub: dict, skip_todo: bool = True,
                        include_exercise_answers: bool = False) -> list:
    frames = []
    page = ''

    # 定義
    defn = sub.get('definition')
    if defn:
        frames += build_definition_frame(defn, page)

    # フーリエ係数（単独フィールド: definition 内にない場合）
    fc = sub.get('fourier_coefficients')
    if fc and not defn:
        name = fc.get('name', 'フーリエ係数')
        fmls = fc.get('formulas', [])
        if fmls:
            frames += build_formulas_frame(name, fmls, page)

    # 直交性
    orth = sub.get('orthogonality')
    if orth:
        frames += build_theorem_frame(orth, page)

    # 収束定理
    conv = sub.get('convergence_theorem')
    if conv:
        frames += build_theorem_frame(conv, page)

    # フーリエ積分定理
    fit = sub.get('fourier_integral_theorem')
    if fit:
        frames += build_theorem_frame(fit, page)

    # 偶関数/奇関数展開
    eo = sub.get('even_odd')
    if eo:
        for key in ('cosine_expansion', 'sine_expansion'):
            t = eo.get(key, {})
            if t:
                name = t.get('name', key)
                frames += build_theorem_frame(t, page)

    # 一般周期
    gp = sub.get('general_period')
    if gp:
        name = gp.get('name', '一般周期関数のフーリエ展開')
        formula = gp.get('formula', '')
        fc2 = gp.get('fourier_coefficients', [])
        body = [r'  \begin{block}{}']
        if formula and not is_todo(formula):
            body.append(fmt_display(formula))
        if fc2:
            body.append(fmt_multiline(fc2))
        body.append(r'  \end{block}')
        frames += frame_lines(name, body)

    # 余弦・サイン変換
    cst = sub.get('cosine_sine_transform')
    if cst:
        for key in ('cosine', 'sine'):
            t = cst.get(key, {})
            if t:
                name = t.get('name', key)
                body = [r'  \begin{block}{}']
                formula = t.get('formula', '')
                inv = t.get('inverse', '')
                if formula:
                    body.append(fmt_display(formula))
                if inv:
                    body.append(fmt_display(inv))
                if t.get('note', ''):
                    body.append(f'  {{\\footnotesize {fmt(t["note"])}}}')
                body.append(r'  \end{block}')
                frames += frame_lines(name, body)

    # 定理リスト
    for thm in sub.get('theorems', []):
        frames += build_theorem_frame(thm, page)

    # 性質リスト（dict形式：既存）
    props = sub.get('properties')
    if isinstance(props, dict) and props.get('items'):
        frames += build_properties_frame(props, page)

    # パーセバル
    parseval = sub.get('parseval_formula')
    if parseval:
        name = parseval.get('name', 'パーセバルの等式')
        formula = parseval.get('formula', '')
        body = [r'  \begin{block}{}']
        if formula:
            body.append(fmt_display(formula))
        body.append(r'  \end{block}')
        frames += frame_lines(name, body)

    # 解法手順（method フィールド）
    method = sub.get('method')
    if method:
        name = method.get('name', '解法手順')
        flow = method.get('flow', [])
        body = [r'  \begin{block}{}']
        if flow:
            body.append(r'  \begin{enumerate}[Step 1.]')
            for step in flow:
                action = step.get('action', '')
                result = step.get('result', '')
                if action:
                    body.append(f'    \\item {fmt(action)}')
                    if result:
                        body.append(f'    $\\Rightarrow$ {fmt(result)}\\\\')
            body.append(r'  \end{enumerate}')
        body.append(r'  \end{block}')
        frames += frame_lines(name, body)

    # ── 順序制御付き例題・演習 ──────────────────────────────────────
    examples  = sub.get('examples', [])
    exercises = sub.get('exercises', [])
    tools     = sub.get('mathematical_tools', [])
    sfs       = sub.get('special_functions', [])

    # list 形式の properties（position: after_definition）
    if isinstance(props, list):
        for prop in props:
            if prop.get('position') == 'after_definition':
                frames += build_property_frame_single(prop)

    # インデックス構築
    ex_by_target = {}     # after_example → [exercise, ...]
    for ex in exercises:
        key = ex.get('after_example')
        ex_by_target.setdefault(key, []).append(ex)

    tools_before = {}     # before_example → [tool, ...]
    for tool in tools:
        key = tool.get('before_example')
        tools_before.setdefault(key, []).append(tool)

    sf_after = {}         # after_example → [sf, ...]
    for sf in sfs:
        key = sf.get('after_example')
        sf_after.setdefault(key, []).append(sf)

    # 例題ループ
    for ex_item in examples:
        ex_id = str(ex_item.get('id', ''))

        # before ツール
        for tool in tools_before.get(ex_id, []):
            frames += build_tool_frame_single(tool)

        # 例題（問題＋解答）
        frames += build_example_frame(ex_item, skip_todo=skip_todo)

        # 例題直後の演習問題グループ
        group = ex_by_target.get(ex_id, [])
        if group:
            frames += build_exercise_frame_group(group, skip_todo)
            if include_exercise_answers:
                frames += build_exercise_answer_frames(group, skip_todo)

        # 例題直後の特殊関数（定義＋埋め込み例題）
        for sf in sf_after.get(ex_id, []):
            frames += build_special_function_def_frame(sf)
            sf_ex = sf.get('example')
            if sf_ex:
                frames += build_example_frame(sf_ex, skip_todo=skip_todo)
                sf_ex_id = str(sf_ex.get('id', ''))
                sf_group = ex_by_target.get(sf_ex_id, [])
                if sf_group:
                    frames += build_exercise_frame_group(sf_group, skip_todo)
                    if include_exercise_answers:
                        frames += build_exercise_answer_frames(sf_group, skip_todo)

    # after_example 未指定の演習（他の章との後方互換）
    ungrouped = ex_by_target.get(None, [])
    if ungrouped:
        frames += build_exercise_frame(ungrouped, title='演習問題', skip_todo=skip_todo)
        if include_exercise_answers:
            frames += build_exercise_answer_frames(ungrouped, skip_todo)

    return frames


def assemble_section(data: dict, skip_todo: bool = True) -> list:
    """セクション全体のフレーム行リストを生成"""
    all_frames = build_section_title_frame(data)

    for sub in data.get('subsections', []):
        sub_title = sub.get('title', '')
        sub_pages = sub.get('pages', '')
        # サブセクション区切りフレーム
        divider_body = [
            r'  \begin{block}{}',
            f'  {{\\large {sub_title}}}',
            r'  \end{block}',
        ]
        all_frames += frame_lines(sub_title, divider_body)
        all_frames += assemble_subsection(sub, skip_todo=skip_todo)

    practice = data.get('practice_problems')
    if practice:
        all_frames += build_practice_frame(practice, skip_todo=skip_todo)

    return all_frames


# ── TeX ファイル生成 ──────────────────────────────────────────────

def gen_tex(data: dict, skip_todo: bool = True, mode: str = 'handout') -> str:
    ch = data.get('chapter', 0)
    sec = data.get('section', 0)
    ch_title = data.get('chapter_title', '')
    sec_title = data.get('section_title', '')
    pages = data.get('pages', '')
    # 講義番号の概算（第2章→7回〜, 第3章→11回〜, 微調整可能）
    lecture_num = 6 + (ch - 2) * 4 + (sec - 1)

    if mode == 'slide':
        docclass = r'\documentclass[aspectratio=43,professionalfonts]{beamer}'
        slidemode_line = r'\newcommand{\slidemode}{1}'
    else:
        docclass = r'\documentclass[aspectratio=43,professionalfonts,handout]{beamer}'
        slidemode_line = ''

    header = ['% !TEX program = lualatex', docclass]
    if slidemode_line:
        header.append(slidemode_line)
    header += [
        r'\usepackage{beamer_template}',
        r'\usepackage{enumerate}',
        '',
        f'\\newcommand{{\\LectureNum}}{{{lecture_num}}}',
        f'\\newcommand{{\\LectureTitle}}{{第{ch}章 {ch_title}　{sec}節 {sec_title}}}',
        f'\\newcommand{{\\TextPages}}{{p.\\,{pages}}}',
        r'\newcommand{\CourseName}{応用数学}',
        r'\renewcommand{\TermName}{前期}',
        '',
        r'\begin{document}',
        '',
    ]

    frames = assemble_section(data, skip_todo=skip_todo)

    footer = ['', r'\end{document}', '']

    return '\n'.join(header) + '\n' + '\n'.join(frames) + '\n'.join(footer)


# ── メイン ───────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(
        description='chapter*.yaml → Beamer .tex ファイル生成',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument('yaml_file', help='入力 YAML ファイル（例: chapter3_section1.yaml）')
    parser.add_argument('-o', '--output', help='出力 .tex ファイルパス（省略時は lecture/<stem>.tex）')
    parser.add_argument('--include-todo', action='store_true',
                        help='「要確認」項目もフレームに含める（デフォルト: スキップ）')
    parser.add_argument('--slide', action='store_true',
                        help='スライドモード出力（デフォルト: ハンドアウトモード）')
    args = parser.parse_args()

    skip_todo = not args.include_todo
    mode = 'slide' if args.slide else 'handout'

    yaml_path = Path(args.yaml_file)
    if not yaml_path.exists():
        print(f'Error: {yaml_path} が見つかりません', file=sys.stderr)
        sys.exit(1)

    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    content = gen_tex(data, skip_todo=skip_todo, mode=mode)

    if args.output:
        out_path = Path(args.output)
    else:
        stem = yaml_path.stem
        suffix = '_slide' if mode == 'slide' else ''
        out_dir = yaml_path.parent / 'lecture'
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f'{stem}{suffix}.tex'

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f'Generated: {out_path}')
    # フレーム数を報告
    frame_count = content.count(r'\begin{frame}')
    print(f'  フレーム数: {frame_count}')


if __name__ == '__main__':
    main()
