import requests
import json

proxies = {
  "http": "http://127.0.0.1:7890",
  "https": "http://127.0.0.1:7890",
}

def get_coin_info_market(symbol):
    print(f"📖 正在获取 {symbol} 的市场信息...")
    url = "https://api.binance.com/api/v3/ticker/24hr"
    params = {"symbol": symbol.upper()+"USDT"}  # 确保交易对符号大写
    # return json.dumps({"price": 0.1})
    response = requests.get(url, params=params, proxies=proxies)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return json.dumps({"error": "Failed to find market information for this cryptocurrency on Binance"}, ensure_ascii=False, indent=4)
    

if __name__ == "__main__":
    symbol = "BNB"
    result = get_coin_info_market(symbol)
    print(result)
