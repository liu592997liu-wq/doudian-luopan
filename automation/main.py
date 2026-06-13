#!/usr/bin/env python3
"""
抖店电商罗盘 — 自动化主控脚本
用法:
  python main.py                 # 运行完整流程（数据→诊断→推送）
  python main.py --dry-run       # 干跑模式，不推送飞书
  python main.py --report daily  # 仅生成日报
  python main.py --report week   # 仅生成周报
  python main.py --diagnose      # 仅运行诊断
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent

# 添加项目根目录到路径
sys.path.insert(0, str(SCRIPT_DIR))

from mock_data import mock_complete_dataset, mock_fetch_history
from diagnostic_engine import DiagnosticEngine, run_diagnostic
from report_generator import ReportGenerator, generate_alert_message
from feishu_pusher import FeishuPusher, get_pusher


def print_header(title: str):
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}")


def print_section(title: str):
    print(f"\n--- {title} ---")


def main(args):
    print_header(f"抖店电商罗盘 · 自动化引擎 v1.0")
    print(f"运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # ═══ Step 1: 数据获取 ═══
    print_section("Step 1: 数据获取")
    
    if args.file:
        with open(args.file) as f:
            data = json.load(f)
        print(f"从文件加载: {args.file}")
    else:
        print("使用模拟数据（生产环境请配置抖店API）")
        data = mock_complete_dataset()
    
    m = data.get("metrics", {})
    print(f"  GMV: ¥{m.get('gmv', 0)}万 | 订单: {m.get('orders', 0)} | 转化: {m.get('conversion_rate', 0)*100:.2f}%")
    
    # ═══ Step 2: 诊断分析 ═══
    print_section("Step 2: 十环诊断")
    
    engine = DiagnosticEngine()
    diagnostic = engine.analyze(data)
    
    print(f"  诊断完成: {diagnostic['total_loops']}环 | "
          f"{diagnostic['alert_count']}环需关注 ({diagnostic['bad_count']}异常)")
    
    for name, result in diagnostic["loops"].items():
        icon = {"ok": "✅", "warn": "⚠️", "bad": "🔴"}.get(result["status"], "?")
        print(f"  {icon} {name}环: {result['detail']}")
    
    # ═══ Step 3: 行动项 ═══
    actions = diagnostic.get("actions", [])
    if actions:
        print_section(f"Step 3: 行动项 ({len(actions)}条)")
        for a in actions:
            print(f"  [{a['priority']}] {a['loop']}环: {a['detail']}")
            for act in a.get("actions", []):
                print(f"    → {act.strip()}")
    
    # ═══ Step 4: 报告生成 ═══
    reporter = ReportGenerator(data, diagnostic)
    
    if args.report == "daily" or args.report is None:
        print_section("Step 4: 日报生成")
        daily = reporter.generate_daily_report()
        print(daily)
        
        # 保存日报
        report_dir = SCRIPT_DIR / "reports"
        report_dir.mkdir(exist_ok=True)
        date_str = m.get("date", datetime.now().strftime("%Y-%m-%d"))
        report_path = report_dir / f"daily_{date_str}.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(daily)
        print(f"  日报已保存: {report_path}")
    
    if args.report == "week":
        print_section("Step 4: 周报生成")
        week_data = [mock_complete_dataset() for _ in range(7)]
        week_diag = [engine.analyze(d) for d in week_data]
        weekly = reporter.generate_weekly_report(week_data, week_diag)
        print(weekly)
    
    # ═══ Step 5: 飞书推送 ═══
    if not args.dry_run:
        print_section("Step 5: 飞书推送")
        pusher = get_pusher()
        
        if not pusher.enabled:
            print("  ⚠️ 飞书Webhook未配置，跳过推送")
            print("  请在 config.json 中配置 feishu.webhook_ops_group")
        else:
            # 推送异常预警
            alert_msg = generate_alert_message(diagnostic)
            if alert_msg:
                result = pusher.push_alert(alert_msg)
                print(f"  异常预警推送: {'✅' if result.get('ops_group') else '❌'}")
            else:
                print("  无异常，跳过预警推送")
            
            # 推送日报
            if args.report in (None, "daily"):
                result = pusher.push_daily_report(daily)
                print(f"  日报推送: {'✅' if result else '❌'}")
    
    print_header("完成")
    print(f"  数据同步 ✅ | 诊断分析 ✅ | 报告生成 ✅ | 飞书推送 {'✅' if not args.dry_run and get_pusher().enabled else '⏭️'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="抖店电商罗盘自动化引擎")
    parser.add_argument("--dry-run", action="store_true", help="干跑模式，不推送飞书")
    parser.add_argument("--report", choices=["daily", "week"], help="仅生成指定报告")
    parser.add_argument("--diagnose", action="store_true", help="仅运行诊断")
    parser.add_argument("--file", type=str, help="从指定JSON文件读取数据")
    args = parser.parse_args()
    
    if args.diagnose:
        print_header("十环诊断")
        results = run_diagnostic(args.file)
        for name, result in results["loops"].items():
            icon = {"ok": "✅", "warn": "⚠️", "bad": "🔴"}.get(result["status"], "?")
            print(f"  {icon} {name}环: {result['detail']}")
    else:
        main(args)
