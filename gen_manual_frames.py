#!/usr/bin/env python3
"""
gen_manual_frames.py
chapter YAML の orphaned fields（properties, mathematical_tools, special_functions, exercises）
から手動フレーム .tex ファイルを生成する。

使い方:
  python gen_manual_frames.py chapter2_section1.yaml --subsection 1 --week 1
  python gen_manual_frames.py chapter2_section1.yaml --subsection 1 --week 1 --list

出力: lecture/manual/week{N}_*.tex
"""

import yaml
import re
import sys
import argparse
from pathlib import Path

# ── yaml2beamer_chapter から共通変換関数を借用 ──────────────────
_here = Path(__file__).parent
sys.path.insert(0, str(_here))
from yaml2beamer_chapter import u2l, mfunc, fmt_display, frame_lines, convert_cases


# ASCII ファイル名マッピング
_NAME_MAP = {
    '部分積分法':       'ibp',
    'ロピタルの定理':   'lhopital',
    '双曲線関数':       'hyperbolic',
    '単位ステップ関数': 'unit_step',
}

def ascii_name(name: str) -> str:
    return _NAME_MAP.get(name, re.sub(r'[^\w]', '_', name))


# ── ヘルパー ────────────────────────────────────────────────────

def fmt(text: str) -> str:
    """テキストを LaTeX 用に変換"""
    text = u2l(str(text))
    text = text.replace('→', r' $\to$ ')
    return mfunc(text)


def write_frame(title: str, body_lines: list, out_path: Path) -> None:
    lines = frame_lines(title, body_lines)
    out_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'  Written: {out_path}')


# ── フレームビルダー ─────────────────────────────────────────────

def build_linearity(properties: list, out_dir: Path, prefix: str) -> Path:
    """線形性フレーム"""
    prop = next((p for p in properties if '線形' in p.get('name', '')), None)
    if not prop:
        return None
    body = [fmt_display(prop['formula'])]
    note = prop.get('note', '')
    if note:
        body.append(f'  {{\\small （{fmt(note)}）}}')
    path = out_dir / f'{prefix}_linearity.tex'
    write_frame('線形性', body, path)
    return path


def build_tools(tools: list, out_dir: Path, prefix: str) -> list:
    """部分積分法・ロピタルの定理フレーム（個別ファイル）"""
    paths = []
    for tool in tools:
        name = tool.get('name', '')
        safe = ascii_name(name)
        body = []

        formula = tool.get('formula', '')
        if formula:
            body.append(fmt_display(formula))

        statement = tool.get('statement', '')
        if statement:
            for line in statement.strip().split('\n'):
                line = line.strip()
                if line:
                    body.append(f'  {fmt(line)}\\\\[2pt]')

        application = tool.get('application', '')
        if application:
            body.append(r'  \medskip{\small \textbf{ラプラス変換での使用：}}\\[2pt]')
            for line in application.strip().split('\n'):
                line = line.strip()
                if line:
                    body.append(f'  {{\\small {fmt(line)}}}\\\\[1pt]')

        note = tool.get('note', '')
        if note:
            body.append(f'  {{\\small {fmt(note)}}}')

        path = out_dir / f'{prefix}_tool_{safe}.tex'
        write_frame(name, body, path)
        paths.append(path)
    return paths


