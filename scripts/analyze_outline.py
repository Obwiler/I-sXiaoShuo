"""大纲情节分析脚本 v4 · 可自定义弧段结构"""
import sys, os, re, json, argparse
from docx import Document

# Chinese numeral map 1-99
_CN_DIGITS = "一二三四五六七八九"
_CN_NUM = {}
for _i, _d in enumerate(_CN_DIGITS, 1):
    _CN_NUM[_d] = _i
_CN_NUM["十"] = 10
for _i, _d in enumerate(_CN_DIGITS, 1):
    _CN_NUM[_d + "十"] = _i * 10
    _CN_NUM["十" + _d] = 10 + _i
for _i1, _d1 in enumerate(_CN_DIGITS, 1):
    for _i2, _d2 in enumerate(_CN_DIGITS, 1):
        _CN_NUM[_d1 + "十" + _d2] = _i1 * 10 + _i2
_CN_KEYS = sorted(_CN_NUM.keys(), key=len, reverse=True)

def load_outline(path):
    if path.lower().endswith('.docx'):
        doc = Document(path)
        paras = [(p, any(r.bold for r in p.runs) if p.runs else False) for p in doc.paragraphs if p.text.strip()]
    else:
        with open(path, 'r', encoding='utf-8') as f:
            md_text = f.read()
        if md_text.startswith('---'):
            end_fm = md_text.find('---', 3)
            if end_fm >= 0:
                md_text = md_text[end_fm + 3:].strip()
        paras = []
        for line in md_text.split('\n'):
            line = line.rstrip()
            if not line: continue
            stripped = line.strip()
            is_bold = False
            if stripped.startswith('#'):
                is_bold = True
            elif any(x in stripped for x in ['弧段', '章', '节']):
                is_bold = True
            paras.append((stripped, is_bold))
    
    sections, chapters = [], []
    current_section = None
    current_chapter = ''
    current_arc = ''
    current_chapter_num = 0
    for t, bold in paras:
        if bold:
            if '弧段' in t[:6]:
                current_arc = t[:50]; current_chapter = t[:50]
                arc_range_m = re.search(r'[（(](\d+)\s*-\s*(\d+)[)）]', t)
                if arc_range_m:
                    current_chapter_num = int(arc_range_m.group(1))
            elif '章' in t[:8]:
                current_chapter = t[:50]
                current_chapter_num = _extract_num(t)
                chapters.append(t[:50])
            elif '节' in t[:4]:
                s = {'name': t[:30], 'chapter': current_chapter, 'arc': current_arc,
                     'elements': {}, 'paras': [], 'chapter_num': current_chapter_num}
                sections.append(s)
                current_section = s
            continue
        if current_section is None:
            continue
        for k, label in [('前因：', '前因'), ('过程：', '过程'),
                         ('后果：', '后果'), ('动机：', '动机'), ('影响：', '影响')]:
            if t.startswith(k):
                current_section['elements'][label] = t
                current_section['paras'].append(t)
                break
        else:
            if current_section['paras']:
                current_section['paras'].append(t)
    return sections, chapters


def _extract_num(text):
    m = re.search(r"[(（](\d+)\s*-\s*(\d+)[)）]", text)
    if m: return int(m.group(1))
    for _k in _CN_KEYS:
        if _k in text: return _CN_NUM[_k]
    m = re.search(r"(\d+)", text)
    if m: return int(m.group(1))
    return 0

def parse_arc_defs(arc_str):
    """解析弧段定义。格式: 名称(001-018);名称(019-035)"""
    if not arc_str or arc_str == 'auto':
        return None
    arcs = []
    for part in arc_str.replace('\n',';').split(';'):
        part = part.strip()
        if not part: continue
        # 格式1: 名称(001-012) —纯数字
        m = re.search(r'\((\d+)\s*-\s*(\d+)\)', part)
        if m:
            arcs.append({'name': part[:m.start()].strip(), 'start_num': int(m.group(1)), 'end_num': int(m.group(2))})
            continue
        # 格式2: 名称(Ch001-012)
        m = re.search(r'\(Ch?(\d+)\s*-\s*Ch?(\d+)\)', part)
        if m:
            arcs.append({'name': part[:m.start()].strip(), 'start_num': int(m.group(1)), 'end_num': int(m.group(2))})
    return arcs if arcs else None

