"""
角色声音指纹自查脚本
用法：python 脚本/审核检查/_audit_voice.py
功能：扫描正文文档中的对白，逐句对照7个核心角色声音指纹，标记AI漂移
"""
import re, os, sys

PROJECT = os.environ.get("WEBNOVEL_PROJECT") or os.getcwd()
from docx import Document

# 角色声音指纹定义
VOICE_PROFILES = {
    '李景宜': {
        'max_line_len': 10,        # 对外对白≤10字
        'max_inner_len': 15,       # 对内通信≤15字
        'forbidden_patterns': ['我觉得', '我感觉', '也许', '可能吧', '我想'],
        'preferred': '陈述句为主，无反问无设问无感慨',
        'signal': '沉默比说话多，能用动作回答不用语言'
    },
    '沈渡': {
        'max_line_len': 40,
        'forbidden_patterns': ['我觉得', '我感觉', '大概', '好像', '比喻来说'],
        'preferred': '像在读实验报告，用数据代替观点',
        'signal': '禁用比喻、夸张、倒装句'
    },
    '陆静澜': {
        'max_line_len': 50,
        'forbidden_patterns': ['我认为', '我决定', '我的态度是'],
        'preferred': '用"有人告诉我"代替"我认为"',
        'signal': '前置条件→限定词→结论结构'
    },
    '王志强': {
        'max_line_len': 30,
        'forbidden_patterns': [],
        'preferred': '冷幽默感——严肃语气说反话',
        'signal': '介于李景宜的冷和沈渡的学术之间'
    },
    '郑建国': {
        'max_line_len': 40,
        'forbidden_patterns': ['我个人的看法'],
        'preferred': '用"上面""上级"代替"我"',
        'signal': '永远在拉人上船'
    },
    '周维安': {
        'max_line_len': 50,
        'forbidden_patterns': ['算了', '随便吧'],
        'preferred': '语速随任务状态变化',
        'signal': '对李景宜的废话量远大于其他人'
    },
    '安德烈': {
        'max_line_len': 40,
        'forbidden_patterns': ['放弃吧', '没用的'],
        'preferred': '用具体动作代替表态',
        'signal': '行动型，话少但信息密度大'
    }
}

# 对话提取正则（双引号/书名号/特殊引号内的内容）
DIALOGUE_PATTERN = re.compile(r'[「」""][^「」""]{2,80}[「」""]')

def scan_document(filepath):
    """扫描单个文档，提取对白并检查"""
    if not os.path.exists(filepath):
        return []
    
    name = os.path.basename(filepath)
    issues = []
    
    if filepath.endswith('.md'):
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
        lines = text.split('\n')
    elif filepath.endswith('.docx'):
        doc = Document(filepath)
        lines = [p.text for p in doc.paragraphs if p.text]
    else:
        return []
    
    for line_idx, line in enumerate(lines):
        # Extract dialogue segments
        dialogues = DIALOGUE_PATTERN.findall(line)
        for d in dialogues:
            # Check each character's profile
            for char_name, profile in VOICE_PROFILES.items():
                if char_name in line[:20]:  # character name in context
                    # Check line length
                    clean_d = d.strip('「」""')
                    if len(clean_d) > profile['max_line_len']:
                        issues.append({
                            'file': name,
                            'line': line_idx + 1,
                            'character': char_name,
                            'issue': f'对白过长（{len(clean_d)}字 > {profile["max_line_len"]}字上限）',
                            'text': clean_d[:60]
                        })
                    # Check forbidden patterns
                    for fp in profile['forbidden_patterns']:
                        if fp in clean_d:
                            issues.append({
                                'file': name,
                                'line': line_idx + 1,
                                'character': char_name,
                                'issue': f'禁用词：{fp}',
                                'text': clean_d[:60]
                            })
    
    return issues

def main():
    # Scan project files
    scan_targets = [
        os.path.join(PROJECT, "正文"),
        os.path.join(PROJECT, "存稿"),
        os.path.join(PROJECT, "设定", "02_大纲章纲.docx"),
    ]
    
    all_issues = []
    for target in scan_targets:
        if os.path.isdir(target):
            for f in os.listdir(target):
                if f.endswith('.md') or f.endswith('.docx'):
                    fp = os.path.join(target, f)
                    all_issues.extend(scan_document(fp))
        elif os.path.isfile(target):
            all_issues.extend(scan_document(target))
    
    # Report
    if not all_issues:
        print('角色声音检查通过。所有对白匹配角色指纹。')
        return
    
    print(f'发现 {len(all_issues)} 处角色声音漂移：')
    print('---')
    for iss in all_issues:
        print(f"[{iss['file']}:L{iss['line']}] {iss['character']}: {iss['issue']}")
        print(f'  对白：「{iss["text"]}」')
        print()

if __name__ == '__main__':
    main()