def build_special_functions(sfs: list, out_dir: Path, prefix: str) -> list:
    """双曲線関数・単位ステップ関数フレーム"""
    paths = []
    for sf in sfs:
        name = sf.get('name', '')
        safe = ascii_name(name)

        # ── 双曲線関数 ──
        if sf.get('definitions'):
            defs = sf['definitions']
            transforms = sf.get('transforms', [])
            body = [
                r'  \begin{align*}',
            ]
            items = list(defs.items())
            for i, (fn, formula) in enumerate(items):
                tex = u2l(str(formula)).replace('→', r' \to ')
                tex = mfunc(tex)
                sep = r' \\' if i < len(items) - 1 else ''
                body.append(f'    {tex}{sep}')
            body.append(r'  \end{align*}')
            if transforms:
                body.append(r'  \begin{block}{ラプラス変換}')
                body.append(r'  \begin{align*}')
                for i, tr in enumerate(transforms):
                    tex = u2l(str(tr)).replace('→', r' \to ')
                    tex = mfunc(tex)
                    tex = re.sub(r'(?<![<>!&])=(?!=)', r'&=', tex, count=1)
                    sep = r' \\' if i < len(transforms) - 1 else ''
                    body.append(f'    {tex}{sep}')
                body.append(r'  \end{align*}')
                body.append(r'  \end{block}')
            path = out_dir / f'{prefix}_sf_{safe}.tex'
            write_frame(name, body, path)
            paths.append(path)

        # ── 単位ステップ関数 ──
        elif sf.get('definition'):
            defn = sf['definition']
            graph = sf.get('graph_note', '')
            # { val (cond) } を cases 環境に変換してから display math
            defn_tex = mfunc(u2l(str(defn)).replace('→', r' \to '))
            defn_tex = convert_cases(defn_tex)
            body = [f'  \\[\n    {defn_tex}\n  \\]']
            if graph:
                body.append(f'  $t = a$ で $0$ から $1$ に跳躍する階段状の関数')
            path = out_dir / f'{prefix}_sf_{safe}.tex'
            write_frame(name, body, path)
            paths.append(path)

            # 例題5フレーム（example フィールド）
            ex = sf.get('example')
            if ex:
                ex_id = ex.get('id', '例題5')
                prob = ex.get('problem', '')
                solution = ex.get('solution', [])
                result = ex.get('result', '')

                # 問題フレーム
                prob_body = [
                    r'  \begin{exampleblock}{問題}',
                    f'  {fmt(prob)}\\\\[2pt]',
                    r'  \end{exampleblock}',
                ]
                p_path = out_dir / f'{prefix}_ex5_prob.tex'
                write_frame(ex_id, prob_body, p_path)
                paths.append(p_path)

                # 解答フレーム
                ans_body = []
                # 最初のステップをテキストとして
                if solution:
                    ans_body.append(f'  {fmt(str(solution[0]))}')
                # 数式ステップを align* に
                math_steps = [s for s in solution[1:] if '=' in str(s) or '∫' in str(s)]
                text_steps = [s for s in solution[1:] if s not in math_steps]
                if math_steps:
                    ans_body.append(r'  \begin{align*}')
                    for i, step in enumerate(math_steps):
                        tex = u2l(str(step)).replace('→', r' \to ')
                        tex = mfunc(tex)
                        tex = re.sub(r'(?<![<>!&])=(?!=)', r'&=', tex, count=1)
                        sep = r' \\' if i < len(math_steps) - 1 else ''
                        ans_body.append(f'    {tex}{sep}')
                    ans_body.append(r'  \end{align*}')
                if result:
                    ans_body += [
                        r'  \begin{alertblock}{答}',
                        f'    ${mfunc(u2l(str(result)))}$',
                        r'  \end{alertblock}',
                    ]
                a_path = out_dir / f'{prefix}_ex5_ans.tex'
                write_frame(f'{ex_id}　解答', ans_body, a_path)
                paths.append(a_path)

    return paths


def build_exercise_group(exercises: list, ids: list,
                          title: str, out_dir: Path, out_name: str) -> Path:
    """指定した問番号の演習フレームを生成"""
    target = [ex for ex in exercises if str(ex.get('id', '')) in ids]
    if not target:
        return None
    body = [r'  \begin{description}']
    for ex in target:
        ex_id = ex.get('id', '')
        content = str(ex.get('content', '')).strip()
        # \[ ... \] を含む場合は改行を保持、それ以外は空白に圧縮
        if r'\[' in content or r'\begin{' in content:
            lines = content.split('\n')
            first = fmt(lines[0].strip()) if lines else ''
            body.append(f'    \\item[{ex_id}] {first}')
            for line in lines[1:]:
                stripped = line.strip()
                if stripped:
                    body.append(f'    {fmt(stripped)}')
        else:
            content = re.sub(r'\s+', ' ', content)
            body.append(f'    \\item[{ex_id}] {fmt(content)}')
    body.append(r'  \end{description}')
    path = out_dir / out_name
    write_frame(title, body, path)
    return path


# ── メイン ───────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='chapter YAML → manual frame .tex ファイル生成')
    parser.add_argument('yaml_file', help='chapter YAML ファイル')
    parser.add_argument('--subsection', type=int, default=1, help='サブセクション ID')
    parser.add_argument('--week', type=int, required=True, help='週番号（ファイル名プレフィックス用）')
    parser.add_argument('--list', action='store_true', help='生成ファイルの一覧を表示して終了')
    args = parser.parse_args()

    base = _here
    yaml_path = base / args.yaml_file
    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    sub_map = {s['id']: s for s in data.get('subsections', [])}
    sub = sub_map.get(args.subsection)
    if not sub:
        print(f'Error: subsection {args.subsection} not found', file=sys.stderr)
        sys.exit(1)

    out_dir = base / 'lecture' / 'manual'
    out_dir.mkdir(parents=True, exist_ok=True)
    prefix = f'week{args.week:02d}_s{args.subsection}'

    print(f'Generating manual frames for week {args.week}, subsection {args.subsection}...')

    # 線形性
    props = sub.get('properties', [])
    if props:
        build_linearity(props, out_dir, prefix)

    # 数学ツール（部分積分・ロピタル）
    tools = sub.get('mathematical_tools', [])
    if tools:
        build_tools(tools, out_dir, prefix)

    # 特殊関数（双曲線・単位ステップ）
    sfs = sub.get('special_functions', [])
    if sfs:
        build_special_functions(sfs, out_dir, prefix)

    # 演習問題（グループ別）
    exercises = sub.get('exercises', [])
    if exercises:
        groups = [
            (['問1', '問2'], '問1・問2', f'{prefix}_q12.tex'),
            (['問3'],        '問3',       f'{prefix}_q3.tex'),
            (['問4', '問5'], '問4・問5', f'{prefix}_q45.tex'),
            (['問6', '問7'], '問6・問7', f'{prefix}_q67.tex'),
        ]
        for ids, title, fname in groups:
            build_exercise_group(exercises, ids, title, out_dir, fname)

    print('Done.')


if __name__ == '__main__':
    main()