def _default_5_arcs():
    return [{'name': '弧段一：猎杀工具', 'start_num': 1, 'end_num': 7},
            {'name': '弧段二：裂痕', 'start_num': 8, 'end_num': 19},
            {'name': '弧段三：峰会', 'start_num': 20, 'end_num': 33},
            {'name': '弧段四：压制', 'start_num': 34, 'end_num': 43},
            {'name': '弧段五：终局', 'start_num': 44, 'end_num': 52}]

def analyze_arc_structure(sections, arc_defs=None):
    """可自定义弧段分析"""
    auto = arc_defs is None
    arc_defs = arc_defs or _default_5_arcs()
    
    result_arcs = []
    unmatched = []
    for sec in sections:
        matched = False
        for arc in arc_defs:
            if arc['start_num'] <= sec['chapter_num'] <= arc['end_num']:
                result_arcs.append({**sec, 'arc_group': arc['name']})
                matched = True
                break
        if not matched:
            unmatched.append(sec)
    
    # Group by arc
    by_arc = {}
    for s in result_arcs:
        g = s['arc_group']
        if g not in by_arc:
            by_arc[g] = []
        by_arc[g].append(s)
    
    lines = []
    tension_values = []
    
    for arc in arc_defs:
        name = arc['name']
        group = by_arc.get(name, [])
        if not group:
            lines.append(f"  [WARN] {name}: 无匹配章节")
            tension_values.append(0)
            continue
        
        total_elements = sum(len(s['elements']) for s in group)
        avg = total_elements / max(len(group), 1)
        est = round(avg * 2, 1)
        tension_values.append(est)
        bar = '█' * min(int(est), 10) + '░' * max(10 - min(int(est), 10), 0)
        
        status = 'PASS' if avg >= 4.5 else ('WARN' if avg >= 3.0 else 'FAIL')
        lines.append(f"  [{status}] {name}")
        lines.append(f"       节数: {len(group)} | 要素均: {avg:.1f}/5")
        lines.append(f"       张力: {bar} {est}/10")
    
    # 张力诊断
    if len(tension_values) >= 2:
        lines.append("--- 张力诊断 ---")
        peak = max(tension_values)
        peak_idx = tension_values.index(peak)
        if peak_idx == len(tension_values) - 1:
            lines.append("  [PASS] 高峰在终段")
        elif peak_idx >= len(tension_values) * 0.5:
            lines.append("  [PASS] 高峰在后半段")
        else:
            lines.append("  [WARN] 高峰偏前")
        
        if len(tension_values) >= 3 and max(tension_values) - min(tension_values) < 2:
            lines.append("  [WARN] 张力落差过小")
        else:
            lines.append("  [PASS] 张力落差合理")
        
        for i in range(len(tension_values) - 1):
            diff = tension_values[i] - tension_values[i+1]
            if diff > 3:
                lines.append(f"  [WARN] 弧段{i+1}→{i+2}陡降{diff}")
    
    info = f"自定义: {len(arc_defs)}弧段" if not auto else f"自动: {len(arc_defs)}弧段"
    lines.insert(0, f"模式: {info}")
    lines.insert(1, f"总节: {sum(len(v) for v in by_arc.values())}")
    
    return {'name': '弧段结构', 'status': 'INFO', 'details': lines,
            'config_hint': '用 --arcs 自定义弧段。格式: "名称(001-012);名称(013-025)"'}

# --- 其他分析函数 ---
def analyze_five_elements(sections):
    total = len(sections)
    complete = sum(1 for s in sections if len(s['elements']) == 5)
    ratio = complete / max(total, 1) * 100
    status = 'PASS' if ratio >= 90 else 'WARN'
    gaps = [(s['name'], [k for k in ['前因','过程','后果','动机','影响'] if k not in s['elements']]) for s in sections if len(s['elements']) < 5]
    return {'name': '五要素覆盖', 'status': status, 'ratio': f'{ratio:.0f}%', 'complete': complete, 'total': total, 'gaps': gaps[:5]}

