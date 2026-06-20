# -*- coding: utf-8 -*-
"""
GitHub 发布装逼 · github_deploy.py
==================================
用法：
  python scripts/git/github_deploy.py --init            初始化 remote
  python scripts/git/github_deploy.py --push --mode=full    推全量工程
  python scripts/git/github_deploy.py --push --mode=reader  只推正文
  python scripts/git/github_deploy.py --gen-readme          生成 README
  python scripts/git/github_deploy.py --deploy              一键装逼（init + push + gen-readme）
  python scripts/git/github_deploy.py --deploy --dual       双推（工程 + 正文分别到两个仓库）

环境变量：
  GITHUB_TOKEN     - GitHub token（创建仓库 / push 用，可选，没 token 时手动建 repo 也能用）
  WEBNOVEL_PROJECT - 项目根路径
"""

import os
import sys
import json
import shutil
import tempfile
import datetime
import argparse
import urllib.request
import urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _git_utils import (
    PROJECT, is_git_repo, get_changed_files, run_git,
    has_remote, get_current_branch, generate_commit_message
)

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
READER_BRANCH = "reader-output"


def _gh_api(method, path, data=None):
    """调用 GitHub REST API。"""
    if not GITHUB_TOKEN:
        return None
    url = f"https://api.github.com{path}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "webnovel-studio/0.5.0"
    }
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except (urllib.error.HTTPError, urllib.error.URLError, json.JSONDecodeError):
        return None


def get_repo_info():
    """从 git remote 解析 owner/repo。"""
    rc, out, _ = run_git(["remote", "get-url", "origin"])
    if rc != 0:
        return None
    url = out.strip()
    # 支持 git@github.com:owner/repo.git 和 https://github.com/owner/repo.git
    m = __import__("re").match(r"(?:git@github\.com:|https://github\.com/)([^/]+)/([^/.]+)", url)
    if m:
        return m.group(1), m.group(2).replace(".git", "")
    return None


def create_github_repo(repo_name, private=False):
    """在 GitHub 上创建仓库，返回 clone URL。"""
    if not GITHUB_TOKEN:
        print("没有 GITHUB_TOKEN，跳过 GitHub API 操作。请手动创建仓库。")
        return None
    data = {"name": repo_name, "private": private, "auto_init": False}
    result = _gh_api("POST", "/user/repos", data)
    if result and "clone_url" in result:
        print(f"GitHub 仓库已创建: {result['clone_url']}")
        return result["clone_url"]
    if result and "errors" in result:
        print(f"创建失败: {result['errors']}")
    return None


def generate_reader_readme():
    """为 reader 模式生成读者向 README。"""
    project_name = os.path.basename(PROJECT)

    # 尝试从现有文件收集信息
    synopsis = ""
    char_summary = ""
    word_count = 0
    chapters = []

    # 统计字数
    content_dir = os.path.join(PROJECT, "正文")
    if os.path.isdir(content_dir):
        for root, _, files in os.walk(content_dir):
            for f in sorted(files):
                if f.endswith(".md") or f.endswith(".docx"):
                    path = os.path.join(root, f)
                    with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                        text = fh.read()
                    word_count += len(text.replace(" ", "").replace("\n", ""))
                    rel = os.path.relpath(path, content_dir)
                    chapters.append((rel, len(text)))
        chapters = chapters[:20]  # 只展示最近20章

    wc_str = f"{word_count / 10000:.1f}" if word_count > 10000 else str(word_count)

    readme = f"""# {project_name}

> 一部正在连载的小说。

---

**进度**：{len(chapters)} 章 · 约 {wc_str} 万字 · 连载中

## 最近章节

"""
    for rel, length in chapters[-10:]:
        readme += f"- {rel}（{length} 字）\n"

    readme += f"""
---

*本作品由 webnovel-studio 工具链辅助创作。*
"""
    return readme


def generate_dev_readme():
    """为 full 模式生成开发者向 README。"""
    project_name = os.path.basename(PROJECT)

    # 统计概况
    dirs = []
    for d in ["正文", "设定", "脚本", "AI注意事项及规则", "人工检查", "其他"]:
        path = os.path.join(PROJECT, d)
        if os.path.isdir(path):
            count = len([f for root, _, fs in os.walk(path) for f in fs if f.endswith((".md", ".py", ".docx", ".yaml"))])
            dirs.append((d, count))

    dirstr = "\n".join(f"├── {d}/    ← {c}个文件" for d, c in sorted(dirs, key=lambda x: -x[1]))

    readme = f"""# {project_name}

> 网文写作工程项目。

---

## 目录结构

```
{project_name}/
{dirstr}
```

## 快速开始

```bash
$env:WEBNOVEL_PROJECT = "$(PROJECT.replace(os.sep, '/') if os.sep == '\\\\' else PROJECT)"
```

## 技术栈

- 工具链：webnovel-studio v0.5.0
- 审计：audit_run.py
- 编译：MD → DOCX
- 格式：方正仿宋 GB2312 · 公文标准
"""
    return readme


