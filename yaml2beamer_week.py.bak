#!/usr/bin/env python3
"""
yaml2beamer_week.py
schedule.yaml + chapter*.yaml → 週別 Beamer .tex ファイル生成

使い方:
  python yaml2beamer_week.py              # 全週を生成
  python yaml2beamer_week.py --week 8     # 第8回のみ
  python yaml2beamer_week.py --week 8-11  # 第8〜11回
  python yaml2beamer_week.py --slide      # スライドモード出力
  python yaml2beamer_week.py --include-todo

出力: lecture/week08.tex, lecture/week08_slide.tex 等
"""

import yaml
import sys
import copy
from pathlib import Path

# yaml2beamer_chapter から共通関数をインポート
_here = Path(__file__).parent
sys.path.insert(0, str(_here))
from yaml2beamer_chapter import (
    assemble_subsection, build_practice_frame,
    build_separator_frame, build_exercise_answer_frames,
    frame_lines, page_ref, tex_title,
    gen_tex,
)


# ── フィルタリング付きサブセクション組み立て ─────────────────

STRUCTURAL_FIELDS = [
    'definition', 'fourier_coefficients', 'orthogonality',
    'convergence_theorem', 'fourier_integral_theorem',
    'even_odd', 'general_period', 'cosine_sine_transform',
    'complex_fourier', 'properties', 'parseval_formula',
    'method', 'spectrum',
]


def filter_subsection(sub: dict, spec: dict) -> dict:
    """
    spec に基づいてサブセクション dict をフィルタリングした新しい dict を返す。
    include_fields / include_examples / include_exercises が指定されている場合のみ絞り込む。
    """
    filtered = copy.deepcopy(sub)

    include_fields = spec.get('include_fields')
    if include_fields is not None:
        for key in STRUCTURAL_FIELDS:
            if key not in include_fields:
                filtered.pop(key, None)

    include_examples = spec.get('include_examples')
    if include_examples is not None:
        filtered['examples'] = [
            ex for ex in sub.get('examples', [])
            if str(ex.get('id', '')) in include_examples
        ]

    include_exercises = spec.get('include_exercises')
    if include_exercises is not None:
        filtered['exercises'] = [
            ex for ex in sub.get('exercises', [])
            if str(ex.get('id', '')) in include_exercises
        ]

    return filtered


# ── 週フレーム組み立て ────────────────────────────────────────

def assemble_week(week_spec: dict, data_map: dict, skip_todo: bool = True,
                  include_answers: bool = True, use_separator: bool = True) -> list:
    """
    週スペックに従ってフレーム行リストを生成。

    include_answers=True, use_separator=True  → [本編] → [区切り「試験前配布」] → [解答]  (handout 従来)
    include_answers=True, use_separator=False → [本編] → [解答]                           (color ans)
    include_answers=False                     → [本編] のみ                                (color main)
    """
    source = week_spec['source']
    data = data_map[source]

    # サブセクション ID → dict のマップを作成
    sub_map = {sub['id']: sub for sub in data.get('subsections', [])}

    main_frames = []   # 概念・例題・問題文
    answer_frames = [] # 演習解説

    sub_specs = week_spec.get('subsections', [])
    show_divider = len(sub_specs) > 1  # サブセクションが複数あるときだけ区切りを表示

    for sub_spec in sub_specs:
        sub_id = sub_spec['id']
        sub = sub_map.get(sub_id)
        if sub is None:
            print(f'Warning: subsection {sub_id} not found in {source}', file=sys.stderr)
            continue

        # フィルタリング（フィールド指定がある場合のみ）
        has_filter = any(k in sub_spec for k in ('include_fields', 'include_examples', 'include_exercises'))
        if has_filter:
            sub = filter_subsection(sub, sub_spec)

        # サブセクション区切りフレーム（複数サブセクションがある週のみ）
        if show_divider:
            sub_title = sub.get('title', '')
            sub_pages = sub.get('pages', '')
            divider_body = [
                r'  \begin{block}{}',
                f'  {{\\large {sub_title}}}',
                r'  \end{block}',
            ]
            if sub_pages:
                divider_body.append(
                    f'  \\vfill\\hfill{{\\scriptsize \\textcolor{{gray}}{{{page_ref(sub_pages)}}}}}'
                )
            main_frames += frame_lines(sub_title, divider_body)

        main_frames += assemble_subsection(sub, skip_todo=skip_todo)

        # 演習解説フレームを収集（answer フィールドがある問のみ）
        if include_answers:
            exercises = sub.get('exercises', [])
            answer_frames += build_exercise_answer_frames(exercises, skip_todo=skip_todo)

    # 練習問題（問題文）
    if week_spec.get('include_practice'):
        practice = data.get('practice_problems')
        if practice:
            main_frames += build_practice_frame(practice, skip_todo=skip_todo)

    # 解説パートを末尾に追加
    if include_answers and answer_frames:
        if use_separator:
            main_frames += build_separator_frame()
        main_frames += answer_frames

    return main_frames


# ── TeX ファイル生成 ──────────────────────────────────────────