def analyze_causal_chain(sections):
    total = sum(1 for s in sections if len(s['elements']) >= 3)
    complete = sum(1 for s in sections if '前因' in s['elements'] and '后果' in s['elements'])
    ratio = complete / max(total, 1) * 100
    status = 'PASS' if ratio >= 90 else 'WARN'
    return {'name': '因果链完整性', 'status': status, 'ratio': f'{ratio:.0f}%', 'complete': complete, 'total': total}

def analyze_motivation(sections):
    an = [s for s in sections if len(s['elements']) >= 2]
    wm = sum(1 for s in an if '动机' in s['elements'])
    ratio = wm / max(len(an), 1) * 100
    status = 'PASS' if ratio >= 90 else 'WARN'
    gaps = [s['name'] for s in an if '动机' not in s['elements']]
    return {'name': '角色动机覆盖', 'status': status, 'ratio': f'{ratio:.0f}%', 'with_motive': wm, 'total': len(an), 'gaps': gaps[:5]}

def analyze_foreshadow(sections):
    return {'name': '伏笔标记', 'status': 'INFO', 'note': '伏笔在03_伏笔追踪.docx中'}

def main():
    parser = argparse.ArgumentParser(description='大纲情节分析')
    parser.add_argument('--target', default=None, help='大纲文件路径')
    parser.add_argument('--arcs', default='auto', help='弧段定义。格式: "名称(001-012);名称(013-025)"')
    parser.add_argument('--json', action='store_true', help='输出JSON')
    parser.add_argument('--check', default='all', help='检查项: all/1,2,3,4,5,6')
    args = parser.parse_args()
    
    target = args.target
    if not target:
        for c in [os.path.join(PROJECT, "设定", "md", "02_大纲章纲.md"),
                  r'']:
            if os.path.exists(c):
                target = c
                break
    if not target or not os.path.exists(target):
        print('Error: outline not found'); return 1
    
    sections, chapters = load_outline(target)
    arc_defs = parse_arc_defs(args.arcs)
    
    checks = {'1': analyze_five_elements, '2': analyze_causal_chain,
              '4': analyze_motivation, '5': analyze_foreshadow}
    results = []
    if args.check == 'all' or '3' in args.check or '1' not in args.check:
        results.append(analyze_arc_structure(sections, arc_defs))
    if args.check == 'all' or '1' in args.check:
        results.append(checks.get('1', lambda s:{'name':'N/A','status':'FAIL'})(sections))
    if args.check == 'all' or '2' in args.check:
        results.append(checks.get('2', lambda s:{'name':'N/A','status':'FAIL'})(sections))
    if args.check == 'all' or '4' in args.check:
        results.append(checks.get('4', lambda s:{'name':'N/A','status':'FAIL'})(sections))
    if args.check == 'all' or '5' in args.check:
        results.append(checks.get('5', lambda s:{'name':'N/A','status':'FAIL'})(sections))
    
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return 0
    
    print(f"\n[大纲分析] {os.path.basename(target)} | {target}")
    print(f"章节: {len(chapters)} | 节: {len(sections)}")
    print()
    for r in results:
        s = r['status']
        print(f"  [{s:>4}] {r['name']}")
        if 'ratio' in r:
            print(f"         {r['ratio']} ({r.get('complete','?')}/{r.get('total','?')})")
        if 'details' in r:
            for l in r['details']:
                print(f"         {l}")
        if 'gaps' in r and r['gaps']:
            for g in r['gaps'][:3]:
                print(f"         gap: {g[0] if isinstance(g,tuple) else g}")
        if 'note' in r:
            print(f"         note: {r['note']}")
        if 'config_hint' in r:
            print(f"         hint: {r['config_hint']}")
        print()
    
    fails = sum(1 for r in results if r['status'] == 'FAIL')
    warns = sum(1 for r in results if r['status'] == 'WARN')
    print(f"  判定: {'PASS' if fails==0 and warns==0 else 'WARN' if fails==0 else 'FAIL'} (失败{fails}, 警告{warns})")
    return 0 if fails == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
