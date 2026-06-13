"""
抖店电商罗盘 — 报告生成器
自动生成日报、周报、月报文本，支持飞书Markdown格式。
"""

from datetime import datetime, timedelta
from typing import Dict


class ReportGenerator:
    """自动化报告生成器"""
    
    def __init__(self, data: Dict, diagnostic: Dict):
        self.data = data
        self.diag = diagnostic
    
    def generate_daily_report(self) -> str:
        """生成日报"""
        m = self.data.get("metrics", {})
        v = self.data.get("video", {})
        l = self.data.get("live", {})
        date = m.get("date", datetime.now().strftime("%Y-%m-%d"))
        
        # KPI行
        gmv_arrow = "↑" if m.get("gmv_change", 0) > 0 else "↓"
        orders_arrow = "↑" if m.get("orders_change", 0) > 0 else "↓"
        
        report = f"""📋 **抖店日报 · {date}**

━━━━━━━━━━━━━━━━━
**核心指标**
━━━━━━━━━━━━━━━━━
• GMV: ¥{m.get('gmv', 0)}万 {gmv_arrow}{abs(m.get('gmv_change', 0))*100:.1f}%
• 订单: {m.get('orders', 0)}单 {orders_arrow}{abs(m.get('orders_change', 0))*100:.1f}%
• 转化率: {m.get('conversion_rate', 0)*100:.2f}%
• 客单价: ¥{m.get('avg_ticket', 0)}

━━━━━━━━━━━━━━━━━
**流量来源**
━━━━━━━━━━━━━━━━━
• 直播: {self.data.get('traffic', {}).get('live_stream', 0)*100:.1f}%
• 短视频: {self.data.get('traffic', {}).get('short_video', 0)*100:.1f}%
• 搜索: {self.data.get('traffic', {}).get('search', 0)*100:.1f}%

━━━━━━━━━━━━━━━━━
**短视频**
━━━━━━━━━━━━━━━━━
• 播放量: {v.get('total_plays', 0)}万
• 互动率: {v.get('engagement_rate', 0)*100:.1f}%
• 带货GMV: ¥{v.get('video_gmv', 0)}万
• 均播时长: {v.get('avg_watch_time_s', 0)}s

━━━━━━━━━━━━━━━━━
**直播**
━━━━━━━━━━━━━━━━━
• 直播GMV: ¥{l.get('live_gmv', 0)}万
• 观看人次: {l.get('viewers', 0)}万
• 转化率: {l.get('live_conversion', 0)*100:.1f}%
• 均停留: {l.get('avg_stay_min', 0)}m{l.get('avg_stay_sec', 0)}s

━━━━━━━━━━━━━━━━━
**商品**
━━━━━━━━━━━━━━━━━
• 在售SPU: {m.get('spu_count', 0)}
• 日销量: {m.get('daily_sales_qty', 0)}件
• 动销率: {m.get('turnover_rate', 0)*100:.1f}%

TOP3品类: {', '.join(f"{c['category']}{c['pct']}%" for c in self.data.get('categories', []))}

━━━━━━━━━━━━━━━━━
**🔍 诊断摘要**
━━━━━━━━━━━━━━━━━
{self.diag.get('summary', '无异常')}

"""
        # 添加行动项
        actions = self.diag.get("actions", [])
        if actions:
            report += "━━━━━━━━━━━━━━━━━\n**⚡ 行动项**\n━━━━━━━━━━━━━━━━━\n"
            for i, a in enumerate(actions, 1):
                report += f"{i}. [{a['priority']}] {a['detail']}\n"
                for act in a.get("actions", []):
                    report += f"   - {act}\n"
        
        report += f"\n📅 自动生成于 {datetime.now().strftime('%m-%d %H:%M')} | 诊断引擎 v1.0"
        return report
    
    def generate_weekly_report(self, week_data_list, week_diagnostic_list) -> str:
        """生成周报"""
        week_num = datetime.now().isocalendar()[1]
        total_gmv = sum(d.get("metrics", {}).get("gmv", 0) for d in week_data_list)
        total_orders = sum(d.get("metrics", {}).get("orders", 0) for d in week_data_list)
        
        avg_conv = sum(d.get("metrics", {}).get("conversion_rate", 0) for d in week_data_list) / max(len(week_data_list), 1)
        
        total_alert = sum(d.get("alert_count", 0) for d in week_diagnostic_list)
        
        report = f"""📊 **抖店周报 · 第{week_num}周**

━━━━━━━━━━━━━━━━━
**本周累计**
━━━━━━━━━━━━━━━━━
• 累计GMV: ¥{total_gmv:.1f}万
• 累计订单: {total_orders}单
• 平均转化率: {avg_conv*100:.2f}%
• 本周诊断预警: {total_alert}次

━━━━━━━━━━━━━━━━━
**趋势分析**
━━━━━━━━━━━━━━━━━
"""
        # 添加7天趋势
        for d in week_data_list:
            m = d.get("metrics", {})
            date = m.get("date", "")
            gmv = m.get("gmv", 0)
            bar = "█" * int(gmv / 2)
            report += f"• {date[-5:]}: {bar} ¥{gmv}万\n"
        
        report += f"\n📅 自动生成于 {datetime.now().strftime('%m-%d %H:%M')} | 诊断引擎 v1.0"
        return report
    
    def generate_monthly_report(self, month_data, month_diagnostic) -> str:
        """生成月报"""
        now = datetime.now()
        report = f"""📑 **抖店月报 · {now.year}年{now.month}月**

━━━━━━━━━━━━━━━━━
**本月概览**
━━━━━━━━━━━━━━━━━
月报将于次月1日自动生成，覆盖以下五大维度：
1. 月度GMV及环比分析
2. 品类结构变化
3. 直播效率趋势
4. 短视频带货效果
5. 库存动销及供应链建议

📅 预计生成时间: {(now.replace(day=1) + timedelta(days=32)).replace(day=1).strftime('%m月1日')} 08:00
📅 自动生成于 {datetime.now().strftime('%m-%d %H:%M')} | 诊断引擎 v1.0
"""
        return report


def generate_alert_message(diagnostic: Dict) -> str:
    """生成异常预警消息（飞书卡片格式）"""
    bad_loops = {k: v for k, v in diagnostic.get("loops", {}).items() if v["status"] == "bad"}
    warn_loops = {k: v for k, v in diagnostic.get("loops", {}).items() if v["status"] == "warn"}
    
    if not bad_loops and not warn_loops:
        return None
    
    msg = "🔴 **异常预警**\n\n"
    
    for name, result in bad_loops.items():
        msg += f"**{name}环 · 异常**\n"
        msg += f"{result['detail']}\n"
        if "recommend" in result:
            msg += f"\n💡 {result['recommend']}\n"
        msg += "\n"
    
    for name, result in warn_loops.items():
        msg += f"⚠️ **{name}环 · 关注**\n"
        msg += f"{result['detail']}\n"
        if "recommend" in result:
            for rec in result['recommend'].split(" | "):
                msg += f"  - {rec}\n"
        msg += "\n"
    
    msg += f"📅 诊断时间: {datetime.now().strftime('%m-%d %H:%M')}"
    return msg
