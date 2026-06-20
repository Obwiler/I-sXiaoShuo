# I'sXiaoShuo · 爱小说

> 一个给 AI agent 用的网文写作工程工具箱。
> 名字梗：I'sXiaoShuo = 爱小说（love novels），不是什么高大上的品牌名，就是字面意思——爱写小说的人给自己搓的工具箱。
> 适配番茄 / 起点 / 晋江 / 知乎盐选 / UC / Webnovel

---

## 它能干嘛

- 一条命令初始化完整的小说项目骨架（目录 / 规则 / 交接文档 / 审计配置）
- 审计脚本跑一遍：P0 格式检查 + 逻辑链 + 角色声音一致性
- 自动识别你在干嘛：讨论设定就只读参考库，写正文就加载规范，跑审计就全量开火
- 百万字长篇的上下文救星：状态缓存 + 章节关键词索引，30 秒恢复"写到哪了"
- 自进化：扫吸取教训，自动提规范修改提案——你批了就改
- **写完自动提交**：git_snapshot.py 检测变更、自动生成提交信息
- **一键装逼到 GitHub**：github_deploy.py 双模式推送（读者只看正文 / 开发者看全量）

## 快速开始

```bash
# 搓一个新项目
python scripts/init/init_project.py --name "我的小说" --path /path/to/project

# 告诉脚本你的项目在哪
$env:WEBNOVEL_PROJECT = "/path/to/project"

# 然后就是：写 → 审 → 归档
#   读 其他/记忆锚点.md（30 秒）
#   写正文
#   python scripts/audit/audit_run.py --quick
#   python scripts/git/git_snapshot.py（自动提交）
#   更新 其他/记忆锚点.md
```

## 结构一览

```
webnovel-studio/
├── SKILL.md              ← 主入口，模式路由（agent 读这个就知道该干嘛）
├── scripts/
│   ├── audit/            ← 审计（P0/P1/P2 分层，单文件或全量）
│   ├── clean/            ← 格式清理（破折号 / 不是而是 / 重复字 / 字体修正）
│   ├── docx/             ← MD → DOCX 编译（唯一真相源是 MD）
│   ├── evolve/           ← 自进化（吸取教训 → 修改提案）
│   ├── git/              ← 【新增】git 检查点 + GitHub 发布
│   │   ├── git_snapshot.py   自动提交检测，写完一章程就提一次
│   │   ├── github_deploy.py  双模式发布（reader / full / dual）
│   │   └── _git_utils.py     公共函数
│   └── init/             ← 脚手架（--name --path --genre）
├── templates/            ← 初始化模板
│   └── project-init/     ← 规则模板 5 件套 + 文档模板
├── references/           ← 写作参考库（核心资产，10 个 craft 模块）
│   ├── craft/modules/    ← 10 个模块，每个 5 件套（README / bad&good / runtime / tutorial）
│   ├── novel-writing/    ← 叙事规则（6 方向）
│   ├── platform/         ← 各平台投稿（7 平台横向对比）
│   ├── quality/          ← AI 检测 / 连贯性 / 节奏（12 项量化指标）
│   └── special/          ← 工程工作流 / 会话承接 / 记忆锚点
├── corpus/               ← 166 篇网文 + 打标签摘录（当写作参考用，别拿去训练模型）
└── demos/                ← 25 个短篇 demo（证明这个库真的能写出东西）
```

## 三种模式

| 模式 | 什么时候触发 | 加载什么 |
|------|-------------|---------|
| **A**（世界观） | 聊设定 / 构建世界观 | 只读 references/ |
| **B**（叙事） | 写正文 / 续写 / 对白 | references/novel-writing/ + AI注意事项及规则/ |
| **C**（工程） | 审计 / 检查 / 全量 | 模式 B + 项目级脚本 |

项目目录下有 其他/PROJECT.yaml 或 AI注意事项及规则/ 的时候自动进入工程模式，不用手动切。

## 审计怎么用

```bash
# 快速检查（P0）：30 秒出报告
python scripts/audit/audit_run.py --quick

# 全量审计（P0+P1+P2+逻辑链+角色声音）
python scripts/audit/audit_run.py --full

# 单文件审计
python scripts/audit/audit_run.py --target=文件路径
```

| 层级 | 查什么 |
|------|--------|
| **P0**（抓出来骂） | 破折号 / 不是而是 / 中二体 / AI 衔接词 |
| **P1**（要认真改） | 引号规范 / 逗句比 1:0.5~0.8 |
| **P2**（建议修） | 角色声音 / 生活细节 / 五要素完整性 |

## git 自动检查点

```bash
# 写完一章跑这个，不用想提交信息怎么写
python scripts/git/git_snapshot.py

# 只看不变更
python scripts/git/git_snapshot.py --status

# 提交完直接推送
python scripts/git/git_snapshot.py --push
```

自动检测你改了哪些文件，按类别（正文/设定/脚本/规则）生成提交信息。没有变更就跳过，不打断工作流。

## GitHub 发布

```bash
# 初始化（第一次用）
python scripts/git/github_deploy.py --init

# 只推正文到 reader 分支——发给朋友看的
python scripts/git/github_deploy.py --push --mode=reader

# 推全量工程到 main——备份用的
python scripts/git/github_deploy.py --push --mode=full

# 一键装逼（双推：读者看正文，开发者看全量）
python scripts/git/github_deploy.py --deploy --dual
```

reader 模式创建一个干净分支，只包含正文文件夹 + 读者向 README。full 模式推全部项目文件到 main。

## 环境变量

```bash
# 所有脚本统一认这个
$env:WEBNOVEL_PROJECT = "/path/to/your/project"

# GitHub 发布需要这个（可选，手动建 repo 也行）
$env:GITHUB_TOKEN = "ghp_xxxxxxxxxxxx"
```

没设就 fallback 到当前目录。懒得设也行，就是别抱怨审计扫错了地方。

## License

MIT —— 随便用，写出来了记得请我喝奶茶。
