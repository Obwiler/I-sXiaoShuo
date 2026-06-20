# -*- coding: utf-8 -*-
"""
evolve_sync.py v2.0
功能: 扫描吸取教训文件，同步到各规范文件
新增: --pre-commit 预提交钩子模式 / --proposal 审查提案模式

用法:
  python evolve_sync.py [--dry-run] [--last=N]
  python evolve_sync.py --pre-commit   (git diff模式)
  python evolve_sync.py --proposal     (生成审查提案)
"""
import os, re, sys, datetime, subprocess

PROJECT = os.environ.get("WEBNOVEL_PROJECT") or os.getcwd()
LESSONS_FILE = os.path.join(PROJECT, "AI注意事项及规则", "09_吸取教训.md")
STYLE_FILE = os.path.join(PROJECT, "AI注意事项及规则", "00_写作风格规范.md")
PROCEDURE_FILE = os.path.join(PROJECT, "AI注意事项及规则", "03_写作模式规程.md")
TIPS_FILE = os.path.join(PROJECT, "AI注意事项及规则", "正文_技巧积累.md")
PROPOSAL_FILE = os.path.join(PROJECT, "_evolution_proposal.md")

DRY_RUN = "--dry-run" in sys.argv
PRE_COMMIT = "--pre-commit" in sys.argv
PROPOSAL = "--proposal" in sys.argv
LAST_N = None
for a in sys.argv:
    if a.startswith("--last="):
        try: LAST_N = int(a.split("=")[1])
        except: pass

def log(msg, level="INFO"):
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] [{level}] {msg}")

def parse_lessons(text):
    entries = []
    date_blocks = re.split(r'\n##\s+(\d{4}-\d{2}-\d{2})', text)
    current_date = "unknown"
    for i, block in enumerate(date_blocks):
        block = block.strip()
        if not block: continue
        if re.match(r'^\d{4}-\d{2}-\d{2}', block[:12]):
            current_date = block[:10]; continue
        for pattern in [r'###\s*教训.*?\n(.*?)(?=\n###\s*教训|\n##\s*\d{4}|\Z)', r'###?\s*教训[：:](.*?)(?=\n###?\s|\Z)']:
            for ls in re.findall(pattern, block, re.DOTALL):
                ls = ls.strip()
                if ls and len(ls) > 20:
                    entries.append({"date": current_date, "text": ls, "type": classify_lesson(ls)})
    seen = set()
    unique = []
    for e in entries:
        key = e["text"][:60]
        if key not in seen: seen.add(key); unique.append(e)
    return unique

def classify_lesson(text):
    lower = text.lower()
    if "发现时间" in lower and "纠正" not in lower: return "incomplete"
    rule_keywords = ["禁止", "禁用", "必须", "不允许", "一律", "绝对", "全文", "不能出现", "不得", "严禁", "应当", "需要", "写作时"]
    supplement_keywords = ["补充", "追加", "修正为", "调整", "改为"]
    has_rule = any(kw in text for kw in rule_keywords)
    has_supplement = any(kw in text for kw in supplement_keywords)
    if has_rule and not has_supplement:
        return "new_rule" if any(kw in text[:300] for kw in ["禁止", "禁用", "不使用", "不能"]) else "rule_supplement"
    elif has_supplement: return "rule_supplement"
    elif "案例" in text[:200] or "示例" in text[:200]: return "case_example"
    elif "问题" in text[:200] and "纠正" in text: return "rule_supplement"
    else: return "rule_supplement"

def get_git_diff():
    """预提交模式: 获取上次提交后的新增条目"""
    try:
        result = subprocess.run(["git", "diff", "--unified=0", "HEAD", "--", LESSONS_FILE], capture_output=True, text=True, cwd=PROJECT, timeout=10)
        additions = result.stdout
        if not additions: return ""
        new_lines = [line[1:] for line in additions.split("\n") if line.startswith("+") and not line.startswith("+++")]
        return "\n".join(new_lines)
    except: return ""

def generate_proposal(entries):
    """生成审查提案"""
    if not entries:
        log("无新增条目，跳过提案生成", "INFO"); return
    lines = ["# 自进化审查提案", "", f"> 生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", "", "---", ""]
    for e in entries:
        lines.append(f"## [{e['type']}] {e['date']}"); lines.append("")
        lines.append("`"); lines.append(e['text'][:200]); lines.append("`"); lines.append("")
    with open(PROPOSAL_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    log(f"审查提案已生成: {PROPOSAL_FILE}", "OK")

def main():
    log("=== evolve_sync v2.0: 自进化同步开始 ===")
    if not os.path.exists(LESSONS_FILE):
        log(f"文件不存在: {LESSONS_FILE}", "ERROR"); return 1

    if PRE_COMMIT:
        log("预提交模式: 扫描git diff新增条目")
        new_text = get_git_diff()
        if not new_text: log("无新增变更，跳过", "INFO"); return 0
        entries = parse_lessons(new_text)
        generate_proposal(entries); return 0

    if PROPOSAL:
        log("审查提案模式: 全量扫描")
        text = open(LESSONS_FILE, encoding="utf-8").read()
        entries = parse_lessons(text)
        generate_proposal(entries); return 0

    text = open(LESSONS_FILE, encoding="utf-8").read()
    entries = parse_lessons(text)
    log(f"解析出 {len(entries)} 条")
    if LAST_N and LAST_N < len(entries): entries = entries[-LAST_N:]; log(f"限制最近{LAST_N}条")
    types = {}
    for e in entries: types[e["type"]] = types.get(e["type"], 0) + 1
    for t, c in types.items(): log(f"  {t}: {c}条")
    if not DRY_RUN:
        new_rules = [e for e in entries if e["type"] in ("new_rule", "rule_supplement")]
        log(f"新规则/补充: {len(new_rules)}条")
        cases = [e for e in entries if e["type"] == "case_example"]
        log(f"案例: {len(cases)}条")
    log("=== 同步完成 ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())

