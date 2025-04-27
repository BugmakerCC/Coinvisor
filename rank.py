import requests
import json
from bs4 import BeautifulSoup
from openai import OpenAI
proxies = {
  "http": "http://127.0.0.1:7890",
  "https": "http://127.0.0.1:7890",
}

def get_24h_tickers():
    url = "https://api.binance.com/api/v3/ticker/24hr"
    response = requests.get(url, proxies=proxies)
    return response.json()

def filter_coins(tickers):
    return [t for t in tickers 
            if t['symbol'].endswith('USDT')]

def get_top_gainers(top_n=10):
    """获取币价涨幅排行榜"""
    print("📈 正在获取币价涨幅排行榜...")
    tickers = get_24h_tickers()
    # 过滤USDT交易对并转换数据格式
    filtered = [
        {
            "symbol": t["symbol"][:-4],  # 去掉USDT后缀
            "priceChangePercent": float(t["priceChangePercent"]),
            "lastPrice": float(t["lastPrice"])
        }
        for t in tickers
        if t["symbol"].endswith("USDT")  # 只保留USDT交易对
    ]
    
    # 按涨幅降序排序
    sorted_tickers = sorted(filtered, key=lambda x: x["priceChangePercent"], reverse=True)
    
    # 取前N名
    return json.dumps(sorted_tickers[:top_n], indent=4, ensure_ascii=False)

def get_hot_coins(top_n=10):
    """获取成交量排行榜"""
    print("📈 正在获取热门加密货币排行榜...")
    tickers = get_24h_tickers()
    filtered = [
        {
            "symbol": t["symbol"][:-4],  # 去掉USDT后缀
            "quoteVolume": float(t["quoteVolume"])
        }
        for t in tickers
        if t["symbol"].endswith("USDT")  # 只保留USDT交易对
    ]
    
    sorted_tickers = sorted(filtered, 
                          key=lambda x: float(x['quoteVolume']), 
                          reverse=True)
    return json.dumps(sorted_tickers[:top_n], indent=4, ensure_ascii=False)