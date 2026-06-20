# -*- coding: utf-8 -*-
"""
统一审计入口 · audit_run.py
===========================
用法：python 脚本/审核检查/audit_run.py
      可选参数 --quick：仅P0检查（快速模式）
      可选参数 --report：输出报告到 报告/ 目录
      可选参数 --target=PATH：审计指定文件而非全文

审计层级：
  P0（致命） → 破折号/不是而是/中二体/AI衔接词
  P1（严重） → 引号规范/逗句比/战斗规范
  P2（建议） → 角色声音/生活细节

输出：
  - stdout：实时进度
  - 报告/统一审计_YYYYMMDD_HHMMSS.md：详细报告（带 --report 时）
  - exit code: 0=全部通过, 1=发现问题
"""

import os
import sys
import datetime
import subprocess
import re

PROJECT = os.environ.get("WEBNOVEL_PROJECT") or os.getcwd()
SCRIPTS_DIR = os.path.join(PROJECT, "脚本", "审核检查")
REPORT_DIR = os.path.join(PROJECT, "报告")

QUICK_MODE = "--quick" in sys.argv
WRITE_REPORT = "--report" in sys.argv
TARGET_FILE = None
for a in sys.argv:
    if a.startswith("--target="):
        TARGET_FILE = a.split("=", 1)[1]

