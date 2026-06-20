#!/usr/bin/env python3
"""align_canonical.py — 设定→规范数据 对齐管道（MD 版）
从 设定/md/*.md 提取规范数据，输出 canonical_data.json。
人工检查模块已移除（用户要求删除）。
"""
import os, re, sys, json

PROJECT = os.environ.get("WEBNOVEL_PROJECT") or os.getcwd()
CANON_DIR = os.path.join(PROJECT, "设定", "md")

def read_md(filename):
    path = os.path.join(CANON_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    # Strip frontmatter
    if content.startswith("---"):
        end = content.find("---", 3)
        if end >= 0:
            content = content[end + 3:].strip()
    return content

def read_md_lines(filename):
    return read_md(filename).split("\n")

def main():
    print("=" * 50)
    print(" [align_canonical] 从 MD 提取规范数据")
    print("=" * 50)
    
    chapters = []
    arc_names = ["弧段一：猎杀工具","弧段二：裂痕","弧段三：峰会","弧段四：压制","弧段五：终局"]
    arc_labels = ["弧段一 猎杀工具","弧段二 裂痕","弧段三 峰会","弧段四 压制","弧段五 终局"]
    cur = 0
    
    lines = read_md_lines("02_大纲章纲.md")
    for line in lines:
        for ai, an in enumerate(arc_names):
            if an[:4] in line:
                cur = ai
        m = re.search(r"第(\d+)章", line)
        if m:
            ch = int(m.group(1))
            rest = line[m.end():]
            for sep in ["（", "("]:
                if sep in rest:
                    rest = rest[:rest.index(sep)]
            nm = rest.strip()[:20]
            if ch not in [c["ch"] for c in chapters]:
                chapters.append({
                    "ch": ch, "arc": cur, "name": nm,
                    "arc_name": arc_names[cur],
                    "arc_label": arc_labels[cur],
                })
    print(f"  chapters: {len(chapters)}")
    
    # 保存 JSON
    data = {"chapters": chapters}
    canon_path = os.path.join(PROJECT, "设定", "canonical_data.json")
    with open(canon_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  saved: {canon_path}")
    print("=" * 50)
    print(" 完成")
    print("=" * 50)

if __name__ == "__main__":
    main()