# -*- coding: utf-8 -*-
"""
git 自动检查点 · git_snapshot.py
===============================
用法：
  python scripts/git/git_snapshot.py              自动检测变更并提交
  python scripts/git/git_snapshot.py --status     只看不变更
  python scripts/git/git_snapshot.py --message=x  手动指定提交信息
  python scripts/git/git_snapshot.py --push       提交后推送

集成位置：每次 audit_run.py 之后自动调用。
没有变更就静默跳过，不打断工作流。
"""

import os
import sys
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _git_utils import (
    PROJECT, is_git_repo, get_changed_files,
    generate_commit_message, run_git, has_remote
)


def main():
    parser = argparse.ArgumentParser(description="git 自动检查点")
    parser.add_argument("--status", action="store_true", help="只看状态，不变更")
    parser.add_argument("--message", "-m", type=str, default=None, help="手动指定提交信息")
    parser.add_argument("--push", action="store_true", help="提交后推送")
    args = parser.parse_args()

    if not is_git_repo():
        print("项目不是 git 仓库，跳过自动提交。")
        return

    changed = get_changed_files()
    if not changed:
        print("没有变更，跳过。")
        return

    if args.status:
        print(f"检测到 {len(changed)} 个变更文件：")
        groups = {}
        for s, p in changed:
            from _git_utils import classify_file
            cat = classify_file(p)
            groups.setdefault(cat, []).append((s, p))
        for cat, items in sorted(groups.items()):
            print(f"  [{cat}]")
            for s, p in items:
                label = {"M": "修改", "A": "新增", "D": "删除", "R": "重命名"}.get(s, s)
                print(f"    {label}  {p}")
        return

    msg = args.message or generate_commit_message(changed)

    # git add
    print(f"提交 {len(changed)} 个文件...")
    rc, _, err = run_git(["add", "-A"])
    if rc != 0:
        print(f"git add 失败: {err}")
        return

    # git commit
    rc, out, err = run_git(["commit", "-m", msg])
    if rc != 0:
        if "nothing to commit" in err:
            print("没有变更，跳过。")
            return
        print(f"git commit 失败: {err}")
        return
    print(f"已提交: {out.split(chr(10))[0] if chr(10) in out else out}")

    # git push (可选)
    if args.push:
        if not has_remote():
            print("没有配置 remote，跳过推送。")
            print(f"推送命令: git push origin HEAD")
            return
        branch = run_git(["rev-parse", "--abbrev-ref", "HEAD"])[1]
        rc, _, err = run_git(["push", "origin", branch])
        if rc == 0:
            print(f"已推送到 origin/{branch}")
        else:
            print(f"推送失败: {err}")


if __name__ == "__main__":
    main()
