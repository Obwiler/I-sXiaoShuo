# Skill 跨环境交接手册（Skill Handoff）

> 将 webnovel-studio 迁移到另一个 Codex 环境或交给另一个团队使用。
> 本文件是技能本身的"安装说明书"和"使用者手册"。

---

## 一、技能总览

**名称：** webnovel-studio（网文工坊）
**定位：** 中文网文全流程生产工具，覆盖选题→大纲→开篇→正文→爽点→章末→去AI味→投稿签约
**适配平台：** 番茄/起点/晋江/知乎盐选/UC/Webnovel
**依赖条件：** 无外部依赖。技能文件全部自包含于 Codex skills 目录。

---

## 二、目录结构

```
webnovel-studio/
├── SKILL.md                            ← 技能主入口，路由表+全流程定义+工作纪律
│
├── references/                         ← 知识库
│   ├── platform/                       ← 平台策略（6平台档案/字数标准/投稿指南）
│   │   ├── platform-profiles.md
│   │   ├── length-standards.md
│   │   ├── submission-guide.md
│   │   └── channel-guide.md
│   │
│   ├── craft/                          ← 写作工艺（钩子/爽点/大纲/对白/世界观...）
│   │   ├── hook-library.md
│   │   ├── trope-library.md
│   │   ├── modules/ (10个子模块)
│   │   └── ... (14个文件)
│   │
│   ├── quality/                        ← 质量控制（AI检测/去AI味/连贯检查/敏感词）
│   │   ├── ai-detector.md
│   │   ├── anti-ai-checklist.md
│   │   ├── human-texture.md
│   │   └── ... (共8个文件)
│   │
│   └── special/                        ← 项目管理（会话承接/记忆锚点/文件管理/工程化）
│       ├── session-handoff.md          ← AI会话承接协议
│       ├── memory-anchor.md            ← 记忆锚点系统
│       ├── file-management.md          ← 文件目录规范
│       ├── engineering-workflow.md     ← 工程化写作工作流（git+质量门）
│       ├── project-memory.md           ← 创作档案系统
│       ├── skill-handoff.md            ← ← 本文件
│       └── ... (英文出海/同人/短剧/热梗)
│
├── corpus/                             ← 语料库（166篇爆款章节节选）
│   ├── data/articles/
│   ├── analysis/
│   └── scripts/search_corpus_examples.py
│
└── demos/                              ← 示例作品（25篇短篇demo + 中长篇demo）
```

---

## 三、安装到新环境

### 方式一：完整复制（推荐）

1. 将 `webnovel-studio/` 整个目录复制到目标 Codex 环境的 `skills/` 目录下
2. 在目标环境的 Codex 配置中启用该 skill
3. 验证：新会话中提及"写小说""番茄""签约"等关键词时，skill 自动触发

### 方式二：最小安装（仅保留核心）

如果不需要语料库和示例作品：

```
webnovel-studio/
├── SKILL.md
└── references/
    ├── platform/
    ├── craft/
    ├── quality/
    └── special/
```

删除 `corpus/` 和 `demos/` 目录。核心功能不受影响。

---

## 四、在新环境创建一个项目

### 项目初始化清单

1. 创建项目根目录，如 `E:\ZhuoMian\奥贝维勒\`
2. 创建 `项目承接.md`（模板见 `session-handoff.md`）
3. 创建 `记忆锚点.md`（模板见 `memory-anchor.md`）
4. 按 `file-management.md` 创建标准目录树
5. （可选）创建 `PROJECT.yaml` 启用工程化工作流
6. 在 `AI注意事项及规则/` 下创建项目专属规则文件

### 最小项目骨架

```
《书名》/
├── 项目承接.md
├── 记忆锚点.md
├── 设定/         (00-04 docx)
├── 正文/         (第1卷/)
├── 存稿/         (待修改章节/)
├── 已发布/       (按平台分目录/)
├── 工程/         (进度日志/改稿记录/)
└── AI注意事项及规则/  (项目专属规则，按需创建)
```

---

## 五、跨团队交接清单

当将 skill + 项目同时移交给另一个团队时：

### Skill 层

- [ ] 整个 `webnovel-studio/` 目录已压缩打包或复制的目标环境
- [ ] 目标环境的 Codex 已启用该 skill
- [ ] 新团队已阅读 `SKILL.md` 了解路由和全流程
- [ ] `references/special/skill-handoff.md`（本文）提供给新团队作为手册

### 项目层

- [ ] `项目承接.md` 已更新（包含当前进度、阻塞项、特殊提醒）
- [ ] `记忆锚点.md` 已更新（全书七段快照完整）
- [ ] `工程/进度日志.md` 包含完整的历史记录
- [ ] `AI注意事项及规则/` 中所有文件已是最新版本
- [ ] `设定/` 下所有 .docx 文件已存档并推送
- [ ] `PROJECT.yaml`（如使用工程化工作流）已更新
- [ ] 所有未完成的修改已 commit 到 git

### 验证

新团队完成交接后，运行以下检查确认环境就绪：
1. 在根目录下找到 `项目承接.md` 和 `记忆锚点.md`
2. 阅读 `SKILL.md` 了解路由（写开头→references/craft/modules/opening/）
3. 尝试执行一次"打开项目"流程（读 项目承接.md → 记忆锚点.md → 快速接入指南.md）
4. 尝试写一章并跑一次质量门检查
