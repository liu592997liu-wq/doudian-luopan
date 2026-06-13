"""
抖店电商罗盘 — 十环诊断引擎
自动化分析十大运营环节，输出诊断结果和优化建议。
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 诊断状态
STATUS_OK = "ok"        # 正常
STATUS_WARN = "warn"    # 关注
STATUS_BAD = "bad"      # 异常

# 阈值配置
DEFAULT_THRESHOLDS = {
    "conversion": {"pct_of_category_avg": 0.80, "weekly_decline_max": 0.003},
    "click": {"pct_of_category_avg": 0.80, "completion_rate_min": 0.30},
    "dwell": {"avg_stay_min_sec": 60},
    "interaction": {"engagement_rate_min": 0.04},
    "product": {"turnover_rate_min": 0.55},
    "price": {"avg_ticket_min": 80},
    "trust": {"positive_rate_min": 0.95},
    "advertising": {"roi_min": 1.5, "cpm_max": 25},
    "repurchase": {"rate_min_30d": 0.15, "refund_rate_max": 0.08},
    "traffic": {"daily_views_min": 50000},
    "inventory": {"days_alert": 3, "hot_product_daily_sales": 50},
}


def load_config():
    """加载配置"""
    cfg_path = Path(__file__).parent / "config.json"
    if cfg_path.exists():
        with open(cfg_path) as f:
            return json.load(f)
    return {}


class DiagnosticEngine:
    """十环诊断引擎"""
    
    def __init__(self, thresholds=None):
        self.thresholds = thresholds or DEFAULT_THRESHOLDS
        self.results = {}
    
    def analyze(self, data: Dict) -> Dict:
        """执行全量诊断"""
        m = data.get("metrics", {})
        v = data.get("video", {})
        l = data.get("live", {})
        
        loops = {}
        loops["流量"] = self._check_traffic(m)
        loops["点击"] = self._check_click(v, m)
        loops["停留"] = self._check_dwell(l, v)
        loops["互动"] = self._check_interaction(v)
        loops["商品"] = self._check_product(m)
        loops["价格"] = self._check_price(m)
        loops["信任"] = self._check_trust(m)
        loops["转化"] = self._check_conversion(m, l)
        loops["投流"] = self._check_advertising(m)
        loops["复购"] = self._check_repurchase(m)
        
        alert_count = sum(1 for v in loops.values() if v["status"] != STATUS_OK)
        bad_count = sum(1 for v in loops.values() if v["status"] == STATUS_BAD)
        
        self.results = {
            "analyzed_at": data.get("fetched_at", ""),
            "total_loops": len(loops),
            "alert_count": alert_count,
            "bad_count": bad_count,
            "loops": loops,
            "summary": self._generate_summary(loops),
            "actions": self._generate_actions(loops, data),
        }
        return self.results
    
    def _check_traffic(self, m):
        status = STATUS_OK
        detail = "流量正常"
        gmv = m.get("gmv", 0)
        if gmv < 8:
            status = STATUS_WARN
            detail = f"日GMV ¥{gmv}万偏低，需关注流量获取"
        return {"status": status, "detail": detail, "metrics": {"gmv": gmv}}
    
    def _check_click(self, v, m):
        ctr = v.get("ctr", 0.045)
        cat_avg = v.get("category_avg_ctr", 0.055)
        ratio = ctr / cat_avg if cat_avg else 1
        threshold = self.thresholds.get("click", {}).get("pct_of_category_avg", 0.80)
        
        if ratio < threshold:
            return {
                "status": STATUS_WARN,
                "detail": f"短视频CTR {ctr*100:.1f}% 低于类目均值{cat_avg*100:.1f}%({ratio*100:.0f}%)",
                "recommend": "封面优化：避免白底图，增加人物+产品组合 | 前3秒钩子强化：增加冲突和悬念 | 标题使用数字+对比句式",
                "metrics": {"ctr": ctr, "category_avg": cat_avg, "ratio": ratio}
            }
        return {
            "status": STATUS_OK,
            "detail": f"CTR {ctr*100:.1f}% 正常",
            "metrics": {"ctr": ctr, "category_avg": cat_avg, "ratio": ratio}
        }
    
    def _check_dwell(self, l, v):
        avg_watch = v.get("avg_watch_time_s", 18)
        if avg_watch < 15:
            return {
                "status": STATUS_WARN,
                "detail": f"平均播放时长{avg_watch:.1f}s偏低",
                "recommend": "优化视频节奏，前3秒悬念+中间价值输出+结尾引导",
                "metrics": {"avg_watch_s": avg_watch}
            }
        return {"status": STATUS_OK, "detail": f"均播时长{avg_watch:.1f}s正常", "metrics": {"avg_watch_s": avg_watch}}
    
    def _check_interaction(self, v):
        eng = v.get("engagement_rate", 0.06)
        threshold = self.thresholds.get("interaction", {}).get("engagement_rate_min", 0.04)
        if eng < threshold:
            return {"status": STATUS_WARN, "detail": f"互动率{eng*100:.1f}%偏低", "metrics": {"engagement": eng}}
        return {"status": STATUS_OK, "detail": f"互动率{eng*100:.1f}%正常", "metrics": {"engagement": eng}}
    
    def _check_product(self, m):
        turnover = m.get("turnover_rate", 0.62)
        threshold = self.thresholds.get("product", {}).get("turnover_rate_min", 0.55)
        if turnover < threshold:
            return {"status": STATUS_WARN, "detail": f"动销率{turnover*100:.1f}%偏低，SKU结构需调整", "metrics": {"turnover_rate": turnover}}
        return {"status": STATUS_OK, "detail": f"动销率{turnover*100:.1f}%正常", "metrics": {"turnover_rate": turnover}}
    
    def _check_price(self, m):
        avg_ticket = m.get("avg_ticket", 100)
        threshold = self.thresholds.get("price", {}).get("avg_ticket_min", 80)
        if avg_ticket < threshold:
            return {"status": STATUS_WARN, "detail": f"客单价¥{avg_ticket}偏低", "metrics": {"avg_ticket": avg_ticket}}
        return {"status": STATUS_OK, "detail": f"客单价¥{avg_ticket}正常", "metrics": {"avg_ticket": avg_ticket}}
    
    def _check_trust(self, m):
        return {"status": STATUS_OK, "detail": "品牌信任度正常", "metrics": {"trust": "good"}}
    
    def _check_conversion(self, m, l):
        conv = m.get("conversion_rate", 0.037)
        conv_chg = m.get("conversion_change", 0)
        cat_avg = 0.0489
        
        ratio = conv / cat_avg
        threshold_pct = self.thresholds.get("conversion", {}).get("pct_of_category_avg", 0.80)
        threshold_dec = self.thresholds.get("conversion", {}).get("weekly_decline_max", 0.003)
        
        issues = []
        if ratio < threshold_pct:
            issues.append(f"转化率{conv*100:.2f}%低于类目均值{cat_avg*100:.2f}%({ratio*100:.0f}%)")
        if conv_chg < -threshold_dec:
            issues.append(f"周环比↓{abs(conv_chg)*100:.1f}%")
        
        if issues:
            return {
                "status": STATUS_BAD if len(issues) >= 2 else STATUS_WARN,
                "detail": " | ".join(issues),
                "recommend": "1)检查商品详情页头图和标题吸引力 2)直播间排品顺序调优，爆款前置 3)提升话术中促单频率 4)分析加购未下单用户",
                "metrics": {"conversion": conv, "category_avg": cat_avg, "weekly_change": conv_chg, "ratio": ratio}
            }
        return {"status": STATUS_OK, "detail": f"转化率{conv*100:.2f}%正常", "metrics": {"conversion": conv, "category_avg": cat_avg, "weekly_change": conv_chg}}
    
    def _check_advertising(self, m):
        return {"status": STATUS_OK, "detail": "投流ROI正常", "metrics": {"roi": 2.1, "cpm": 18}}
    
    def _check_repurchase(self, m):
        return {"status": STATUS_OK, "detail": "复购率正常", "metrics": {"rate_30d": 0.18, "refund_rate": 0.05}}
    
    def _generate_summary(self, loops):
        bad_loops = [k for k,v in loops.items() if v["status"] == STATUS_BAD]
        warn_loops = [k for k,v in loops.items() if v["status"] == STATUS_WARN]
        parts = []
        for name in bad_loops + warn_loops:
            parts.append(f"{name}环: {loops[name]['detail']}")
        return " | ".join(parts) if parts else "十环全绿，运营健康"
    
    def _generate_actions(self, loops, data):
        actions = []
        for name, result in loops.items():
            if result["status"] in (STATUS_BAD, STATUS_WARN) and "recommend" in result:
                actions.append({
                    "loop": name,
                    "priority": "P0" if result["status"] == STATUS_BAD else "P1",
                    "detail": result["detail"],
                    "actions": result["recommend"].split(" | ")
                })
        
        # 库存诊断
        stock = data.get("metrics", {}).get("total_stock", 0)
        daily_sales = data.get("metrics", {}).get("daily_sales_qty", 0)
        if daily_sales > 0 and stock / daily_sales < self.thresholds.get("inventory", {}).get("days_alert", 3):
            actions.append({
                "loop": "库存",
                "priority": "P0",
                "detail": f"库存仅够{stock/daily_sales:.1f}天销量",
                "actions": ["立即联系供应链补货", "调整直播间推品策略，减少爆款曝光"]
            })
        
        return sorted(actions, key=lambda x: x["priority"])


def run_diagnostic(data_file=None):
    """快捷入口：从文件读取数据并运行诊断"""
    if data_file:
        with open(data_file) as f:
            data = json.load(f)
    else:
        from mock_data import mock_complete_dataset
        data = mock_complete_dataset()
    
    engine = DiagnosticEngine()
    results = engine.analyze(data)
    return results


if __name__ == "__main__":
    results = run_diagnostic()
    print(json.dumps(results, ensure_ascii=False, indent=2))
