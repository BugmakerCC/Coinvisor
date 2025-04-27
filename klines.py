import requests
import pandas as pd
from datetime import datetime, timedelta

# 基础请求函数
def get_klines(symbol, interval='1d', limit=500, start_time=None, end_time=None):
    url = "https://api.binance.com/api/v3/klines"
    end_time = datetime.now()  # 当前时间
    start_time = end_time - timedelta(days=90)  # 3个月
    params = {
        "symbol": symbol.upper(),
        "interval": interval,
        "limit": limit
    }

    # 时间范围过滤
    if start_time:
        params["startTime"] = int(pd.Timestamp(start_time).timestamp() * 1000)
    if end_time:
        params["endTime"] = int(pd.Timestamp(end_time).timestamp() * 1000)
    
    while True:
        try:
            response = requests.get(url, params=params)
            # response.raise_for_status()
            return parse_klines(response.json())
        except Exception as e:
            continue
# 数据解析函数
def parse_klines(data):
    columns = [
        'open_time', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'trades',
        'taker_buy_base', 'taker_buy_quote', 'ignore'
    ]
    df = pd.DataFrame(data, columns=columns)
    
    # 类型转换
    numeric_cols = ['open', 'high', 'low', 'close', 'volume']
    df[numeric_cols] = df[numeric_cols].astype(float)
    
    # 时间转换
    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
    df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
    
    return df