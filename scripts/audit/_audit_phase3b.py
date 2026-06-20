from docx import Document

doc2 = Document(os.path.join(PROJECT, "设定", "04_世界观与势力.docx"))
print('=== 04_世界观与势力.docx 段落索引 ===')
for i, p in enumerate(doc2.paragraphs):
    t = p.text.strip()
    if t:
        if len(t) < 120:
            print(f'P{i}: {t}')
        else:
            print(f'P{i}: {t[:120]}...')
