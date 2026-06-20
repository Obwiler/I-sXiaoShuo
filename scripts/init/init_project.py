# -*- coding: utf-8 -*-
"""Project initializer for webnovel-studio skill.

Usage:
    python init_project.py --name "我的小说" --path /path/to/project --genre fantasy

Reads template files from ../templates/project-init/template_rules/ and template_docs/
Replaces {{project_name}}, {{date}}, {{path}} placeholders in template files.
Generates PROJECT.yaml, _HANDOFF.md, 记忆锚点.md, _chapter_index.yaml.
"""

import os, sys, datetime

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEMPLATES_RULES = os.path.join(SKILL_DIR, "templates", "project-init", "template_rules")
TEMPLATES_DOCS = os.path.join(SKILL_DIR, "templates", "project-init", "template_docs")


def render_template(src_path, replacements):
    content = open(src_path, "r", encoding="utf-8").read()
    for key, val in replacements.items():
        content = content.replace("{{" + key + "}}", val)
    return content


def main():
    name = "My Novel"
    path = os.getcwd()
    genre = "default"
    args = sys.argv[1:]
    for i, a in enumerate(args):
        if a == "--name" and i + 1 < len(args):
            name = args[i + 1]
        if a == "--path" and i + 1 < len(args):
            path = os.path.abspath(args[i + 1])
        if a == "--genre" and i + 1 < len(args):
            genre = args[i + 1]

    if not os.path.exists(path):
        os.makedirs(path)

    replacements = {
        "project_name": name,
        "date": datetime.date.today().isoformat(),
        "path": path,
    }

    created = 0

    # 1. Copy template_rules/ -> AI注意事项及规则/
    rules_target = os.path.join(path, "AI注意事项及规则")
    if os.path.exists(TEMPLATES_RULES):
        for f in os.listdir(TEMPLATES_RULES):
            if f.endswith(".md"):
                content = render_template(os.path.join(TEMPLATES_RULES, f), replacements)
                target = os.path.join(rules_target, f)
                os.makedirs(os.path.dirname(target), exist_ok=True)
                open(target, "w", encoding="utf-8").write(content)
                created += 1
        # Genre-specific rule appendix (P2: --genre)
    # Genre affects PROJECT.yaml output only; template branching TBD
    pass
    # 2. Copy template_docs/ -> project root (skip gitignore, README)
    docs_skip = {".gitignore", "README.md"}
    if os.path.exists(TEMPLATES_DOCS):
        for item in os.listdir(TEMPLATES_DOCS):
            item_path = os.path.join(TEMPLATES_DOCS, item)
            if os.path.isdir(item_path):
                target = os.path.join(path, item)
                if not os.path.exists(target):
                    os.makedirs(target)
            elif item not in docs_skip and item.endswith(".md"):
                content = render_template(item_path, replacements)
                target = os.path.join(path, item)
                os.makedirs(os.path.dirname(target), exist_ok=True)
                open(target, "w", encoding="utf-8").write(content)
                created += 1

    # 3. Generate README.md from template
    readme_src = os.path.join(TEMPLATES_DOCS, "README.md")
    if os.path.exists(readme_src):
        content = render_template(readme_src, replacements)
        open(os.path.join(path, "README.md"), "w", encoding="utf-8").write(content)
        created += 1

    # 4. Generate .gitignore from template
    gitignore_src = os.path.join(TEMPLATES_DOCS, ".gitignore")
    if os.path.exists(gitignore_src):
        content = open(gitignore_src, "r", encoding="utf-8").read()
        os.makedirs(os.path.join(path, "其他"), exist_ok=True)
        open(os.path.join(path, "其他/.gitignore"), "w", encoding="utf-8").write(content)
        created += 1

    # 5. Generate derived files
    derived = {}
    derived["其他/.gitignore"] = (
        "# Project-specific\n__pycache__/\n*.pyc\n.DS_Store\nnode_modules/\n"
        "temp_*\ntest_*\n\n# Generated artifacts\n*.docx\n!设定/template.docx\n"
    )
    derived["其他/PROJECT.yaml"] = (
        'project:\n  name: "' + name + '"\n  version: 0.1.0\n  type: novel\n'
        '  genre: ' + genre + '\n  platform: \n  created: ' + replacements["date"] + '\n\n'
        'quality_gates:\n  after_each_chapter:\n    - audit_run.py --quick\n'
        '  after_each_arc:\n    - audit_run.py --full\n'
        '  final:\n    - final_verify.py\n'
    )
    derived["\u5176\u4ed6/\u8bb0\u5fc6\u951a\u70b9.md"] = (
        "# \u8bb0\u5fc6\u951a\u70b9\n\n"
        "> \u5168\u4e66\u72b6\u6001\u5feb\u7167\u3002\u6bcf\u6b21\u5199\u4f5c\u524d\u8bfb\u6b64\u6587\u4ef6\uff0830\u79d2\uff09\u6062\u590d\u4e0a\u4e0b\u6587\u3002\n\n"
        "## \u9879\u76ee\n- \u4f5c\u54c1\uff1a" + name + "\n- \u521d\u59cb\u5316\u65f6\u95f4\uff1a" + replacements["date"] + "\n\n"
        "## \u5f53\u524d\u6307\u9488\n- \u5f53\u524d\u5f27\u6bb5\uff1a\n- \u5f53\u524d\u7ae0\u8282\uff1a\n- \u4e3b\u89d2\u4f4d\u7f6e\uff1a\n\n"
        "## \u6d3b\u8dc3\u4f0f\u7b14\n\uff08\u7f16\u53f7+\u72b6\u6001\uff09\n\n"
        "## \u53e3\u5f84\u4ef2\u88c1\u8bb0\u5f55\n\uff08\u6b63\u6587\u4e0e\u5927\u7eb2\u4e0d\u4e00\u81f4\u65f6\u7684\u51b3\u7b56+\u65f6\u95f4\u6233\uff09\n"
    )
    derived["\u8bbe\u5b9a/_chapter_index.yaml"] = (
        "# " + name + " \u00b7 \u7ae0\u8282\u5173\u952e\u8bcd\u7d22\u5f15\n"
        "# \u6bcf\u8282\u5b8c\u6210\u6216\u5927\u7eb2\u8c03\u6574\u540e\u66f4\u65b0\u6b64\u6587\u4ef6\n"
        "# \u683c\u5f0f\uff1a\n# \u7b2c001\u7ae0:\n#   \u82821_\u7ae0\u8282\u540d: [\u5173\u952e\u8bcd1, \u5173\u952e\u8bcd2]\n"
    )
    derived["其他/_HANDOFF.md"] = (
        "# " + name + " \u00b7 \u9879\u76ee\u4ea4\u63a5\u6587\u6863\n\n"
        "> \u672c\u6587\u4ef6\u662f webnovel-studio skill \u7684\u4ea4\u63a5\u5165\u53e3\u3002\n"
        "> \u65b0\u63a5\u624b\u7684\u4eba\u6216\u56e2\u961f\u8bfb\u6b64\u6587\u4ef6\u5373\u53ef\u83b7\u53d6\u5168\u90e8\u63a5\u5165\u4fe1\u606f\u3002\n\n"
        "## \u4e00\u3001\u9879\u76ee\u6982\u51b5\n"
        "- \u4f5c\u54c1\u540d\u79f0\uff1a" + name + "\n"
        "- \u9879\u76ee\u8def\u5f84\uff1a" + path + "\n"
        "- \u521d\u59cb\u5316\u65f6\u95f4\uff1a" + replacements["date"] + "\n"
        "- \u7c7b\u578b/\u6d41\u6d3e\uff1a" + genre + "\n\n"
        "## \u4e8c\u3001\u6838\u5fc3\u8d44\u6e90\u8def\u5f84\n"
        "| \u8d44\u6e90 | \u8def\u5f84 |\n"
        "|------|------|\n"
        "| \u5199\u4f5c\u89c4\u5219 | AI\u6ce8\u610f\u4e8b\u9879\u53ca\u89c4\u5219/ |\n"
        "| \u8bbe\u5b9a\u6587\u6863 | \u8bbe\u5b9a/ |\n"
        "| \u6b63\u6587 | \u6b63\u6587/ |\n"
        "| \u5927\u7eb2 | \u8bbe\u5b9a/\uff08\u6309\u9879\u76ee\u7ed3\u6784\uff09 |\n"
        "| \u9879\u76ee\u7ea7\u811a\u672c | \u811a\u672c/ |\n\n"
        "## \u4e09\u3001\u5de5\u7a0b\u5316\u5de5\u4f5c\u6d41\n"
        "1. \u8bfb \u8bb0\u5fc6\u951a\u70b9.md \u6062\u590d\u72b6\u6001\uff0830\u79d2\uff09\n"
        "2. \u67e5 \u8bbe\u5b9a/_chapter_index.yaml \u786e\u8ba4\u5267\u60c5\u8282\u70b9\n"
        "3. \u5199\n"
        "4. \u8dd1 audit_run.py --quick\uff08P0\u5408\u89c4\u68c0\u67e5\uff09\n"
        "5. \u66f4\u65b0 \u8bb0\u5fc6\u951a\u70b9.md \u548c _chapter_index.yaml\n\n"
        "## \u56db\u3001Skill\u5173\u8054\n"
        "- base skill: webnovel-studio\uff08\u8def\u5f84\uff1a" + SKILL_DIR + "\uff09\n"
        "- \u901a\u7528\u811a\u672c\uff1awebnovel-studio/scripts/\n"
        "- \u89e6\u53d1\u5173\u952e\u8bcd\uff1a\u5199\u4f5c/\u5199\u6b63\u6587/\u7eed\u5199/\u5927\u7eb2/\u5ba1\u8ba1/\u68c0\u67e5/\u683c\u5f0f/\u4eba\u7269\u58f0\u97f3\n\n"
        "> **\u4ea4\u63a5\u5b8c\u6210\u3002**\n"
    )

    for rel_path, content in derived.items():
        full = os.path.join(path, rel_path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        open(full, "w", encoding="utf-8").write(content)
        created += 1

    # 6. Create empty directories
    for d in ["\u6b63\u6587", "\u62a5\u544a", "\u811a\u672c/\u5de5\u5177", "\u8bbe\u5b9a/md", "\u8bbe\u5b9a/docx_output", "\u5b58\u7a3f"]:
        os.makedirs(os.path.join(path, d), exist_ok=True)

    # 7. Print guide
    print()
    print("=" * 50)
    print("  " + name + " \u2014 \u9879\u76ee\u521d\u59cb\u5316\u5b8c\u6210")
    print("=" * 50)
    print("  \u8def\u5f84: " + path)
    print("  \u6587\u4ef6: " + str(created) + " \u4e2a")
    print("  \u7c7b\u578b: " + genre)
    print()
    print("  \u25b6 \u4e0b\u4e00\u6b65")
    print("  1. cd " + path)
    print('  2. $env:WEBNOVEL_PROJECT = "' + path.replace("\\", "\\\\") + '"')
    print("  3. \u9605\u8bfb AI\u6ce8\u610f\u4e8b\u9879\u53ca\u89c4\u5219/05_\u5feb\u901f\u63a5\u5165\u6307\u5357.md")
    print("  4. \u7f16\u8f91 PROJECT.yaml \u8865\u5145\u5e73\u53f0\u548c\u51fa\u7248\u4fe1\u606f")
    print("  5. \u5f00\u59cb\u5199\u4f5c")
    print()


if __name__ == "__main__":
    main()
