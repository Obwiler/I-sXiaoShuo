# -*- coding: utf-8 -*-
"""
GitHub 发布装逼 · github_deploy.py
==================================
用法：
  python scripts/git/github_deploy.py --init [--private]           初始化 remote
  python scripts/git/github_deploy.py --push --mode=full           推全量工程
  python scripts/git/github_deploy.py --push --mode=reader         只推正文到 reader-output 分支
  python scripts/git/github_deploy.py --deploy --dual [--private]  双推（正文+工程分别到两个仓库）
  python scripts/git/github_deploy.py --deploy --dual --author=Id  双推，指定作者Id

双推仓库命名规则（书名 → 项目名拼音）：
  reader:     {书名}-ZhengWen-{作者Id}           例：AoBeiWeiLe-ZhengWen-Obwiler
  engineering:{书名}-GongCheng-{作者Id}           例：AoBeiWeiLe-GongCheng-Obwiler

环境变量：
  GITHUB_TOKEN / GH_TOKEN - GitHub token
  WEBNOVEL_PROJECT        - 项目根路径

限制：
  - GitHub 不支持中文仓库名，拼音转写替代
  - gh CLI 需要先认证（gh auth login）或用 GH_TOKEN
"""
import os, sys, json, shutil, tempfile, datetime, argparse, urllib.request, urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _git_utils import PROJECT, is_git_repo, run_git, has_remote, get_current_branch


# ── 辅助函数 ─────────────────────────────────────────────────


def _run(args, cwd=None):
    """执行外部命令。"""
    import subprocess
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=60, cwd=cwd)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except FileNotFoundError:
        return -1, "", "command not found"
    except subprocess.TimeoutExpired:
        return -1, "", "timeout"


def _gh_user():
    """获取 GitHub 用户名。"""
    rc, out, _ = _run(["gh", "api", "user", "--jq", ".login"])
    if rc == 0 and out.strip():
        return out.strip()
    token = os.environ.get("GH_TOKEN", "") or os.environ.get("GITHUB_TOKEN", "")
    if token:
        req = urllib.request.Request(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {token}", "User-Agent": "webnovel-studio/1.0"},
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read().decode()).get("login", "YOUR_USER")
        except Exception:
            pass
    return "YOUR_USER"


def _repo_url(owner, name):
    return f"https://github.com/{owner}/{name}.git"


def _auth_url(remote_url):
    """给 URL 注入 token 用于推送。"""
    token = os.environ.get("GH_TOKEN", "") or os.environ.get("GITHUB_TOKEN", "")
    if token and remote_url.startswith("https://"):
        user = _gh_user()
        return remote_url.replace("https://", f"https://{user}:{token}@")
    return remote_url


# ── 创建 + 删除仓库 ──────────────────────────────────────────


