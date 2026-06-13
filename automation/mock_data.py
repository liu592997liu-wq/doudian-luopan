"""
抖店电商罗盘 — 数据模拟模块
模拟从抖店罗盘API拉取的数据结构，用于开发和演示。
生产环境替换为真实API调用。
"""

from datetime import datetime, timedelta
import json
import random

def mock_fetch_daily_metrics(date_str=None):
    """模拟拉取单日核心指标"""
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    # 基于随机种子生成相对稳定的数据
    seed = hash(date_str) % 100
    random.seed(seed)
    
    base_gmv = 105000 + random.randint(-5000, 25000)
    gmv_change = round(random.uniform(-0.05, 0.20), 3)
    
    return {
        "date": date_str,
        "gmv": round(base_gmv / 10000, 2),           # 万元
        "gmv_change": gmv_change,                      # 环比
        "orders": random.randint(800, 1500),
        "orders_change": round(random.uniform(-0.03, 0.15), 3),
        "conversion_rate": round(random.uniform(0.032, 0.048), 3),
        "conversion_change": round(random.uniform(-0.008, 0.012), 3),
        "avg_ticket": round(random.uniform(95, 115), 1),
        "avg_ticket_change": round(random.uniform(-0.02, 0.05), 3),
        "spu_count": random.randint(120, 135),
        "total_stock": random.randint(4500, 5200),
        "daily_sales_qty": random.randint(120, 180),
        "turnover_rate": round(random.uniform(0.58, 0.67), 2),
        "turnover_change": round(random.uniform(-0.05, 0.02), 3),
    }


def mock_fetch_traffic():
    """模拟流量来源分布"""
    return {
        "live_stream": round(random.uniform(0.45, 0.58), 3),
        "short_video": round(random.uniform(0.25, 0.35), 3),
        "search": round(1.0 - 0.48 - 0.32, 3),  # remainder
    }


def mock_fetch_video_metrics():
    """模拟短视频核心指标"""
    return {
        "total_plays": round(random.randint(300000, 550000) / 10000, 1),
        "plays_change": round(random.uniform(-0.05, 0.20), 3),
        "engagement_rate": round(random.uniform(0.05, 0.08), 2),
        "engagement_change": round(random.uniform(-0.02, 0.04), 3),
        "video_gmv": round(random.randint(25000, 55000) / 10000, 1),
        "video_gmv_change": round(random.uniform(-0.05, 0.25), 3),
        "avg_watch_time_s": round(random.uniform(15, 22), 1),
        "watch_time_change": round(random.uniform(-2, 1), 1),
        "ctr": round(random.uniform(0.035, 0.055), 3),
        "category_avg_ctr": round(random.uniform(0.05, 0.065), 3),
    }


def mock_fetch_live_metrics():
    """模拟直播核心指标"""
    return {
        "live_gmv": round(random.randint(60000, 100000) / 10000, 1),
        "live_gmv_change": round(random.uniform(-0.05, 0.25), 3),
        "viewers": round(random.randint(20000, 40000) / 10000, 1),
        "viewers_change": round(random.uniform(-0.03, 0.10), 3),
        "live_conversion": round(random.uniform(0.035, 0.05), 2),
        "live_conversion_change": round(random.uniform(-0.01, 0.02), 3),
        "avg_stay_min": random.randint(1, 3),
        "avg_stay_sec": random.randint(0, 59),
        "stay_change_sec": random.randint(-15, 5),
        "sessions": [
            {"time": "14:00", "name": "夏季新品专场", "gmv": round(random.randint(30000, 55000) / 10000, 1), "status": "done"},
            {"time": "18:00", "name": "夏季爆款返场", "gmv": 0, "status": "live"},
            {"time": "20:00", "name": "清仓福利专场", "gmv": 0, "status": "upcoming"},
        ],
    }


def mock_fetch_product_ranking():
    """模拟商品排行"""
    products = [
        {"rank": 1, "name": "夏季冰丝Polo衫", "sales": random.randint(3000, 4500), "gmv": round(random.randint(75000, 100000) / 10000, 1)},
        {"rank": 2, "name": "经典圆领T恤", "sales": random.randint(2500, 3500), "gmv": round(random.randint(60000, 80000) / 10000, 1)},
        {"rank": 3, "name": "休闲直筒长裤", "sales": random.randint(1800, 2500), "gmv": round(random.randint(50000, 70000) / 10000, 1)},
    ]
    return products


def mock_fetch_video_ranking():
    """模拟短视频排行"""
    videos = [
        {"rank": 1, "name": "冰丝Polo夏季穿搭", "plays": 8.2, "engagement": 7.3, "gmv": 1.2},
        {"rank": 2, "name": "圆领T恤百搭推荐", "plays": 6.8, "engagement": 5.9, "gmv": 0.9},
        {"rank": 3, "name": "直筒裤夏日通勤", "plays": 5.1, "engagement": 4.8, "gmv": 0.7},
    ]
    return videos


def mock_fetch_category_breakdown():
    """模拟品类销售占比"""
    return [
        {"category": "T恤", "pct": 42},
        {"category": "Polo衫", "pct": 31},
        {"category": "裤子", "pct": 22},
        {"category": "其他", "pct": 5},
    ]


def mock_fetch_history(days=7):
    """模拟拉取历史趋势数据"""
    data = []
    for i in range(days - 1, -1, -1):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        day = mock_fetch_daily_metrics(date)
        data.append({"date": day["date"], "gmv": day["gmv"]})
    return data


def mock_complete_dataset(date_str=None):
    """生成完整的单日数据集"""
    return {
        "fetched_at": datetime.now().isoformat(),
        "metrics": mock_fetch_daily_metrics(date_str),
        "traffic": mock_fetch_traffic(),
        "video": mock_fetch_video_metrics(),
        "live": mock_fetch_live_metrics(),
        "products": mock_fetch_product_ranking(),
        "videos": mock_fetch_video_ranking(),
        "categories": mock_fetch_category_breakdown(),
        "trend_7d": mock_fetch_history(7),
    }


if __name__ == "__main__":
    dataset = mock_complete_dataset()
    print(json.dumps(dataset, ensure_ascii=False, indent=2))
