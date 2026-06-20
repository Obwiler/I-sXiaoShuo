from docx import Document

PROJECT = os.environ.get("WEBNOVEL_PROJECT") or os.getcwd()
outline_arg = sys.argv[1] if len(sys.argv) > 1 else None
outline_path = outline_arg or os.path.join(PROJECT, "设定", "02_大纲章纲.docx")
doc = Document(outline_path)

# Index all paragraphs
paragraphs = []
for i, p in enumerate(doc.paragraphs):
    t = p.text.strip()
    if t:
        paragraphs.append((i, t))

# Find chapter boundaries
chapters = []
for i, (idx, text) in enumerate(paragraphs):
    for n in range(1, 53):
        tag = f'第{n:03d}章'
        if text.startswith(tag):
            # Get end (next chapter or end)
            end_idx = len(paragraphs)
            for j in range(i+1, len(paragraphs)):
                for m in range(n+1, 53):
                    next_tag = f'第{m:03d}章'
                    if paragraphs[j][1].startswith(next_tag):
                        end_idx = j
                        break
                if end_idx < len(paragraphs):
                    break
            chapters.append((n, i, end_idx, text[:50]))
            break

# Print chapter index
print('=== 章节索引 ===')
for n, s, e, h in chapters:
    print(f'  Ch{n:03d}: 段落{s}-{e} 标题: {h}')

print()

# 11 claimed insertions
claims = [
    ('Ch002', '马磊', '马磊在监控日志上看到了这段异常侧信道数据'),
    ('Ch003', '陈国栋', '陈国栋周五前需要'),
    ('Ch003', '林婉', '林婉在关机前'),
    ('Ch006', '卡特', '卡特在课后'),
    ('Ch006', '福斯特', '福斯特在起草'),
    ('Ch007', '肖扬', '肖扬在事后'),
    ('Ch013', '赵文斌', '赵文斌'),
    ('Ch013', '方静', '方静'),
    ('Ch016', '克劳福德', '克劳福德'),
    ('Ch016', '贝特朗', '贝特朗'),
    ('Ch017', '周明远', '周明远'),
    ('Ch022', '瓦格纳', '瓦格纳'),
    ('Ch026', '顾峰', '顾峰'),
    ('Ch030', '赤隼', '赤隼'),
    ('Ch044', '钱程', '钱程'),
]

for ch_id, char, desc in claims:
    ch_num = int(ch_id.replace('Ch', ''))
    
    # Find chapter
    ch_data = None
    for n, s, e, h in chapters:
        if n == ch_num:
            ch_data = (s, e)
            break
    
    if not ch_data:
        print(f'❌ {ch_id} {char}: 章节未找到')
        continue
    
    ch_start, ch_end = ch_data
    # Search within chapter paragraphs
    found = False
    for i in range(ch_start, ch_end):
        if char in paragraphs[i][1]:
            snippet = paragraphs[i][1][:120]
            print(f'  ✅ {ch_id} {char}: (P{paragraphs[i][0]}) {snippet}...')
            found = True
            break
    
    if not found:
        # Also search a few paragraphs after chapter end
        for i in range(ch_end, min(ch_end+3, len(paragraphs))):
            if char in paragraphs[i][1]:
                snippet = paragraphs[i][1][:120]
                print(f'  ⚠️ {ch_id} {char}: 在下一章P{paragraphs[i][0]}找到: {snippet}...')
                found = True
                break
        if not found:
            print(f'  ❌ {ch_id} {char}: 在章节内未找到')
