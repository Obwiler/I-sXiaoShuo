import os
PROJECT = os.environ.get("WEBNOVEL_PROJECT") or os.getcwd()
import docx
doc = docx.Document(os.path.join(PROJECT, "设定", "02_大纲章纲.docx"))
t = doc.paragraphs[0].text
print("DOCX chars:", len(t))
checks = ["第012章 增补节", "第020章 增补节", "第025章 增补节", "第037章 增补节", "第026章 增补节", "加洛林特遣人员", "塞西尔特派观察员", "中枢教会搜索队", "联合指挥部内卫分队"]
print("=== Insertion verification ===")
for c in checks:
    print("  OK" if c in t else "  MISS", ":", c[:20])
violations = ["十七秒", "百分之十五", "零点五秒", "十一点三秒", "零点三秒", "从铰链"]
print("=== Residual violation scan ===")
for v in violations:
    print("  RESIDUAL" if v in t else "  CLEAN", ":", v)
with open(os.path.join(PROJECT, "AI注意事项及规则", "09_吸取教训.md"), "r", encoding="utf-8") as f:
    ls = f.read()
print("=== Lessons ===")
for r in ["教训一百零六：五要素标准化", "教训一百零七：公文格式写作标准", "教训一百零八：反派交锋密度", "教训一百零九：多势力武装冲突密度", "教训一百一十：中二体清除专项"]:
    print("  LESSON-OK" if r in ls else "  LESSON-MISS", ":", r[:15])
