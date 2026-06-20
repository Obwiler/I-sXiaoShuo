# -*- coding: utf-8 -*-
"""
git 公共工具 · _git_utils.py
===========================
git_snapshot.py 和 github_deploy.py 共享的函数。
"""

import os
import re
import subprocess
import datetime

PROJECT = os.environ.get("WEBNOVEL_PROJECT") or os.getcwd()


def run_git(args, cwd=None):
    """执行 git 命令，返回 (returncode, stdout, stderr)。"""
    cmd = ["git"] + args
    cwd = cwd or PROJECT
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, timeout=30)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except FileNotFoundError:
        return -1, "", "git not found"
    except subprocess.TimeoutExpired:
        return -1, "", "git timeout"


def is_git_repo():
    """检查当前项目是否在 git 仓库内。"""
    rc, _, _ = run_git(["rev-parse", "--git-dir"])
    return rc == 0


def get_changed_files():
    """获取已修改/新增/删除的文件列表。
    返回: [(status, path), ...]   status: M/A/D/R
    """
    rc, out, _ = run_git(["status", "--porcelain"])
    if rc != 0:
        return []
    files = []
    for line in out.split("\n"):
        if not line.strip():
            continue
        status = line[:2].strip()
        path = line[3:].strip()
        if status:
            files.append((status[0], path))
    return files


def classify_file(path):
    """根据路径判断文件类别：正文/设定/脚本/规则/其他"""
    p = path.replace("\\", "/")
    if p.startswith("正文/") or p.startswith("正文\\"):
        return "正文"
    if p.startswith("设定/") or p.startswith("设定\\"):
        return "设定"
    if p.startswith("脚本/") or p.startswith("脚本\\"):
        return "脚本"
    if p.startswith("AI注意事项及规则/") or p.startswith("AI注意事项及规则\\"):
        return "规则"
    if p.startswith("其他/") or p.startswith("其他\\"):
        return "项目管理"
    if p.startswith("报告/"):
        return "报告"
    return "其他"


def classify_changes(changed_files):
    """按类别分组变更文件。
    返回: {类别: [(status, path), ...], ...}
    """
    groups = {}
    for status, path in changed_files:
        cat = classify_file(path)
        groups.setdefault(cat, []).append((status, path))
    return groups


def generate_commit_message(changed_files):
    """根据变更文件自动生成 commit message。"""
    groups = classify_changes(changed_files)

    parts = []
    for cat in ["正文", "设定", "规则", "脚本", "项目管理"]:
        items = groups.get(cat, [])
        if not items:
            continue
        # 统计操作类型
        stats = {"M": 0, "A": 0, "D": 0}
        for s, _ in items:
            stats[s] = stats.get(s, 0) + 1
        desc_parts = []
        if stats["A"]:
            desc_parts.append(f"新增{stats['A']}")
        if stats["M"]:
            desc_parts.append(f"修改{stats['M']}")
        if stats["D"]:
            desc_parts.append(f"删除{stats['D']}")
        desc = "、".join(desc_parts) if desc_parts else "更新"
        # 取有意义的文件名摘要
        paths = [p for _, p in items[:3]]
        detail = ", ".join(paths)
        if len(items) > 3:
            detail += f" 等{len(items)}个文件"
        parts.append(f"[{cat}] {desc} - {detail}")

    if not parts:
        return "chore: 常规更新"

    # 头行：短摘要
    subject_parts = []
    for cat in ["正文", "设定", "规则", "脚本", "项目管理"]:
        items = groups.get(cat, [])
        if not items:
            continue
        count = len(items)
        subject_parts.append(f"{cat}{count}")
    subject = " ".join(subject_parts) if subject_parts else "更新"

    # 找章节信息
    chapter_info = ""
    for _, path in changed_files:
        m = re.search(r"Ch(\d{3})", path)
        if m:
            chapter_info = f"Ch{m.group(1)} "
            break

    now = datetime.datetime.now().strftime("%m-%d %H:%M")
    first_line = f"{chapter_info}{subject}"

    body = "\n".join(parts)
    return f"{first_line}\n\n{body}"


def get_remote_url():
    """获取 origin remote 地址，没有则返回 None。"""
    rc, out, _ = run_git(["remote", "get-url", "origin"])
    return out if rc == 0 else None


def get_current_branch():
    """获取当前分支名。"""
    rc, out, _ = run_git(["rev-parse", "--abbrev-ref", "HEAD"])
    return out if rc == 0 else "main"


def has_remote():
    """检查是否有 remote。"""
    rc, _, _ = run_git(["remote"])
    return rc == 0