class AuditRunner:
    def __init__(self):
        self.results = {
            "P0": [],
            "P1": [],
            "P2": []
        }
        self.start_time = datetime.datetime.now()
    
    def check_p0(self):
        """P0检查：致命问题"""
        checks = []
        
        # 1. 破折号检查（直接正则扫描）
        checks.append(("破折号检查", self._check_dash))
        
        # 2. 不是而是检查
        checks.append(("不是句式检查", self._check_notbut))
        
        # 3. 中二体检查（精确数字、身体超常、标签化词）
        checks.append(("中二体检查", self._check_zhonger))
        
        # 4. AI衔接词检查
        checks.append(("AI衔接词检查", self._check_ai_transition))
        
        for name, func in checks:
            self._run_p0(name, func)
    
    def check_p1(self):
        """P1检查：硬性要求"""
        if QUICK_MODE:
            print("  [跳过P1] 快速模式")
            return
        
        checks = []
        checks.append(("引号规范检查", self._check_quotes))
        checks.append(("逗句比检查", self._check_comma_period_ratio))
        
        for name, func in checks:
            self._run_p1(name, func)
    
    def check_p2(self):
        """P2检查：建议遵守"""
        if QUICK_MODE:
            print("  [跳过P2] 快速模式")
            return
        
        checks = []
        checks.append(("现有审计脚本", self._run_existing_audit_scripts))
        
        for name, func in checks:
            self._run_p2(name, func)
    
    def _get_target_text(self):
        """获取待审计文本"""
        if TARGET_FILE and os.path.exists(TARGET_FILE):
            try:
                return open(TARGET_FILE, encoding="utf-8").read()
            except:
                return ""
        return None  # 全文模式
    
    def _run_p0(self, name, func):
        print(f"  [P0] {name} ...", end=" ")
        try:
            issues = func()
            if issues:
                self.results["P0"].append({"name": name, "issues": issues, "status": "issues"})
                print(f"发现问题 ({len(issues)}处)")
                for i in issues[:3]:
                    print(f"    例: {i[:60]}")
                if len(issues) > 3:
                    print(f"    ... 共{len(issues)}处")
            else:
                self.results["P0"].append({"name": name, "issues": [], "status": "pass"})
                print("通过")
        except Exception as e:
            self.results["P0"].append({"name": name, "issues": [str(e)], "status": "error"})
            print(f"错误: {e}")
    
    def _run_p1(self, name, func):
        print(f"  [P1] {name} ...", end=" ")
        try:
            issues = func()
            if issues:
                self.results["P1"].append({"name": name, "issues": issues, "status": "issues"})
                print(f"发现问题 ({len(issues)}处)")
                for i in issues[:3]:
                    print(f"    例: {i[:60]}")
            else:
                self.results["P1"].append({"name": name, "issues": [], "status": "pass"})
                print("通过")
        except Exception as e:
            self.results["P1"].append({"name": name, "issues": [str(e)], "status": "error"})
            print(f"错误: {e}")
    
    def _run_p2(self, name, func):
        print(f"  [P2] {name} ...", end=" ")
        try:
            issues = func()
            if issues:
                self.results["P2"].append({"name": name, "issues": issues, "status": "issues"})
                print(f"发现问题 ({len(issues)}处)")
            else:
                self.results["P2"].append({"name": name, "issues": [], "status": "pass"})
                print("通过")
        except Exception as e:
            self.results["P2"].append({"name": name, "issues": [str(e)], "status": "error"})
            print(f"错误: {e}")
    
    def _check_dash(self):
        """扫描破折号"""
        text = self._get_target_text()
        if text is None:
            # 扫描全部正文md文件（真相源）
            issues = []
            body_dir = os.path.join(PROJECT, "正文")
            if os.path.exists(body_dir):
                for root, dirs, files in os.walk(body_dir):
                    for f in files:
                        if f.endswith(".md"):  # only scan MD (truth source)
                            fp = os.path.join(root, f)
                            try:
                                content = open(fp, encoding="utf-8").read()
                                dashes = re.findall(r'——+', content)
                                if dashes:
                                    issues.append(f"{f}: {len(dashes)}处破折号")
                            except:
                                pass
            # 扫描大纲文件
            outline_md = os.path.join(PROJECT, "设定", "md", "02_大纲章纲.md"); outline = outline_md if os.path.exists(outline_md) else None
            if os.path.exists(outline):
                try:
                    content = open(outline, "r", encoding="utf-8").read()
                    dashes = re.findall(r'——+', content)
                    if dashes:
                        issues.append(f"大纲文件: {len(dashes)}处破折号")
                except:
                    pass
            return issues
        else:
            # 单文件模式
            dashes = re.findall(r'——+', text)
            if dashes:
                return [f"发现{len(dashes)}处破折号"]
            return []
    
    def _check_notbut(self):
        """扫描不是而是变体"""
        text = self._get_target_text()
        patterns = [
            r'不是[^，。；]*?而是',
            r'并非[^，。；]*?而是',
            r'不是因为[^，。；]*?(而是|只是|是因为)',
            r'不是说[^，。；]*?是说',
            r'[。，]不是[^。；]*?[。]',
        ]
        if text is None:
            issues = []
            # 扫描所有AI注意事项文件
            rules_dir = os.path.join(PROJECT, "AI注意事项及规则")
            if os.path.exists(rules_dir):
                for f in sorted(os.listdir(rules_dir)):
                    if f.endswith(".md"):
                        fp = os.path.join(rules_dir, f)
                        content = open(fp, encoding="utf-8").read()
                        for pat in patterns:
                            matches = re.findall(pat, content)
                            if matches:
                                issues.append(f"{f}: 发现{len(matches)}处疑似不是句式")
                                break
            # 扫描正文
            body_dir = os.path.join(PROJECT, "正文")
            if os.path.exists(body_dir):
                for root, dirs, files in os.walk(body_dir):
                    for f in files:
                        if f.endswith(".md"):
                            fp = os.path.join(root, f)
                            content = open(fp, encoding="utf-8").read()
                            for pat in patterns:
                                matches = re.findall(pat, content)
                                if matches:
                                    issues.append(f"{f}: 发现{len(matches)}处")
                                    break
            return issues
        else:
            issues = []
            for pat in patterns:
                matches = re.findall(pat, text)
                if matches:
                    issues.append(f"发现{len(matches)}处匹配模式: {pat[:30]}")
            return issues
    
    def _check_zhonger(self):
        """扫描中二体：精确数字、身体超常、标签化词"""
        text = self._get_target_text()
        if text is None:
            return []  # 依赖文件具体路径
        issues = []
        # 精确数字模式：数字+单位/时间
        num_patterns = [
            r'\d+\.?\d*\s*点\d+秒',
            r'\d+\.?\d*\s*秒(?!钟)',
            r'百分之\s*\d+\.?\d*',
            r'\d+\s*个?组合数',
        ]
        for pat in num_patterns:
            matches = re.findall(pat, text)
            if matches:
                issues.append(f"精确数字: {len(matches)}处")
                break
        
        # 标签化词
        tags = ['风卷残云', '天神下凡', '势如破竹', '碾压', '摧枯拉朽']
        for tag in tags:
            count = text.count(tag)
            if count > 0:
                issues.append(f"标签化词: {tag}出现{count}次")
        
        return issues
    
    def _check_ai_transition(self):
        """扫描AI衔接词"""
        text = self._get_target_text()
        if text is None:
            return []
        issues = []
        bad_words = ['然而', '与此同时', '紧接着', '此外', '另一方面']
        for w in bad_words:
            count = text.count(w)
            if count > 0:
                issues.append(f"AI衔接词: {w}出现{count}次")
        return issues
    
    def _check_quotes(self):
        """检查引号规范"""
        text = self._get_target_text()
        if text is None:
            return []
        issues = []
        # 检查直角引号
        if '「' in text or '」' in text or '『' in text or '』' in text:
            issues.append("发现日式角引号，应替换为中文标准双引号")
        return issues
    
    def _check_comma_period_ratio(self):
        """检查逗句比"""
        text = self._get_target_text()
        if not text:
            return []
        
        commas = text.count('，')
        periods = text.count('。')
        if commas + periods == 0:
            return []
        
        ratio = periods / max(commas, 1)
        chars_per_100 = len(text) / 100
        periods_per_100 = periods / max(chars_per_100, 1)
        
        issues = []
        if ratio > 0.8:
            issues.append(f"逗句比{1}:{ratio:.2f}，句号偏多（标准1:0.5~0.8）")
        if periods_per_100 > 3.5:
            issues.append(f"每百字符句号{periods_per_100:.1f}个，超过3.5上限")
        return issues
    
    def _run_existing_audit_scripts(self):
        """运行现有审计脚本"""
        issues = []
        existing_scripts = [
            ('_audit_not.py', '不是句式专项'),
            ('_audit_voice.py', '角色声音专项'),
        ]
        for script_name, desc in existing_scripts:
            sp = os.path.join(SCRIPTS_DIR, script_name)
            if os.path.exists(sp):
                try:
                    r = subprocess.run([sys.executable, sp], capture_output=True, text=True, timeout=60)
                    if r.returncode != 0:
                        out = (r.stdout + r.stderr)[:100]
                        issues.append(f"{desc}: {out}")
                except:
                    issues.append(f"{desc}: 运行失败")
            else:
                issues.append(f"{desc}: 脚本不存在")
        return issues
    
    def report(self):
        """输出汇总报告"""
        elapsed = (datetime.datetime.now() - self.start_time).total_seconds()
        
        total_p0 = len(self.results["P0"])
        pass_p0 = sum(1 for r in self.results["P0"] if r["status"] == "pass")
        total_p1 = len(self.results["P1"])
        pass_p1 = sum(1 for r in self.results["P1"] if r["status"] == "pass")
        total_p2 = len(self.results["P2"])
        pass_p2 = sum(1 for r in self.results["P2"] if r["status"] == "pass")
        
        print(f"\n{'='*50}")
        print(f"审计耗时: {elapsed:.1f}s")
        print(f"P0: {pass_p0}/{total_p0} 通过")
        print(f"P1: {pass_p1}/{total_p1} 通过")
        print(f"P2: {pass_p2}/{total_p2} 通过")
        
        # 判定结果
        p0_issues = any(r["status"] != "pass" for r in self.results["P0"])
        if p0_issues:
            print("状态: 发现问题（P0不通过，不允许归档）")
        else:
            print("状态: 全部通过")
        
        # 写入报告
        if WRITE_REPORT:
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            os.makedirs(REPORT_DIR, exist_ok=True)
            rp = os.path.join(REPORT_DIR, f"统一审计_{ts}.md")
            with open(rp, "w", encoding="utf-8") as f:
                f.write(f"# 统一审计报告 · {ts}\n\n")
                f.write(f"| 层级 | 检查项 | 状态 | 发现 |\n")
                f.write(f"|------|--------|------|------|\n")
                for level in ["P0", "P1", "P2"]:
                    for r in self.results[level]:
                        s = {"pass":"通过","issues":"发现","error":"错误","skipped":"跳过"}.get(r["status"],r["status"])
                        ic = len(r["issues"])
                        f.write(f"| {level} | {r['name']} | {s} | {ic}处 |\n")
                        if ic > 0:
                            f.write(f"\n详情：\n")
                            for iss in r["issues"][:10]:
                                f.write(f"- {iss}\n")
                            f.write("\n")
            print(f"报告: {rp}")
        
        return 0 if not p0_issues else 1

def main():
    print("=== 统一审计入口 ===")
    if QUICK_MODE:
        print("模式: P0快速检查")
    else:
        print("模式: 全量审计")
    if TARGET_FILE:
        print(f"目标: {TARGET_FILE}")
    else:
        print("目标: 全文扫描")
    print()
    
    runner = AuditRunner()
    runner.check_p0()
    runner.check_p1()
    runner.check_p2()
    
    print()
    exit_code = runner.report()
    return exit_code

if __name__ == "__main__":
    print(f"webnovel-studio audit v0.5.0 | PROJECT: {PROJECT}")
    sys.exit(main())
