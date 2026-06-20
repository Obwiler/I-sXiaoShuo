import sys
sys.stdout.reconfigure(encoding='utf-8')
from docx import Document
import os, copy

base = os.path.join(PROJECT, "设定")

# ============ Replacements ============
# (file, old_text, new_text)
replacements = [
    # 世界观与势力: M1-M5 in narrative text
    ('04_世界观与势力.docx', 'M1 · 中枢教会', '中枢教会'),
    ('04_世界观与势力.docx', 'M2 · 解放阵线', '解放阵线'),
    ('04_世界观与势力.docx', 'M3 · 血缘社', '血缘社'),
    ('04_世界观与势力.docx', 'M4 · 「灰桥」', '灰桥'),
    ('04_世界观与势力.docx', 'M5 · 传承会', '传承会'),
    ('04_世界观与势力.docx', 'M系列组织', '边缘行者武装组织'),
    ('04_世界观与势力.docx', 'M1教长', '中枢教会教长'),
    ('04_世界观与势力.docx', 'M1中枢教会', '中枢教会'),
    ('04_世界观与势力.docx', 'M2解放阵线', '解放阵线'),
    ('04_世界观与势力.docx', 'M3血缘社', '血缘社'),
    ('04_世界观与势力.docx', 'M4灰桥', '灰桥'),
    ('04_世界观与势力.docx', 'M5传承会', '传承会'),
    ('04_世界观与势力.docx', 'M1', '中枢教会'),
    ('04_世界观与势力.docx', 'M2', '解放阵线'),
    ('04_世界观与势力.docx', 'M3', '血缘社'),
    ('04_世界观与势力.docx', 'M4', '灰桥'),
    ('04_世界观与势力.docx', 'M5', '传承会'),
    ('04_世界观与势力.docx', 'A01（国家最高决策者）', '国家最高决策者'),
    ('04_世界观与势力.docx', 'A03（宣传系统）', '宣传系统负责人'),
    ('04_世界观与势力.docx', 'A01', '国家最高决策者'),
    ('04_世界观与势力.docx', 'A03', '宣传系统负责人'),
    ('04_世界观与势力.docx', 'K系列', '人类建制化'),
    ('04_世界观与势力.docx', 'H系', '外援者'),
    # 设定总纲: power levels
    ('00_设定总纲.docx', 'L3（主角李景宜）', '全球峰值（主角李景宜）'),
    ('00_设定总纲.docx', 'L2（人类正规武装）', '人类正规武装'),
    ('00_设定总纲.docx', 'L1.5（人类顶尖战力）', '人类顶尖战力'),
    ('00_设定总纲.docx', 'L1（普通边缘行者）', '普通边缘行者'),
    ('00_设定总纲.docx', 'L3', '全球峰值'),
    ('00_设定总纲.docx', 'L2', '人类正规武装'),
    ('00_设定总纲.docx', 'L1.5', '人类顶尖战力'),
    ('00_设定总纲.docx', 'L1', '普通边缘行者'),
    # 人物档案: power levels and org codes
    ('01_人物档案.docx', 'L1.5层级', '人类顶尖战力层级'),
    ('01_人物档案.docx', 'L1.5', '人类顶尖战力'),
    ('01_人物档案.docx', 'L1', '普通边缘行者'),
    ('01_人物档案.docx', 'L3', '全球峰值'),
    ('01_人物档案.docx', 'L2', '人类正规武装'),
]

for fn, old, new in replacements:
    fp = os.path.join(base, fn)
    if not os.path.exists(fp):
        continue
    doc = Document(fp)
    count = 0
    for para in doc.paragraphs:
        if old in para.text:
            # Need to handle runs carefully
            for run in para.runs:
                if old in run.text:
                    run.text = run.text.replace(old, new)
                    count += 1
            # Also handle text in paragraphs directly
            if old in para.text:
                # Some text might be in the paragraph element directly
                for run in para.runs:
                    run.text = run.text.replace(old, new)
    if count > 0:
        doc.save(fp)
        print(f"  {fn}: {count} replacements")

print("Cleaning complete.")
