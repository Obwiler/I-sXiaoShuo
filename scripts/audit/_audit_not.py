import re, os

PROJECT = os.environ.get("WEBNOVEL_PROJECT") or os.getcwd()
from docx import Document

files = [
    os.path.join(PROJECT, "设定", "02_大纲章纲.docx"),
    os.path.join(PROJECT, "设定", "00_设定总纲.docx"),
    os.path.join(PROJECT, "设定", "01_人物档案.docx"),
    os.path.join(PROJECT, "设定", "03_伏笔追踪.docx"),
    os.path.join(PROJECT, "设定", "04_世界观与势力.docx"),
    os.path.join(PROJECT, "AI注意事项及规则", "09_吸取教训.md"),
    os.path.join(PROJECT, "AI注意事项及规则", "10_角色声音自查.md"),
    os.path.join(PROJECT, "AI注意事项及规则", "11_终局写法策略.md"),
    os.path.join(PROJECT, "其他", "记忆锚点.md"),
]

total = 0

for fp in files:
    if not os.path.exists(fp):
        print(f'[MISS] {fp}')
        continue
    name = os.path.basename(fp)
    if fp.endswith('.md'):
        with open(fp, 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        doc = Document(fp)
        text = '\n'.join([p.text for p in doc.paragraphs])
    
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if '不是' in line and ('而是' in line or '只是' in line):
            # Check if it's the "不是...而是..." pattern
            idx = line.find('不是')
            if idx >= 0:
                rest = line[idx:idx+120]
                if '而是' in rest or '只是' in rest:
                    print(f'[{name}] L{i+1}: ...{rest[:100]}...')
                    total += 1

if total == 0:
    print('✅ 零残留：全文无结构性"不是……而是……"句式')
else:
    print(f'\n⚠️ 发现 {total} 处残留')
