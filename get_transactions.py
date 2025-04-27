import os
import requests
from bs4 import BeautifulSoup
import urllib.request,urllib.error
from datetime import datetime, timedelta
from dotenv import load_dotenv
import json
from openai import OpenAI

load_dotenv()
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY", "your-api-key-here")
QWEN_API_KEY = 'your-api-key-here'
proxies = {
    'https': 'https://127.0.0.1:7890',     # 查找到你的vpn在本机使用的https代理端口
    'http': 'http://127.0.0.1:7890',       # 查找到vpn在本机使用的http代理端口
}
head = {  # 模拟浏览器头部信息，向豆瓣服务器发送消息
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
}
opener = urllib.request.build_opener(urllib.request.ProxyHandler(proxies))
urllib.request.install_opener(opener)
    
def get_token_decimal(token_id):
    """
    通过CoinGecko API获取代币实时价格（USD）
    """
    # CoinGecko API（无需 API Key）
    url = f"https://api.coingecko.com/api/v3/coins/{token_id}"
    response = requests.get(url).json()
    if response == {'error': 'coin not found'}:
        print("⚠️  精度获取失败，设置为默认值18")
        return 18
    elif "detail_platforms" in response:
        decimals = response["detail_platforms"]["ethereum"]["decimal_place"]
        return decimals
    else:
        print("⚠️  精度获取失败，设置为默认值18")
        return 18

def remove_duplicates(transactions):
    seen = set()
    return [d for d in transactions if d["tx_hash"] not in seen and not seen.add(d["tx_hash"])]

def get_recent_token_transactions(token_contract_address, token_symbol, token_decimals, token_price, days, min_amount_usd=100000):
    """
    获取指定代币近24小时的交易记录，并筛选大额交易
    """
    # 计算时间范围
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)
    print(start_time, end_time)

    # Etherscan API请求
    url = (
        f"https://api.etherscan.io/api"
        f"?module=account"
        f"&action=tokentx"
        f"&contractaddress={token_contract_address}"
        f"&startblock=22050000"
        f"&endblock=99999999"
        f"&sort=desc"
        f"&apikey={ETHERSCAN_API_KEY}"
    )

    # 发送请求
    print(f"正在获取 {token_symbol} 近期的交易列表...")
    while True:
        response = requests.get(url)
        data = response.json()

        if data["status"] == "1":
            transactions = data["result"]
            break
        else:
            print("交易获取失败，正在尝试重新获取...")
    
    # 筛选近24小时的交易
    recent_transactions = []
    for tx in transactions:
        tx_time = datetime.fromtimestamp(int(tx["timeStamp"]))
        if start_time <= tx_time <= end_time:
            recent_transactions.append(tx)

    # 筛选大额交易
    large_transactions = []
    for tx in recent_transactions:
        # 计算实际代币数量（考虑精度）
        value = int(tx["value"])
        time = pow(10, token_decimals)
        amount_token =  value / time
        amount_usd = amount_token * token_price
        
        if amount_usd >= min_amount_usd:
            large_transactions.append({
                "tx_hash": tx["hash"],
                "amount_usd": amount_usd,
                "time": datetime.fromtimestamp(int(tx["timeStamp"])).strftime("%Y-%m-%d %H:%M:%S"),
            })
        
    large_transactions = remove_duplicates(large_transactions)
    if len(large_transactions) >= 5:
        return sorted(large_transactions, key=lambda x: x["amount_usd"], reverse=True)[:5]
    else:
        return large_transactions

def get_transaction_action(tx_hash):
    url = "https://etherscan.io/tx/" + tx_hash
    request = urllib.request.Request(url, headers=head, method="GET") #封装访问信息
    while True:
        try:
            response = urllib.request.urlopen(request, timeout=10)
            break
        except urllib.error.URLError as e:
            pass
    # response = urllib.request.urlopen(request, timeout=10)
    html = response.read().decode("utf-8")

    soup = BeautifulSoup(html, 'html.parser')
    transaction_action_div = soup.find('div', {'id': 'wrapperContent'})

    if transaction_action_div:
        # 提取文本内容并清理空白
        transaction_action_text = ' '.join(transaction_action_div.stripped_strings)
        return transaction_action_text
    else:
        return None

def get_big_tranasaction(coin_info):
    print(f"📖 正在获取{coin_info['id']}的链上交易数据...")
    if "ethereum" in coin_info["chains"]:
        token_contract_address = coin_info["chains"]["ethereum"]
    else: return
    token_id = coin_info["id"]
    token_decimals = get_token_decimal(token_id)
    token_price = coin_info["price"]

    large_txs = get_recent_token_transactions(token_contract_address, token_id, token_decimals, token_price, days=1, min_amount_usd=100000)
    print(f"发现 {len(large_txs)} 笔异常的大额交易")
    json_data = []
    for tx in large_txs:
        tx_hash = tx["tx_hash"]
        tx_action = get_transaction_action(tx_hash)
        if tx_action:
            json_data.append({
            "time": tx["time"],
            "amount_usd": tx["amount_usd"],
            "transaction_action": tx_action
        })
    if json_data:
        return json_data
    return None