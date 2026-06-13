"""
抖店电商罗盘 — 飞书推送模块
通过飞书机器人Webhook推送日报、异常预警和话术建议。
"""

import json
import requests
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict


def load_config():
    cfg_path = Path(__file__).parent / "config.json"
    if cfg_path.exists():
        with open(cfg_path) as f:
            return json.load(f)
    return {}


class FeishuPusher:
    """飞书消息推送器"""
    
    def __init__(self):
        cfg = load_config()
        feishu = cfg.get("feishu", {})
        self.webhook_ops = feishu.get("webhook_ops_group", "")
        self.webhook_host = feishu.get("webhook_host_group", "")
        self.enabled = bool(self.webhook_ops)
    
    def _send(self, webhook_url: str, content: str, msg_type: str = "text") -> bool:
        """发送飞书消息"""
        if not webhook_url or "YOUR_" in webhook_url:
            print(f"[飞书] Webhook未配置，消息内容:\n{content[:200]}...")
            return False
        
        payload = {
            "msg_type": msg_type,
            "content": {"text": content}
        }
        
        try:
            resp = requests.post(webhook_url, json=payload, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("code") == 0:
                    print(f"[飞书] 推送成功")
                    return True
                else:
                    print(f"[飞书] 推送失败: {data.get('msg')}")
            else:
                print(f"[飞书] HTTP错误: {resp.status_code}")
            return False
        except Exception as e:
            print(f"[飞书] 异常: {e}")
            return False
    
    def push_alert(self, message: str, to_ops: bool = True, to_host: bool = False) -> Dict:
        """推送异常预警"""
        results = {}
        if to_ops and message:
            results["ops_group"] = self._send(self.webhook_ops, message)
        if to_host and message:
            results["host_group"] = self._send(self.webhook_host, message)
        return results
    
    def push_daily_report(self, report: str) -> bool:
        """推送日报到运营群"""
        return self._send(self.webhook_ops, report)
    
    def push_weekly_report(self, report: str) -> bool:
        """推送周报到运营群"""
        return self._send(self.webhook_ops, report)
    
    def push_script_suggestion(self, product_name: str, selling_point: str) -> Dict:
        """推送话术建议到主播群"""
        message = f"""💡 **直播话术建议**

**产品:** {product_name}
**卖点:** {selling_point}
**生成时间:** {datetime.now().strftime('%m-%d %H:%M')}

**开场话术:**
"欢迎新进直播间的家人们！今天给大家带来的是我们夏季爆款{product_name}，这个{selling_point}穿过的都知道有多香！"

**促单话术:**
"现在下单立减20，还赠送运费险，不满意包退！库存不多，抢到就是赚到！"

**逼单话术:**
"最后5单！最后5单！拍完这个颜色就没了，手慢真的就没了！"
"""
        return {
            "host_group": self._send(self.webhook_host, message),
            "ops_group": self._send(self.webhook_ops, message),
        }
    
    def push_inventory_alert(self, product_name: str, stock: int, daily_sales: int) -> bool:
        """推送库存预警"""
        days_left = stock / daily_sales if daily_sales > 0 else 0
        message = f"""📦 **库存预警**

**产品:** {product_name}
**当前库存:** {stock}件
**日销量:** {daily_sales}件/天
**预计清空:** {days_left:.1f}天

⚠️ 建议立即联系供应链补货，或调整推品策略减少曝光。
"""
        return self._send(self.webhook_ops, message)


# 快捷函数
_default = None

def get_pusher() -> FeishuPusher:
    global _default
    if _default is None:
        _default = FeishuPusher()
    return _default


if __name__ == "__main__":
    pusher = FeishuPusher()
    print(f"飞书推送器已初始化，Webhook状态: {'已配置' if pusher.enabled else '未配置'}")
    # 测试消息（需配置 webhook 后生效）
    pusher._send(pusher.webhook_ops, "🤖 抖店自动复盘系统 · 推送模块测试")