def gen_week_tex(week_spec: dict, data_map: dict,
                 skip_todo: bool = True, mode: str = 'handout',
                 include_answers: bool = True) -> str:
    """
    mode:
      'handout'    : モノクロ4up（従来デフォルト）
      'slide'      : モノクロ1枚/p
      'color_main' : カラー16:9・解説なし
      'color_ans'  : カラー16:9・解説あり（区切りなし）
    """
    week_num = week_spec['week']
    title = week_spec.get('title', f'第{week_num}回')
    source = week_spec['source']
    data = data_map[source]

    ch = data.get('chapter', '')
    ch_title = data.get('chapter_title', '')
    sec = data.get('section', '')

    if mode in ('color_main', 'color_ans'):
        docclass = r'\documentclass[aspectratio=169,professionalfonts]{beamer}'
        slidemode_cmd = r'\newcommand{\slidemode}{1}  % カラー投影モード'
        _include_answers = (mode == 'color_ans')
        _use_separator = False
    elif mode == 'slide':
        docclass = r'\documentclass[aspectratio=43,professionalfonts]{beamer}'
        slidemode_cmd = ''
        _include_answers = include_answers
        _use_separator = True
    else:  # handout
        docclass = r'\documentclass[aspectratio=43,professionalfonts,handout]{beamer}'
        slidemode_cmd = ''
        _include_answers = include_answers
        _use_separator = True

    header = [
        '% !TEX program = lualatex',
        docclass,
    ]
    if slidemode_cmd:
        header.append(slidemode_cmd)
    header += [
        r'\usepackage{beamer_template}',
        r'\usepackage{enumerate}',
        '',
        f'\\newcommand{{\\LectureNum}}{{{week_num}}}',
        f'\\newcommand{{\\LectureTitle}}{{{title}}}',
        f'\\newcommand{{\\CourseName}}{{応用数学}}',
        r'\renewcommand{\TermName}{前期}',
        '',
        r'\begin{document}',
        '',
    ]

    # 表紙フレーム
    title_body = [
        r'  \begin{block}{本回の内容}',
        f'  {title}',
        r'  \end{block}',
        f'  \\vfill\\hfill{{\\scriptsize \\textcolor{{gray}}{{第{ch}章 {ch_title}　§{sec}}}}}',
    ]
    title_frames = frame_lines(f'第{week_num}回　{title}', title_body)

    frames = title_frames + assemble_week(
        week_spec, data_map, skip_todo=skip_todo,
        include_answers=_include_answers, use_separator=_use_separator,
    )
    footer = ['', r'\end{document}', '']

    return '\n'.join(header) + '\n' + '\n'.join(frames) + '\n'.join(footer)


# ── メイン ───────────────────────────────────────────────────

def parse_week_range(s: str) -> list:
    """'8', '8-11', '8,9,11' などをパースして週番号リストに"""
    weeks = []
    for part in s.split(','):
        part = part.strip()
        if '-' in part:
            a, b = part.split('-', 1)
            weeks.extend(range(int(a), int(b) + 1))
        else:
            weeks.append(int(part))
    return weeks


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description='schedule.yaml → 週別 Beamer .tex ファイル生成',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument('--week', help='生成する週番号（例: 8, 8-11, 8,9,11）')
    parser.add_argument('--slide', action='store_true', help='スライドモード出力（モノクロ）')
    parser.add_argument('--color', action='store_true',
                        help='カラー16:9で解説なし(_main)と解説あり(_ans)を両方生成')
    parser.add_argument('--include-todo', action='store_true', help='要確認項目も含める')
    parser.add_argument('--schedule', default='schedule.yaml', help='スケジュール YAML')
    args = parser.parse_args()

    skip_todo = not args.include_todo
    if args.color:
        mode = 'color'
    elif args.slide:
        mode = 'slide'
    else:
        mode = 'handout'

    base_dir = _here
    schedule_path = base_dir / args.schedule
    if not schedule_path.exists():
        print(f'Error: {schedule_path} が見つかりません', file=sys.stderr)
        sys.exit(1)

    with open(schedule_path, 'r', encoding='utf-8') as f:
        schedule = yaml.safe_load(f)

    all_weeks = schedule.get('weeks', [])

    # 週番号フィルタ
    if args.week:
        target_weeks = set(parse_week_range(args.week))
        all_weeks = [w for w in all_weeks if w['week'] in target_weeks]

    if not all_weeks:
        print('対象の週が見つかりません', file=sys.stderr)
        sys.exit(1)

    # 必要なソース YAML を読み込む
    sources_needed = {w['source'] for w in all_weeks}
    data_map = {}
    for src in sources_needed:
        src_path = base_dir / src
        if not src_path.exists():
            print(f'Error: {src_path} が見つかりません', file=sys.stderr)
            sys.exit(1)
        with open(src_path, 'r', encoding='utf-8') as f:
            data_map[src] = yaml.safe_load(f)

    out_dir = base_dir / 'lecture'
    out_dir.mkdir(parents=True, exist_ok=True)

    for week_spec in all_weeks:
        week_num = week_spec['week']

        if mode == 'color':
            # カラー版：解説なし(_main) と 解説あり(_ans) を両方生成
            for variant, m in [('_main', 'color_main'), ('_ans', 'color_ans')]:
                out_path = out_dir / f'week{week_num:02d}{variant}.tex'
                content = gen_week_tex(week_spec, data_map, skip_todo=skip_todo, mode=m)
                with open(out_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                frame_count = content.count(r'\begin{frame}')
                print(f'Generated: {out_path}  ({frame_count} frames)')
        else:
            suffix = '_slide' if mode == 'slide' else ''
            out_path = out_dir / f'week{week_num:02d}{suffix}.tex'
            content = gen_week_tex(week_spec, data_map, skip_todo=skip_todo, mode=mode)
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(content)
            frame_count = content.count(r'\begin{frame}')
            print(f'Generated: {out_path}  ({frame_count} frames)')


if __name__ == '__main__':
    main()
