# 新增的绘图函数（放在代码中合适位置）
import mplfinance as mpf
import os
import os
from openai import OpenAI
import base64
from datetime import datetime, timedelta
import requests
import pandas as pd
import json
import uuid
proxies = {
  "http": "http://127.0.0.1:7890",
  "https": "http://127.0.0.1:7890",
}

BASE_URL = "http://116.62.42.206:5000"

# 基础请求函数
def get_klines(symbol, days=90, interval='1d',limit=500, start_time=None, end_time=None):
    url = "https://api.binance.com/api/v3/klines"
    end_time = datetime.now()  # 当前时间
    start_time = end_time - timedelta(days)  # 3个月
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
    
    response = requests.get(url, params=params, proxies=proxies)
    if response.status_code == 200:
        return parse_klines(response.json())
    else:
        return json.dumps({"error": "Binance service not responding"}, ensure_ascii=False, indent=4)
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


#  Base64 编码格式
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
    
def analyze_k(image_path):
    """
    读取图片并返回描述
    """
    # 读取图片
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()

    # 将图片数据转换为Base64编码
    base64_image = base64.b64encode(image_data).decode("utf-8")
    client = OpenAI(
        # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
        api_key="sk-25c7f85d161a4856839e4ba4eac42e27",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    completion = client.chat.completions.create(
        model="qwen-omni-turbo-latest",
        messages=[
            {
                "role": "system",
                "content": [{"type": "text", "text": "You are a K-line analysis expert in cryptocurrency"}],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{base64_image}"},
                    },
                    {"type": "text", "text": '''I will provide you with 90 days of candlestick (K-line) image for a specific cryptocurrency.

Your task is to analyze this image and extract valuable key insights, including but not limited to:
	1.	Trends (e.g., bullish or bearish phases, trend reversals).
	2.	Support and resistance levels.
	3.	Periods of high volatility or unusual trading volume.
	4.	Notable candlestick patterns (e.g., doji, hammer, engulfing patterns).
	5.	Potential signals for technical indicators (e.g., moving averages, RSI, MACD — you can infer them if not directly provided).
	6.	Any anomalies or market behavior worth highlighting.

Present your analysis in a clear, structured, and human-readable format. If possible, conclude with a short summary of the overall market sentiment based on the 90-day data.'''},
                ],
            },
        ],
        # 设置输出数据的模态，当前支持两种：["text","audio"]、["text"]
        modalities=["text"],
        # stream 必须设置为 True，否则会报错
        stream=True,
        stream_options={"include_usage": True},
    )

    response = ""
    for chunk in completion:
        if chunk.choices:
            if chunk.choices[0].delta.content:
                response += chunk.choices[0].delta.content
    return response


def get_k_des(symbol, days=90, interval='1d',save_dir='/charts'):
    """
    绘制K线图并保存到指定目录
    """
    save_dir = os.path.abspath(save_dir)
    os.makedirs(save_dir, exist_ok=True)

    unique_id = uuid.uuid4().hex

    print(f"🤔 正在绘制并分析 {symbol} 的{days}日k线图...")
    df = get_klines(symbol+"USDT", days, interval)
    try:
        # 设置时间为索引
        df_plot = df.set_index('open_time')
        
        # 重命名列以符合 mplfinance 要求
        df_plot = df_plot.rename(columns={
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'volume': 'Volume'
        })
        
        
        filename = f"{save_dir}/{symbol}_candlestick_{unique_id}.png"

        # 绘制并保存
        mpf.plot(
            df_plot,
            type='candle',
            style='binance',
            title=f'{symbol} price trend',
            ylabel='Price',
            volume=True,
            savefig=filename
        )
        # print(f"k线图已保存至: {filename}")
        img_url = f"{BASE_URL}{filename}"
        markdown = f"![{symbol} K线图]({img_url})"
        return json.dumps({"markdown": markdown}, ensure_ascii=False, indent=4)
    except Exception as e:
        # print(f"绘制 {symbol} K线图失败: {str(e)}")
        return json.dumps({"error": "K线图绘制失败"}, ensure_ascii=False, indent=4)
    
    # result = analyze_k(filename)
    # return json.dumps({"K line description": result}, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    # 示例：绘制 BTCUSDT 的 90 天 K 线图
    print(get_k_des("BTC"))