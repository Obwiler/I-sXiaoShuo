# I'sXiaoShuo · 我的小说

> 工程化网文写作工具箱 —— 给 AI agent 用的全流程写作 skill
> 适配番茄 / 起点 / 晋江 / 知乎盐选 / UC / Webnovel

---

## 它能做什么

- 用一条命令初始化完整的小说项目骨架
- 提供审计脚本：P0 格式检查、逻辑链校验、角色声音一致性检查
- 模式自动路由（纯设定讨论 / 正文写作 / 全量工程审计）
- 项目状态缓存 + 章节关键词索引，降低百万字长篇小说上下文恢复成本
- 自进化机制：扫描历史教训，自动生成规范更新提案

## 快速开始

```bash
# 1. 初始化一个新项目
python scripts/init/init_project.py --name "我的小说" --path /path/to/project

# 2. 设置环境变量
$env:WEBNOVEL_PROJECT = "/path/to/project"

# 3. 写正文 → 审计 → 归档
#    读 其他/记忆锚点.md（30秒恢复状态）
#    写正文
#    python scripts/audit/audit_run.py --quick
#    更新 其他/记忆锚点.md
```

## 技能结构

```
webnovel-studio/
├── SKILL.md              ← 主入口，触发模式路由
├── scripts/              ← 脚本工具链（审计 / 清理 / DOCX 编译 / 自进化 / 初始化）
│   ├── audit/            ← 审计全家桶（P0/P1/P2 分层检查）
│   ├── clean/            ← 格式清理（破折号 / 不是而是 / 重复字）
│   ├── docx/             ← MD → DOCX 编译
│   ├── evolve/           ← 自进化（扫吸取教训 → 提修改提案）
│   └── init/             ← 新项目脚手架
├── templates/            ← 项目初始化模板
│   └── project-init/
│       ├── template_rules/   ← 规则模板（5 文件）
│       └── template_docs/    ← 文档模板
├── references/           ← 写作参考库（10 个 craft 模块 + 平台 / 质量 / 工程文档）
│   ├── craft/modules/    ← 10 个专项模块（开篇 / 对话 / 情节逻辑 / 反 AI 腔等）
│   ├── novel-writing/    ← 叙事规则引擎
│   ├── platform/         ← 各平台投稿指南
│   ├── quality/          ← AI 检测 / 连贯性 / 节奏检查
│   └── special/          ← 工程工作流 / 会话承接 / 记忆锚点
├── corpus/               ← 网文语料库（166 篇已爬取文章 + 打标签摘录）
└── demos/                ← 25 个不同主题的短篇 demo
```

## 三种模式

| 模式 | 触发场景 | 加载内容 |
|------|---------|---------|
| **A**（世界观） | 设定讨论 / 世界观构建 | 只读 `references/` |
| **B**（叙事） | 写正文 / 续写 / 对白 | `references/novel-writing/` + `AI注意事项及规则/` |
| **C**（工程） | 审计 / 检查 / 全量 | 模式 B + 项目级脚本 |

检测到项目目录下有 `其他/PROJECT.yaml` 或 `AI注意事项及规则/` 时，自动进入工程模式。

## 审计分层

| 层级 | 检查项 |
|------|--------|
| **P0**（致命） | 破折号 / 不是而是 / 中二体 / AI 衔接词 |
| **P1**（严重） | 引号规范 / 逗句比 1:0.5~0.8 |
| **P2**（建议） | 角色声音 / 生活细节 / 五要素完整性 |

单文件审计：`python scripts/audit/audit_run.py --target=文件路径`

## 环境变量

```bash
# 所有脚本统一使用
$env:WEBNOVEL_PROJECT = "/path/to/your/project"
```

未设置时 fallback 到当前目录。

## License

MIT