def create_repo(repo_name, private=False):
    """在 GitHub 上创建仓库，支持 gh CLI / API / 手动指引三路。"""
    # 方法1: gh CLI
    vis = "--private" if private else "--public"
    rc, out, err = _run(["gh", "repo", "create", repo_name, vis])
    if rc == 0:
        url = _repo_url(_gh_user(), repo_name)
        print(f"gh CLI 创建成功: {url}")
        return url
    if "name already exists" in err.lower():
        print(f"仓库名 \"{repo_name}\" 已被占用（可能是上次创建未完成的幽灵仓库）。")
        print(f"解决方法：打开 https://github.com/{_gh_user()}?tab=repositories")
        print(f"  找到同名仓库并删除，然后重试。")
        return None

    # 方法2: API
    token = os.environ.get("GH_TOKEN", "") or os.environ.get("GITHUB_TOKEN", "")
    if token:
        data = json.dumps({"name": repo_name, "private": private}).encode()
        req = urllib.request.Request(
            "https://api.github.com/user/repos", data=data,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json", "User-Agent": "webnovel-studio/1.0"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                result = json.loads(resp.read().decode())
                print(f"API 创建成功: {result['clone_url']}")
                return result["clone_url"]
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            if "name already exists" in body:
                print(f"仓库名 \"{repo_name}\" 已被占用（幽灵仓库）。删除后重试。")
            else:
                print(f"API 创建失败 (HTTP {e.code}): {body[:200]}")
            return None

    # 方法3: 手动指引
    print("\n无法自动创建，请手动操作：")
    print(f"  1. 打开 https://github.com/new")
    print(f"  2. 仓库名：{repo_name}")
    print(f"  3. git remote add origin {_repo_url('YOUR_USER', repo_name)}")
    print(f"  4. git push -u origin main")
    return None


def set_repo_visibility(repo_full_name, private=True):
    """设置仓库可见性。"""
    token = os.environ.get("GH_TOKEN", "") or os.environ.get("GITHUB_TOKEN", "")
    if not token:
        print(f"跳过权限设置（无 token），请手动到 GitHub 仓库 Settings 页面修改。")
        return False
    data = json.dumps({"private": private}).encode()
    req = urllib.request.Request(
        f"https://api.github.com/repos/{repo_full_name}", data=data,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json", "User-Agent": "webnovel-studio/1.0"},
        method="PATCH",
    )
    try:
        with urllib.request.urlopen(req, timeout=15):
            status = "私有" if private else "公开"
            print(f"仓库 {repo_full_name} 已设为 {status}")
            return True
    except urllib.error.HTTPError as e:
        print(f"设置可见性失败 (HTTP {e.code}): 需要 Administration 权限")
        return False


# ── 命名生成 ──────────────────────────────────────────────────


def make_repo_names(project_name, author_id):
    """生成双仓库命名。GitHub 不支持中文，用拼音转写。"""
    # 取项目名拼音或直接使用 basename
    name = os.path.basename(project_name) if os.path.isdir(project_name) else project_name
    # 保留非中文英文部分，中文用拼音替换
    # 简单方案：去掉非 ASCII 字符后用英文部分
    slug = "".join(c for c in name if c.isascii() and c.isalnum() or c in "-_")
    if not slug:
        slug = "Novel"  # 全中文名时的 fallback
    aid = author_id or _gh_user()
    return {
        "reader": f"{slug}-ZhengWen-{aid}",
        "engineer": f"{slug}-GongCheng-{aid}",
    }


# ── README 生成 ──────────────────────────────────────────────


def generate_reader_readme():
    """生成读者向 README。"""
    pname = os.path.basename(PROJECT)
    content_dir = os.path.join(PROJECT, "正文")
    wc, chapters = 0, []
    if os.path.isdir(content_dir):
        for root, _, files in os.walk(content_dir):
            for f in sorted(files):
                if f.endswith((".md", ".docx")):
                    text = open(os.path.join(root, f), "r", encoding="utf-8", errors="ignore").read()
                    c = len(text.replace(" ", "").replace("\n", ""))
                    wc += c
                    chapters.append((os.path.relpath(os.path.join(root, f), content_dir), c))
    wcs = f"{wc/10000:.1f}" if wc > 10000 else str(wc)
    lines = "\n".join(f"- {rel}（{c} 字）" for rel, c in chapters[-10:])
    return f"""# {pname}

> 一部正在连载的小说。

---

**进度**：{len(chapters)} 章 · 约 {wcs} 万字 · 连载中

## 最近章节

{lines}

---

*本作品由 webnovel-studio 工具链辅助创作。*
"""


def generate_dev_readme():
    """生成开发者向 README。"""
    pname = os.path.basename(PROJECT)
    dirs = []
    for d in ["正文", "设定", "脚本", "AI注意事项及规则", "人工检查", "其他"]:
        p = os.path.join(PROJECT, d)
        if os.path.isdir(p):
            count = len([f for r, _, fs in os.walk(p) for f in fs if f.endswith((".md", ".py", ".docx", ".yaml"))])
            dirs.append((d, count))
    ds = "\n".join(f"├── {d}/    ← {c}个文件" for d, c in sorted(dirs, key=lambda x: -x[1]))
    return f"""# {pname}

> 网文写作工程项目。

---

## 目录结构

```
{pname}/
{ds}
```

## 技术栈

- 工具链：webnovel-studio v1.0.0
- 审计：audit_run.py
- 编译：MD → DOCX
- 格式：方正仿宋 GB2312 · 公文标准
"""


# ── 推送 ─────────────────────────────────────────────────────


def push_to_remote(tmp_dir, remote_url, branch="main", force=False):
    """从临时目录推送到指定 remote。"""
    auth = _auth_url(remote_url)
    _run(["git", "init"], cwd=tmp_dir)
    _run(["git", "config", "user.email", "novel@webnovel-studio"], cwd=tmp_dir)
    _run(["git", "config", "user.name", "webnovel-studio"], cwd=tmp_dir)
    _run(["git", "add", "-A"], cwd=tmp_dir)
    rc, _, err = _run(["git", "commit", "-m", f"update: {datetime.date.today().isoformat()}"], cwd=tmp_dir)
    if rc != 0:
        if "nothing to commit" in err:
            print("没有新内容可推。")
            return True
        print(f"提交失败: {err}")
        return False
    _run(["git", "remote", "add", "origin", auth], cwd=tmp_dir)
    f = "-f" if force else ""
    rc, out, err = _run(["git", "push", f, "origin", f"main:{branch}"] if f
                        else ["git", "push", "origin", f"main:{branch}"], cwd=tmp_dir)
    if rc == 0:
        print(f"推送成功到 {remote_url}")
        return True
    print(f"推送失败: {err}")
    return False


def push_full():
    """推全量工程到当前 remote。"""
    if not has_remote():
        print("没有 remote，跳过。")
        return False
    branch = get_current_branch()
    rc, out, err = run_git(["push", "origin", branch])
    if rc == 0:
        print(f"全量工程已推送到 origin/{branch}")
        return True
    print(f"推送失败: {err}")
    return False


def push_reader(target_url=None):
    """只推正文到指定远程仓库（或当前 remote 的 reader-output 分支）。"""
    content_dir = os.path.join(PROJECT, "正文")
    if not os.path.isdir(content_dir):
        print("没有找到 正文/ 目录。")
        return False

    tmp = tempfile.mkdtemp(prefix="wv-reader-")
    try:
        for item in os.listdir(content_dir):
            s = os.path.join(content_dir, item)
            d = os.path.join(tmp, item)
            (shutil.copytree(s, d, dirs_exist_ok=True) if os.path.isdir(s) else shutil.copy2(s, d))
        readme = generate_reader_readme()
        with open(os.path.join(tmp, "README.md"), "w", encoding="utf-8") as f:
            f.write(readme)

        if target_url:
            ok = push_to_remote(tmp, target_url, branch="main", force=True)
        else:
            rc, url, _ = run_git(["remote", "get-url", "origin"])
            if rc != 0:
                print("没有 remote。")
                return False
            ok = push_to_remote(tmp, url, branch="reader-output", force=True)
        shutil.rmtree(tmp, ignore_errors=True)
        return ok
    except Exception as e:
        print(f"reader 发布异常: {e}")
        shutil.rmtree(tmp, ignore_errors=True)
        return False


# ── 双推工作流 ──────────────────────────────────────────────


def dual_deploy(author_id, private_eng=False):
    """双推：正文 → ZhengWen 仓库，全量 → GongCheng 仓库。"""
    names = make_repo_names(PROJECT, author_id)
    user = _gh_user()
    print(f"\n仓库命名方案：")
    print(f"  reader:     {names['reader']}")
    print(f"  engineer:   {names['engineer']}")
    print()

    # 1. 创建/确认 reader 仓库
    reader_url = create_repo(names["reader"], private=False)
    if not reader_url:
        reader_url = _repo_url(user, names["reader"])
        print(f"  reader 仓库可能已存在，尝试直接推送: {reader_url}")

    # 2. 推正文到 reader 仓库
    print("\n--- 推送正文 ---")
    push_reader(target_url=reader_url)

    # 3. 创建工程仓库（私有）
    print("\n--- 设置工程仓库 ---")
    eng_url = create_repo(names["engineer"], private=private_eng)
    if eng_url:
        # 设置 remote
        run_git(["remote", "remove", "origin"])
        run_git(["remote", "add", "origin", eng_url])
        # 推全量
        print("\n--- 推送工程 ---")
        push_full()
        # 确保私有
        if private_eng:
            set_repo_visibility(f"{user}/{names['engineer']}", private=True)
    else:
        print(f"工程仓库创建失败，请检查。")

    print(f"\n--- 完成 ---")
    print(f"reader:     {_repo_url(user, names['reader'])}")
    print(f"engineer:   {_repo_url(user, names['engineer'])}")


# ── CLI ──────────────────────────────────────────────────────


def main():
    p = argparse.ArgumentParser(description="GitHub 发布工具")
    p.add_argument("--init", action="store_true", help="初始化 remote")
    p.add_argument("--push", action="store_true", help="推送")
    p.add_argument("--deploy", action="store_true", help="一键部署")
    p.add_argument("--dual", action="store_true", help="双推（正文+工程到两个独立仓库）")
    p.add_argument("--mode", choices=["reader", "full"], default="reader", help="发布模式")
    p.add_argument("--author", type=str, default=None, help="作者Id（用于仓库命名）")
    p.add_argument("--repo", type=str, default=None, help="指定仓库名")
    p.add_argument("--private", action="store_true", help="工程仓库设为私有")
    p.add_argument("--gen-readme", action="store_true", help="只生成 README")
    args = p.parse_args()

    if not is_git_repo():
        print("错误：当前目录不是 git 仓库。先 git init。")
        return

    # 只生成 README
    if args.gen_readme and not args.push and not args.deploy:
        print(generate_reader_readme() if args.mode == "reader" else generate_dev_readme())
        return

    # ====== 双推模式 ======
    if args.dual and (args.deploy or args.push):
        dual_deploy(args.author, private_eng=args.private)
        return

    # ====== 单推模式（legacy） ======
    if args.init or args.deploy:
        repo_name = args.repo or os.path.basename(PROJECT)
        url = create_repo(repo_name, private=args.private)
        if url:
            run_git(["remote", "remove", "origin"])
            run_git(["remote", "add", "origin", url])
        else:
            existing = run_git(["remote", "get-url", "origin"])[1]
            if not existing:
                return

    if args.push or args.deploy:
        if args.mode == "reader":
            push_reader()
        else:
            push_full()

    url = run_git(["remote", "get-url", "origin"])[1] if has_remote() else None
    if url:
        print(f"\n远程仓库: {url}")


if __name__ == "__main__":
    main()