def push_full():
    """推全量工程到 main。"""
    if not has_remote():
        print("没有 remote，请先用 --init 设置。")
        return False

    branch = get_current_branch()
    rc, out, err = run_git(["push", "origin", branch])
    if rc == 0:
        print(f"全量工程已推送到 origin/{branch}")
        url = run_git(["remote", "get-url", "origin"])[1]
        print(f"链接: {url}")
        return True
    else:
        print(f"推送失败: {err}")
        return False


def push_reader():
    """只推正文到 reader 分支。"""
    content_dir = os.path.join(PROJECT, "正文")
    if not os.path.isdir(content_dir):
        print("没有找到 正文/ 目录，无法以 reader 模式发布。")
        return False

    if not has_remote():
        print("没有 remote，请先用 --init 设置。")
        return False

    reader_branch = READER_BRANCH

    # 1. 确保 reader 分支存在（用 orphan 方式创建）
    print(f"准备 reader 分支 ({reader_branch})...")
    run_git(["branch", "-D", reader_branch])  # 删除旧分支，忽略错误
    run_git(["checkout", "--orphan", reader_branch])
    run_git(["rm", "-rf", "."])  # 清空工作区

    # 2. 复制 正文/ 内容到根目录
    for item in os.listdir(content_dir):
        src = os.path.join(content_dir, item)
        dst = os.path.join(PROJECT, item)
        if os.path.isdir(src):
            shutil.copytree(src, dst, symlinks=False, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dst)

    # 3. 生成 README
    readme_content = generate_reader_readme()
    with open(os.path.join(PROJECT, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme_content)

    # 4. 提交
    run_git(["add", "-A"])
    rc, out, err = run_git(["commit", "-m", f"reader: {datetime.date.today().isoformat()} 更新"])
    if rc != 0:
        print(f"reader 分支提交失败: {err}")
        # 切回原分支
        run_git(["checkout", "-f", get_current_branch()])
        return False

    # 5. 推送到 reader 分支
    rc, out, err = run_git(["push", "-f", "origin", f"{reader_branch}:{reader_branch}"])
    if rc == 0:
        print(f"正文已推送到 origin/{reader_branch}")
        url = run_git(["remote", "get-url", "origin"])[1]
        print(f"阅读链接: {url.replace('.git', '')}/tree/{reader_branch}")
        # 切回原分支
        run_git(["checkout", "-f", get_current_branch()])
        return True
    else:
        print(f"reader 推送失败: {err}")
        run_git(["checkout", "-f", get_current_branch()])
        return False


def main():
    parser = argparse.ArgumentParser(description="GitHub 发布工具")
    parser.add_argument("--init", action="store_true", help="初始化 remote")
    parser.add_argument("--push", action="store_true", help="推送")
    parser.add_argument("--deploy", action="store_true", help="一键部署 (init + push + gen-readme)")
    parser.add_argument("--dual", action="store_true", help="双推（正文到 reader 分支 + 全量到 main）")
    parser.add_argument("--mode", choices=["reader", "full"], default="reader", help="发布模式")
    parser.add_argument("--repo", type=str, default=None, help="指定仓库名（--init 时用）")
    parser.add_argument("--private", action="store_true", help="创建私有仓库")
    parser.add_argument("--gen-readme", action="store_true", help="只生成 README")
    args = parser.parse_args()

    if not is_git_repo():
        print("错误：当前项目不是 git 仓库。")
        print("先执行: git init && git add -A && git commit -m \"initial\"")
        return

    # --gen-readme 单跑模式
    if args.gen_readme and not args.push and not args.deploy:
        if args.mode == "reader":
            print(generate_reader_readme())
        else:
            print(generate_dev_readme())
        return

    # --init
    if args.init or args.deploy:
        repo_name = args.repo or os.path.basename(PROJECT)
        print(f"初始化 remote...")

        # 尝试创建 GitHub repo
        clone_url = create_github_repo(repo_name, private=args.private)
        if clone_url:
            run_git(["remote", "remove", "origin"])
            run_git(["remote", "add", "origin", clone_url])
            print(f"remote 已设置: {clone_url}")
        else:
            existing = run_git(["remote", "get-url", "origin"])[1]
            if existing:
                print(f"已有 remote: {existing}")
            else:
                print(f"请手动创建 GitHub 仓库 \"{repo_name}\" 然后运行:")
                print(f"  git remote add origin https://github.com/YOUR_USER/{repo_name}.git")
                return

    # --push
    if args.push or args.deploy:
        if args.dual:
            print("\n=== 双推模式 ===")
            push_full()
            print("---")
            push_reader()
        elif args.mode == "reader":
            push_reader()
        else:
            push_full()

    # 打印远程信息
    url = run_git(["remote", "get-url", "origin"])[1] if has_remote() else None
    if url:
        print(f"\n远程仓库: {url}")


if __name__ == "__main__":
    main()

