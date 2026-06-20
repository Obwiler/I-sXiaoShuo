"""
全量审计脚本
用法：python 脚本/审核检查/_audit_full.py
功能：依次运行所有审计检查，汇总报告
"""
import os, sys, subprocess, datetime

SCRIPTS_DIR = os.path.join(PROJECT, "脚本", "审核检查")
REPORT_DIR = os.path.join(PROJECT, "报告")

def run_audit(script_name, description):
    """运行单个审计脚本"""
    script_path = os.path.join(SCRIPTS_DIR, script_name)
    if not os.path.exists(script_path):
        print(f'  [跳过] {description} —— 脚本不存在：{script_name}')
        return {'script': script_name, 'status': 'skipped', 'output': ''}
    
    print(f'  [运行] {description} ...', end=' ')
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode == 0:
            print('通过')
            return {'script': script_name, 'status': 'pass', 'output': result.stdout}
        else:
            print('发现问题')
            return {'script': script_name, 'status': 'issues', 'output': result.stdout + result.stderr}
    except subprocess.TimeoutExpired:
        print('超时')
        return {'script': script_name, 'status': 'timeout', 'output': ''}
    except Exception as e:
        print(f'错误：{e}')
        return {'script': script_name, 'status': 'error', 'output': str(e)}

def main():
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    
    print('=== 全量审计 ===')
    print(f'时间：{timestamp}')
    print(f'工作目录：{SCRIPTS_DIR}')
    print()
    
    # Audit checklist
    audits = [
        ('_audit_not.py', '不是句式检查'),
        ('_audit_voice.py', '角色声音检查'),
        ('_audit_threads.py', '逻辑线索检查'),
        ('_audit_v2.py', 'v2审计'),
        ('_audit_phase3.py', '阶段3审计（设定总纲）'),
        ('_audit_phase3b.py', '阶段3b审计（世界观）'),
    ]
    
    results = []
    for script_name, description in audits:
        result = run_audit(script_name, description)
        results.append(result)
    
    # Summary
    print()
    print('=== 汇总 ===')
    passed = sum(1 for r in results if r['status'] == 'pass')
    issues = sum(1 for r in results if r['status'] == 'issues')
    skipped = sum(1 for r in results if r['status'] == 'skipped')
    errors = sum(1 for r in results if r['status'] in ('error', 'timeout'))
    
    print(f'通过：{passed}  发现问题：{issues}  跳过：{skipped}  错误：{errors}')
    print(f'总检查项：{len(audits)}')
    
    # Write report
    report_path = os.path.join(REPORT_DIR, f'全量审计_{timestamp}.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f'# 全量审计报告 · {timestamp}\n\n')
        f.write(f'| 脚本 | 状态 |\n')
        f.write(f'|------|------|\n')
        for r in results:
            status_emoji = {'pass': '通过', 'issues': '发现问题', 'skipped': '跳过', 'error': '错误', 'timeout': '超时'}
            f.write(f'| {r["script"]} | {status_emoji.get(r["status"], r["status"])} |\n')
            if r['output']:
                f.write(f'\n输出：\n```\n{r["output"][:500]}\n```\n\n')
    
    print(f'\n报告已写入：{report_path}')

if __name__ == '__main__':
    main()
